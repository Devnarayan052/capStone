import pickle
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from preprocess import OWNER_ORDER

app = FastAPI(title="Car Valuation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for the Vercel frontend
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

class PredictionRequest(BaseModel):
    year: int
    kms: int
    owner: str
    mileage: float
    engine: int
    power: int
    seats: int
    fuel: str
    trans: str
    body: str
    city: str

@app.post("/predict")
def predict_price(req: PredictionRequest):
    if not model:
        return {"error": "Model not loaded"}
    
    inp = req.dict()
    row = {
        "registered_year": inp["year"],
        "kms_driven": inp["kms"],
        "owner_type": OWNER_ORDER.get(inp["owner"], 2),
        "mileage": inp["mileage"],
        "engine_capacity": inp["engine"],
        "max_power": inp["power"],
        "seats": inp["seats"],
        "vehicle_age": 2026 - inp["year"]
    }
    
    for pfx, val in [("fuel_type", inp["fuel"]), ("transmission_type", inp["trans"]),
                    ("body_type", inp["body"]), ("city", inp["city"])]:
        for c in model_cols:
            if c.startswith(pfx + "_"):
                row[c] = 1 if c[len(pfx) + 1:] == val else 0
                
    df = pd.DataFrame([row])
    for c in model_cols:
        if c not in df.columns:
            df[c] = 0
            
    df = df[model_cols]
    pred = float(model.predict(df)[0])
    pred = max(0.1, pred)
    return {
        "price_lakh": pred,
        "range_low": pred * 0.91,
        "range_high": pred * 1.09,
        "model_name": model_name
    }
    
@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": model is not None}
