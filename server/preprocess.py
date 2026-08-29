"""
preprocess.py
=============
Data Cleaning & Preprocessing Pipeline for Used Vehicle Price Prediction System.
Run standalone to inspect cleaned data, or import clean_data() in train.py / app.py.
"""

import re
import numpy as np
import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# 1. RAW LOADERS
# ─────────────────────────────────────────────────────────────────────────────

DATA_PATH = Path(__file__).parent / "data" / "car_resale_prices.csv"


def load_raw(path: str = None) -> pd.DataFrame:
    """Load the raw CSV and return a DataFrame."""
    path = path or DATA_PATH
    df = pd.read_csv(path, index_col=0)
    print(f"[INFO] Loaded {len(df):,} rows × {df.shape[1]} columns")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. COLUMN-LEVEL CLEANING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def parse_resale_price(series: pd.Series) -> pd.Series:
    """
    Convert price strings like:
      "₹ 5.45 Lakh"  →  5.45
      "₹ 50,000"     →  0.50
      "₹ 1.04 Crore" →  104.0
    Returns price in Lakhs (float).
    """
    def _parse(val):
        if pd.isna(val):
            return np.nan
        val = str(val).replace("₹", "").replace(",", "").strip()
        # Crore
        m = re.search(r"([\d.]+)\s*crore", val, re.IGNORECASE)
        if m:
            return float(m.group(1)) * 100
        # Lakh
        m = re.search(r"([\d.]+)\s*lakh", val, re.IGNORECASE)
        if m:
            return float(m.group(1))
        # Plain number (assumed rupees → convert to lakhs)
        m = re.search(r"[\d.]+", val)
        if m:
            rupees = float(m.group())
            if rupees > 1_000:          # raw rupees
                return rupees / 1_00_000
            return rupees               # already in lakhs
        return np.nan

    return series.apply(_parse)


def parse_registered_year(series: pd.Series) -> pd.Series:
    """
    Handle:
      2017        → 2017
      "Jul 2021"  → 2021
      "Mar 2016"  → 2016
    Returns integer year.
    """
    def _parse(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip()
        # plain 4-digit year
        if re.fullmatch(r"\d{4}", val):
            return int(val)
        # "Mon YYYY"
        m = re.search(r"(\d{4})", val)
        if m:
            return int(m.group(1))
        return np.nan

    return series.apply(_parse).astype("float")


def parse_engine_capacity(series: pd.Series) -> pd.Series:
    """'1197 cc' → 1197.0"""
    return series.astype(str).str.extract(r"([\d.]+)")[0].astype("float")


def parse_kms_driven(series: pd.Series) -> pd.Series:
    """'40,000 Kms' → 40000.0"""
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"([\d.]+)")[0]
        .astype("float")
    )


def parse_max_power(series: pd.Series) -> pd.Series:
    """
    Extract numeric bhp from messy strings.
    Handles: "83.1bhp", "170PS", "90 PS", "300kWbhp", "118PS at 6,600 rpm",
             "120bhp (86.7kw)", "80 PS at 5200 rpm", "63PS at 5,400 rpm".
    kW values are converted: 1 kW ≈ 1.341 hp ≈ 1.360 PS/bhp (close enough).
    """
    def _parse(val):
        if pd.isna(val) or str(val).strip() == "":
            return np.nan
        val = str(val).strip()

        # kW (only kW, not "kw" embedded in "120bhp (86.7kw)")
        m = re.match(r"([\d.]+)\s*kW\b", val, re.IGNORECASE)
        if m and "bhp" not in val.lower() and "ps" not in val.lower():
            return round(float(m.group(1)) * 1.341, 2)

        # First number before bhp / PS / hp
        m = re.search(r"([\d.]+)\s*(?:bhp|ps|hp)", val, re.IGNORECASE)
        if m:
            return float(m.group(1))

        # fallback: first standalone number
        m = re.search(r"^([\d.]+)", val)
        if m:
            return float(m.group(1))

        return np.nan

    return series.apply(_parse)


def parse_mileage(series: pd.Series) -> pd.Series:
    """'21.4 kmpl' / '21.94 km/kg' / '30.48 km/kg' → numeric float."""
    return series.astype(str).str.extract(r"([\d.]+)")[0].astype("float")


# ─────────────────────────────────────────────────────────────────────────────
# 3. MAIN CLEANING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

# Columns we keep for modelling
FEATURE_COLS = [
    "registered_year",
    "kms_driven",
    "fuel_type",
    "transmission_type",
    "owner_type",
    "body_type",
    "city",
    "mileage",
    "engine_capacity",
    "max_power",
    "seats",
]
TARGET_COL = "resale_price"

# Categorical columns that need label / ordinal encoding
CAT_COLS = ["fuel_type", "transmission_type", "owner_type", "body_type", "city"]

OWNER_ORDER = {
    "First Owner": 1,
    "Second Owner": 2,
    "Third Owner": 3,
    "Fourth Owner": 4,
    "Fifth Owner": 5,
    "6th Owner": 6,
    "UnRegistered Car": 0,
    "Test Drive Car": 0,
}


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full cleaning pipeline:
      1. Parse all messy columns to numerics.
      2. Drop duplicates.
      3. Drop rows with missing target.
      4. Impute missing features.
      5. Ordinal-encode owner_type.
      6. One-hot encode remaining categorical columns.
    Returns a clean DataFrame ready for modelling.
    """
    df = df.copy()

    # ── 3.1  Parse / Convert ─────────────────────────────────────────────────
    df[TARGET_COL]          = parse_resale_price(df[TARGET_COL])
    df["registered_year"]   = parse_registered_year(df["registered_year"])
    df["engine_capacity"]   = parse_engine_capacity(df["engine_capacity"])
    df["kms_driven"]        = parse_kms_driven(df["kms_driven"])
    df["max_power"]         = parse_max_power(df["max_power"])
    df["mileage"]           = parse_mileage(df["mileage"])

    # seats might have ".0" suffix – keep as float
    df["seats"] = pd.to_numeric(df["seats"], errors="coerce")

    # ── 3.2  Filter: keep only useful rows ───────────────────────────────────
    df = df[FEATURE_COLS + [TARGET_COL]].copy()

    # Drop rows where target is missing or zero
    df = df[df[TARGET_COL].notna() & (df[TARGET_COL] > 0)]

    # Drop exact duplicates
    df = df.drop_duplicates()

    # ── 3.3  Remove extreme price outliers (> 3 IQR rule) ───────────────────
    Q1  = df[TARGET_COL].quantile(0.01)
    Q99 = df[TARGET_COL].quantile(0.99)
    df  = df[(df[TARGET_COL] >= Q1) & (df[TARGET_COL] <= Q99)]

    # ── 3.4  Impute missing numerics with median ──────────────────────────────
    num_cols = ["mileage", "engine_capacity", "max_power", "kms_driven", "seats", "registered_year"]
    for col in num_cols:
        df[col].fillna(df[col].median(), inplace=True)

    # ── 3.5  Impute missing categoricals with mode ────────────────────────────
    for col in CAT_COLS:
        df[col] = df[col].fillna(df[col].mode()[0])

    # ── 3.6  Standardise strings ──────────────────────────────────────────────
    for col in CAT_COLS:
        df[col] = df[col].astype(str).str.strip()

    # ── 3.7  Encode owner_type as ordinal ─────────────────────────────────────
    df["owner_type"] = df["owner_type"].map(OWNER_ORDER).fillna(2)

    # ── 3.8  One-hot encode remaining categoricals ────────────────────────────
    remaining_cats = [c for c in CAT_COLS if c != "owner_type"]
    df = pd.get_dummies(df, columns=remaining_cats, drop_first=True)

    # ── 3.9  Vehicle age feature ──────────────────────────────────────────────
    current_year = 2026
    df["vehicle_age"] = current_year - df["registered_year"]

    print(f"[INFO] After cleaning: {len(df):,} rows × {df.shape[1]} columns")
    return df.reset_index(drop=True)


def get_feature_target(df_clean: pd.DataFrame):
    """Split cleaned DataFrame into X (features) and y (target)."""
    y = df_clean[TARGET_COL]
    X = df_clean.drop(columns=[TARGET_COL])
    return X, y


# ─────────────────────────────────────────────────────────────────────────────
# 4. STANDALONE QUICK-CHECK
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    raw = load_raw()
    cleaned = clean_data(raw)
    X, y = get_feature_target(cleaned)
    print("\n── Feature columns ──────────────────────────────────────────────")
    print(X.columns.tolist())
    print("\n── Target stats ─────────────────────────────────────────────────")
    print(y.describe())
    print("\n── Sample (first 3 rows) ────────────────────────────────────────")
    print(cleaned.head(3).to_string())
