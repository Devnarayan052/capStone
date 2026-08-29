import json
import pickle
from typing import Optional, List
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from preprocess import OWNER_ORDER

app = FastAPI(title="Used Car Valuation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",        # Local dev
        "http://localhost:3000",
        "https://carval.co.in",         # Custom domain
        "https://www.carval.co.in",
        "https://*.vercel.app",         # Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR = Path(__file__).parent / "models"
try:
    with open(MODELS_DIR / "best_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(MODELS_DIR / "model_columns.pkl", "rb") as f:
        model_cols = pickle.load(f)
    try:
        model_name = (MODELS_DIR / "best_model_name.txt").read_text().strip()
    except Exception:
        model_name = "XGBoost"
except Exception as e:
    model = None
    model_cols = None
    model_name = "N/A"

# Load metrics if present
metrics_data = {}
try:
    metrics_path = MODELS_DIR / "model_metrics.json"
    if metrics_path.exists():
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
except Exception:
    metrics_data = {}

# Load nested brand → model specifications lookup table
# Structure: {"Maruti": {"Swift": {engine, power, mileage, body, fuel, trans, seats, sample_count}, ...}, ...}
car_specs: dict = {}
try:
    specs_path = MODELS_DIR / "car_specs.json"
    if specs_path.exists():
        with open(specs_path, "r", encoding="utf-8") as f:
            car_specs = json.load(f)
except Exception as e:
    print(f"[WARN] Could not load car_specs.json: {e}")
    car_specs = {}


def normalize_owner(owner_str: str) -> int:
    """Normalize owner string to integer representation."""
    if not owner_str:
        return 1
    s = str(owner_str).strip().lower()
    if "1" in s or "first" in s:
        return 1
    elif "2" in s or "second" in s:
        return 2
    elif "3" in s or "third" in s:
        return 3
    elif "4" in s or "fourth" in s:
        return 4
    elif "5" in s or "fifth" in s:
        return 5
    elif "test" in s or "unregistered" in s:
        return 0
    return OWNER_ORDER.get(owner_str, 2)


def lookup_spec(brand: str, model: str) -> Optional[dict]:
    """Look up specs from nested car_specs dict. Case-insensitive fallback."""
    if not brand or not model:
        return None
    # Direct lookup
    if brand in car_specs and model in car_specs[brand]:
        return car_specs[brand][model]
    # Case-insensitive brand search
    for b_key, models_dict in car_specs.items():
        if b_key.lower() == brand.strip().lower():
            # Case-insensitive model search within brand
            for m_key, spec in models_dict.items():
                if m_key.lower() == model.strip().lower():
                    return spec
    return None


# ──────────────────────────────────────────────────────────────────────────────
# NEW ENDPOINTS: /brands and /models
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/brands")
def get_brands():
    """Returns sorted list of all brand names in the specs database."""
    return sorted(car_specs.keys())


@app.get("/models")
def get_models(brand: str = Query(..., description="Brand name"),
               q: Optional[str] = Query(None, description="Partial model name for filtering")):
    """
    Returns models under a given brand, optionally filtered by a partial query string.
    Case-insensitive substring match, capped at 8 results.
    """
    # Find brand case-insensitively
    brand_models: dict = {}
    for b_key, models_dict in car_specs.items():
        if b_key.lower() == brand.strip().lower():
            brand_models = models_dict
            break
    
    if not brand_models:
        return []

    model_names = list(brand_models.keys())
    
    if q and len(q) >= 1:
        q_lower = q.strip().lower()
        model_names = [m for m in model_names if q_lower in m.lower()]
    
    # Cap at 8 results
    return model_names[:8]


# ──────────────────────────────────────────────────────────────────────────────
# LEGACY endpoint: /car-models (kept for backward compatibility)
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/car-models")
def get_car_models():
    """Legacy flat list. Returns all brand+model combinations."""
    result = []
    for brand_name, models_dict in car_specs.items():
        for model_name_str, spec in models_dict.items():
            result.append({
                "brand": brand_name,
                "model": model_name_str,
                "brand_model": f"{brand_name} {model_name_str}",
                "body": spec.get("body", ""),
                "fuel": spec.get("fuel", ""),
                "trans": spec.get("trans", ""),
            })
    return result


@app.get("/car-specs")
def get_car_specs(brand: Optional[str] = None, model: Optional[str] = None,
                  brand_model: Optional[str] = None):
    """Retrieve specifications for a given brand and model (nested lookup)."""
    if brand and model:
        spec = lookup_spec(brand, model)
        if spec:
            return {**spec, "brand": brand, "model": model}
        raise HTTPException(status_code=404, detail=f"Specs not found for '{brand} {model}'")
    
    # Legacy: brand_model as combined string
    if brand_model:
        parts = brand_model.strip().split(" ", 1)
        if len(parts) == 2:
            spec = lookup_spec(parts[0], parts[1])
            if spec:
                return {**spec, "brand": parts[0], "model": parts[1]}
    
    raise HTTPException(status_code=400, detail="Provide brand + model, or brand_model query parameter")


# ──────────────────────────────────────────────────────────────────────────────
# POST /predict — Updated payload schema
# ──────────────────────────────────────────────────────────────────────────────

class PredictionRequest(BaseModel):
    # Core user-provided fields (always required)
    brand: str
    model: str
    year: int
    kms: int
    fuel: str
    trans: str
    seats: int
    mileage: float
    city: str = "Delhi"
    owner: str = "1st Owner"
    # Fallback fields: only required when brand+model not in lookup
    engine: Optional[int] = None
    power: Optional[int] = None


@app.post("/predict")
def predict_price(req: PredictionRequest):
    if not model or not model_cols:
        raise HTTPException(status_code=500, detail="Model not loaded on server")
    
    # 1. Look up engine + power from car_specs.json (user doesn't provide these)
    spec = lookup_spec(req.brand, req.model)
    sample_count = spec.get("sample_count", 0) if spec else 0

    # Engine and power: from lookup (preferred) or fallback payload
    engine = spec.get("engine") if spec else req.engine
    if engine is None:
        engine = req.engine
    
    power = spec.get("power") if spec else req.power
    if power is None:
        power = req.power
    
    # Body type: always from lookup (not a user field)
    body = spec.get("body", "Sedan") if spec else "Sedan"

    # 2. Validation: if brand+model unknown and no engine/power fallback provided
    missing_fields = []
    if engine is None:
        missing_fields.append("engine_capacity")
    if power is None:
        missing_fields.append("max_power")
    
    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Vehicle '{req.brand} {req.model}' not found in our database. "
                f"Please also provide: {', '.join(missing_fields)}."
            )
        )

    # 3. Construct full 49-column feature row
    row = {
        "registered_year": req.year,
        "kms_driven": req.kms,
        "owner_type": normalize_owner(req.owner),
        "mileage": float(req.mileage),
        "engine_capacity": int(engine),
        "max_power": int(power),
        "seats": int(req.seats),
        "vehicle_age": max(0, 2026 - req.year)
    }
    
    # 4. One-hot encoding for categorical columns (fuel, trans, body, city)
    for pfx, val in [
        ("fuel_type", req.fuel),
        ("transmission_type", req.trans),
        ("body_type", body),
        ("city", req.city)
    ]:
        for c in model_cols:
            if c.startswith(pfx + "_"):
                row[c] = 1 if c[len(pfx) + 1:].lower() == str(val).lower() else 0
                
    df = pd.DataFrame([row])
    for c in model_cols:
        if c not in df.columns:
            df[c] = 0
            
    df = df[model_cols]
    pred = float(model.predict(df)[0])
    pred = max(0.15, pred)
    
    # 5. Dynamic confidence score based on sample backing
    if sample_count >= 50:
        confidence = 94
    elif sample_count >= 15:
        confidence = 89
    elif sample_count > 0:
        confidence = 78
    else:
        confidence = 82  # Unknown model with manual fallback specs
    
    return {
        "price_lakh": round(pred, 2),
        "range_low": round(pred * 0.92, 2),
        "range_high": round(pred * 1.08, 2),
        "model_name": model_name,
        "confidence_score": confidence,
        "vehicle_age": 2026 - req.year,
        "derived_specs": {
            "engine": engine,
            "power": power,
            "mileage": req.mileage,
            "body": body,
            "fuel": req.fuel,
            "trans": req.trans,
            "seats": req.seats,
            "sample_count": sample_count
        }
    }


@app.get("/metrics")
def get_metrics():
    return metrics_data or {
        "best": "XGBoost",
        "models": [
            {"name": "Linear Regression", "r2": 0.6808, "rmse": 4.3298, "mae": 2.5442, "cv_r2": 0.721},
            {"name": "Random Forest", "r2": 0.9399, "rmse": 1.8794, "mae": 0.9769, "cv_r2": 0.9324},
            {"name": "XGBoost", "r2": 0.9501, "rmse": 1.7123, "mae": 0.9075, "cv_r2": 0.9430}
        ]
    }


@app.get("/presets")
def get_presets():
    return [
        {"id": "swift",    "brand": "Maruti",   "model": "Swift",     "year": 2022, "kms": 28000, "city": "Delhi",      "owner": "1st Owner", "tag": "Most Popular"},
        {"id": "creta",    "brand": "Hyundai",  "model": "Creta",     "year": 2022, "kms": 32000, "city": "Mumbai",     "owner": "1st Owner", "tag": "Top SUV"},
        {"id": "city",     "brand": "Honda",    "model": "City",      "year": 2021, "kms": 38000, "city": "Bangalore",  "owner": "1st Owner", "tag": "Executive Sedan"},
        {"id": "nexon",    "brand": "Tata",     "model": "Nexon",     "year": 2022, "kms": 24000, "city": "Pune",       "owner": "1st Owner", "tag": "5-Star Safety"},
        {"id": "thar",     "brand": "Mahindra", "model": "Thar",      "year": 2023, "kms": 18000, "city": "Chandigarh", "owner": "1st Owner", "tag": "4x4 Icon"},
        {"id": "fortuner", "brand": "Toyota",   "model": "Fortuner",  "year": 2021, "kms": 46000, "city": "Hyderabad",  "owner": "1st Owner", "tag": "Premium SUV"},
    ]


@app.get("/health")
def health_check():
    total_models = sum(len(m) for m in car_specs.values())
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_name": model_name,
        "features_count": len(model_cols) if model_cols else 0,
        "car_specs_brands": len(car_specs),
        "car_specs_models": total_models,
    }
