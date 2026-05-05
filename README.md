# 🚗 Used Vehicle Price Prediction System
### Final Year Capstone Project | Machine Learning | 2026

---

## 📌 Project Overview

An end-to-end Machine Learning system that predicts the **resale price of used vehicles** in India based on key features like vehicle age, mileage, fuel type, and engine specs.  
Built on **17,448 real car listings** across multiple Indian cities.

---

## 🏗️ Project Structure

```
capstone/
├── data/
│   └── car_resale_prices.csv      # Raw dataset
├── models/
│   ├── best_model.pkl             # Trained best model
│   ├── model_columns.pkl          # Feature column names
│   ├── model_metrics.json         # All model metrics
│   └── best_model_name.txt        # Name of best model
├── charts/
│   ├── price_vs_year.png
│   ├── price_vs_kms.png
│   ├── price_by_fuel.png
│   ├── price_by_transmission.png
│   ├── correlation_heatmap.png
│   └── feature_importance.png
├── preprocess.py                  # Data cleaning pipeline
├── train.py                       # Model training & evaluation
├── app.py                         # Streamlit web application
├── requirements.txt               # Python dependencies
└── README.md
```

---

## ⚙️ Setup & Installation

### Step 1 – Clone / Navigate to project
```bash
cd /Users/devnarayan/Desktop/capstone
```

### Step 2 – Create virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### Step 3 – Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 – Train the model
```bash
python train.py
```
This will:
- Clean & preprocess the dataset
- Train Linear Regression, Random Forest, XGBoost
- Auto-select the best model by R² score
- Save model to `models/best_model.pkl`
- Generate EDA charts in `charts/`

### Step 5 – Launch the web app
```bash
streamlit run app.py
```
Opens at: **http://localhost:8501**

---

## 🤖 Models Trained

| Model | Description |
|-------|-------------|
| Linear Regression | Baseline model with feature scaling |
| Random Forest | 200 trees, max depth 20 |
| XGBoost | 300 estimators, lr=0.05, max depth 7 |

**Best model is automatically selected** based on highest R² on the test set.

---

## 📊 Features Used

| Feature | Description |
|---------|-------------|
| `registered_year` | Year of registration |
| `kms_driven` | Total kilometers driven |
| `fuel_type` | Petrol / Diesel / CNG / Electric / LPG |
| `transmission_type` | Manual / Automatic |
| `owner_type` | 1st / 2nd / 3rd owner etc. |
| `body_type` | Hatchback / Sedan / SUV / MUV etc. |
| `city` | City of sale |
| `mileage` | Fuel efficiency (kmpl) |
| `engine_capacity` | Engine CC |
| `max_power` | BHP |
| `seats` | Number of seats |
| `vehicle_age` | Derived: 2026 − registered_year |

---

## 🌐 Web App Pages

| Page | Description |
|------|-------------|
| 🏠 Home | Overview, dataset stats, price distribution |
| 🔮 Predict Price | Input form → instant price prediction + download report |
| 📊 EDA Dashboard | Interactive charts: price vs year, kms, fuel, transmission, heatmap |
| 📈 Model Performance | Model comparison table, R²/RMSE bar charts, feature importance |

---

## 📈 Evaluation Metrics

- **R² Score** – How well model explains variance (higher = better)
- **RMSE** – Root Mean Squared Error in ₹ Lakh (lower = better)  
- **MAE** – Mean Absolute Error in ₹ Lakh (lower = better)
- **CV R²** – 5-fold Cross Validation R² (robustness check)

---

## 🚀 Deployment

### Streamlit Cloud (Free)
1. Push project to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `app.py` as main file
4. Deploy ✅

### Local Network Demo
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

---

## 💡 Presentation Tips (Viva)

1. **Explain the problem** – Why predicting used car prices matters in India
2. **Show data cleaning** – The messy formats (₹ symbols, "Lakh/Crore", "bhp/PS") you handled
3. **Show EDA charts** – Highlight that newer cars and automatics fetch higher prices
4. **Model comparison** – Explain why Random Forest/XGBoost beats Linear Regression on this data
5. **Live prediction demo** – Enter a real car (e.g. 2019 Maruti Swift, 50k km, Petrol, Manual)
6. **Feature importance** – registered_year, kms_driven, max_power are top predictors

---

## 👨‍💻 Tech Stack

`Python 3.10+` · `Pandas` · `NumPy` · `Scikit-learn` · `XGBoost` · `Streamlit` · `Plotly` · `Matplotlib` · `Seaborn`

---

*Capstone Project – Used Vehicle Price Prediction System | 2026*
