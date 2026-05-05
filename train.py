"""
train.py
========
Model Training Pipeline for Used Vehicle Price Prediction System.

Usage:
    python train.py

Outputs:
    models/best_model.pkl        – Best trained model
    models/model_columns.pkl     – Feature column names (for inference alignment)
    models/model_metrics.json    – All model metrics
"""

import json
import pickle
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[WARN] XGBoost not installed – skipping XGBRegressor.")

from preprocess import load_raw, clean_data, get_feature_target, parse_resale_price

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).parent
MODELS_DIR = ROOT / "models"
CHARTS_DIR = ROOT / "charts"
MODELS_DIR.mkdir(exist_ok=True)
CHARTS_DIR.mkdir(exist_ok=True)


# ──────────────────────────────────────────────────────────────────────────
# 1.  LOAD & PREPARE DATA
# ──────────────────────────────────────────────────────────────────────────

def prepare_data():
    raw     = load_raw()
    cleaned = clean_data(raw)
    X, y    = get_feature_target(cleaned)
    return X, y, cleaned


# ──────────────────────────────────────────────────────────────────────────
# 2.  EVALUATE MODEL
# ──────────────────────────────────────────────────────────────────────────

def evaluate(name, model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2   = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae  = mean_absolute_error(y_test, y_pred)

    # 5-fold CV R²
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="r2")

    print(f"\n{'─'*50}")
    print(f"  Model      : {name}")
    print(f"  R² Score   : {r2:.4f}")
    print(f"  RMSE       : ₹{rmse:.2f} Lakh")
    print(f"  MAE        : ₹{mae:.2f} Lakh")
    print(f"  CV R² (5F) : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"{'─'*50}")

    return {
        "name":     name,
        "model":    model,
        "r2":       round(r2, 4),
        "rmse":     round(rmse, 4),
        "mae":      round(mae, 4),
        "cv_r2":    round(cv_scores.mean(), 4),
        "cv_std":   round(cv_scores.std(), 4),
        "y_pred":   y_pred,
    }


# ──────────────────────────────────────────────────────────────────────────
# 3.  EXPLORATORY DATA ANALYSIS CHARTS
# ──────────────────────────────────────────────────────────────────────────

def generate_eda_charts(df: pd.DataFrame):
    """Generate and save EDA charts to charts/ directory."""
    palette = "viridis"

    # ── 3a. Price vs Year ──────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    yr_avg = df.groupby("registered_year")["resale_price"].median().reset_index()
    ax.plot(yr_avg["registered_year"], yr_avg["resale_price"], marker="o", linewidth=2, color="#6C63FF")
    ax.fill_between(yr_avg["registered_year"], yr_avg["resale_price"], alpha=0.15, color="#6C63FF")
    ax.set_title("Median Resale Price vs Registration Year", fontsize=14, fontweight="bold")
    ax.set_xlabel("Registration Year")
    ax.set_ylabel("Price (₹ Lakh)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(CHARTS_DIR / "price_vs_year.png", dpi=150)
    plt.close(fig)
    print("[INFO] Saved chart: price_vs_year.png")

    # ── 3b. Price vs KMs Driven ────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = df.sample(min(2000, len(df)), random_state=42)
    sc = ax.scatter(sample["kms_driven"], sample["resale_price"],
                    alpha=0.4, c=sample["resale_price"], cmap=palette, s=10)
    plt.colorbar(sc, label="Price (₹ Lakh)")
    ax.set_title("Resale Price vs KMs Driven", fontsize=14, fontweight="bold")
    ax.set_xlabel("KMs Driven")
    ax.set_ylabel("Price (₹ Lakh)")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(CHARTS_DIR / "price_vs_kms.png", dpi=150)
    plt.close(fig)
    print("[INFO] Saved chart: price_vs_kms.png")

    # ── 3c. Price by Fuel Type ─────────────────────────────────────────────
    _raw = load_raw()
    _raw["resale_price_clean"] = parse_resale_price(_raw["resale_price"])
    _raw = _raw.dropna(subset=["resale_price_clean", "fuel_type"])
    _raw = _raw[_raw["resale_price_clean"] > 0]
    fig, ax = plt.subplots(figsize=(10, 5))
    fuel_order = (
        _raw.groupby("fuel_type")["resale_price_clean"]
        .median().sort_values(ascending=False).index.tolist()
    )
    sns.boxplot(data=_raw, x="fuel_type", y="resale_price_clean",
                order=fuel_order, palette="viridis", ax=ax)
    ax.set_title("Resale Price by Fuel Type", fontsize=14, fontweight="bold")
    ax.set_xlabel("Fuel Type")
    ax.set_ylabel("Price (₹ Lakh)")
    ax.set_ylim(0, _raw["resale_price_clean"].quantile(0.97))
    plt.xticks(rotation=15)
    plt.tight_layout()
    fig.savefig(CHARTS_DIR / "price_by_fuel.png", dpi=150)
    plt.close(fig)
    print("[INFO] Saved chart: price_by_fuel.png")

    # ── 3d. Price by Transmission ──────────────────────────────────────────
    _raw2 = load_raw()
    _raw2["resale_price_clean"] = parse_resale_price(_raw2["resale_price"])
    _raw2 = _raw2.dropna(subset=["resale_price_clean", "transmission_type"])
    _raw2 = _raw2[_raw2["resale_price_clean"] > 0]
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ["#6C63FF", "#FF6584"]
    _raw2.groupby("transmission_type")["resale_price_clean"].median().plot(
        kind="bar", ax=ax, color=colors, edgecolor="black"
    )
    ax.set_title("Median Resale Price by Transmission", fontsize=14, fontweight="bold")
    ax.set_xlabel("Transmission Type")
    ax.set_ylabel("Median Price (₹ Lakh)")
    ax.tick_params(axis="x", rotation=0)
    plt.tight_layout()
    fig.savefig(CHARTS_DIR / "price_by_transmission.png", dpi=150)
    plt.close(fig)
    print("[INFO] Saved chart: price_by_transmission.png")

    # ── 3e. Correlation Heatmap ────────────────────────────────────────────
    num_only = df.select_dtypes(include=[np.number]).copy()
    # Keep top 12 correlated columns to keep it readable
    corr = num_only.corr()[["resale_price"]].abs().sort_values("resale_price", ascending=False)
    top_cols = corr.index[:12].tolist()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        num_only[top_cols].corr(),
        annot=True, fmt=".2f", cmap="coolwarm",
        ax=ax, linewidths=0.5, annot_kws={"size": 8}
    )
    ax.set_title("Correlation Heatmap (Top Features)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    fig.savefig(CHARTS_DIR / "correlation_heatmap.png", dpi=150)
    plt.close(fig)
    print("[INFO] Saved chart: correlation_heatmap.png")


# ──────────────────────────────────────────────────────────────────────────
# 4.  FEATURE IMPORTANCE CHART
# ──────────────────────────────────────────────────────────────────────────

def plot_feature_importance(model, feature_names):
    """Plot and save feature importance for tree-based models."""
    if not hasattr(model, "feature_importances_"):
        return
    importances = model.feature_importances_
    fi_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=True)
        .tail(15)
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(fi_df["feature"], fi_df["importance"], color="#6C63FF", edgecolor="white")
    ax.set_title("Feature Importance (Top 15)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Importance Score")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    fig.savefig(CHARTS_DIR / "feature_importance.png", dpi=150)
    plt.close(fig)
    print("[INFO] Saved chart: feature_importance.png")


# ──────────────────────────────────────────────────────────────────────────
# 5.  MAIN TRAINING LOOP
# ──────────────────────────────────────────────────────────────────────────

def train():
    print("\n" + "═"*60)
    print("  USED VEHICLE PRICE PREDICTION – TRAINING PIPELINE")
    print("═"*60)

    # Load
    X, y, cleaned = prepare_data()
    print(f"\n[INFO] Feature matrix: {X.shape}")
    print(f"[INFO] Target range  : ₹{y.min():.2f}L – ₹{y.max():.2f}L")

    # EDA charts
    print("\n[STEP] Generating EDA charts …")
    generate_eda_charts(cleaned)

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\n[INFO] Train size: {len(X_train):,}  |  Test size: {len(X_test):,}")

    # Scale (for Linear Regression)
    scaler  = StandardScaler()
    X_tr_sc = scaler.fit_transform(X_train)
    X_te_sc = scaler.transform(X_test)

    # ── Define models ────────────────────────────────────────────────────
    models_cfg = [
        ("Linear Regression",
         LinearRegression(),
         X_tr_sc, X_te_sc),

        ("Random Forest",
         RandomForestRegressor(
             n_estimators=200, max_depth=20,
             min_samples_leaf=2, n_jobs=-1, random_state=42
         ),
         X_train, X_test),
    ]

    if XGBOOST_AVAILABLE:
        models_cfg.append((
            "XGBoost",
            XGBRegressor(
                n_estimators=300, learning_rate=0.05, max_depth=7,
                subsample=0.8, colsample_bytree=0.8,
                random_state=42, verbosity=0
            ),
            X_train, X_test,
        ))

    # ── Train & Evaluate ─────────────────────────────────────────────────
    print("\n[STEP] Training & evaluating models …")
    results = []
    for name, model, Xtr, Xte in models_cfg:
        res = evaluate(name, model, Xtr, Xte, y_train, y_test)
        results.append(res)

    # ── Select best model (by R²) ─────────────────────────────────────────
    best = max(results, key=lambda r: r["r2"])
    print(f"\n✅ Best Model  : {best['name']}")
    print(f"   R²          : {best['r2']}")
    print(f"   RMSE        : ₹{best['rmse']} Lakh")
    print(f"   MAE         : ₹{best['mae']} Lakh")

    # ── Save best model ───────────────────────────────────────────────────
    with open(MODELS_DIR / "best_model.pkl", "wb") as f:
        pickle.dump(best["model"], f)
    print(f"\n[SAVED] models/best_model.pkl")

    # Save scaler only if best model is Linear Regression
    with open(MODELS_DIR / "scaler.pkl", "wb") as f:
        pickle.dump(scaler if best["name"] == "Linear Regression" else None, f)

    # Save column names for inference alignment
    with open(MODELS_DIR / "model_columns.pkl", "wb") as f:
        pickle.dump(X.columns.tolist(), f)
    print(f"[SAVED] models/model_columns.pkl")

    # Save best model name
    with open(MODELS_DIR / "best_model_name.txt", "w") as f:
        f.write(best["name"])

    # ── Save metrics JSON ─────────────────────────────────────────────────
    metrics = [
        {
            "name":   r["name"],
            "r2":     r["r2"],
            "rmse":   r["rmse"],
            "mae":    r["mae"],
            "cv_r2":  r["cv_r2"],
            "cv_std": r["cv_std"],
        }
        for r in results
    ]
    with open(MODELS_DIR / "model_metrics.json", "w") as f:
        json.dump({"best": best["name"], "models": metrics}, f, indent=2)
    print(f"[SAVED] models/model_metrics.json")

    # ── Feature importance chart ──────────────────────────────────────────
    plot_feature_importance(best["model"], X.columns.tolist())

    # ── Summary table ─────────────────────────────────────────────────────
    print("\n" + "═"*60)
    print("  MODEL COMPARISON SUMMARY")
    print("═"*60)
    summary = pd.DataFrame([
        {
            "Model": r["name"],
            "R²": r["r2"],
            "RMSE (₹L)": r["rmse"],
            "MAE (₹L)": r["mae"],
            "CV R²": r["cv_r2"],
        }
        for r in results
    ])
    print(summary.to_string(index=False))
    print("\n✅ Training complete!")
    return best


if __name__ == "__main__":
    train()
