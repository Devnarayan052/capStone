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
├── client/                      # React + Vite Frontend
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   └── ...
│   └── ...
├── server/                      # Python Backend & ML Pipeline
│   ├── main.py                  # FastAPI server
│   ├── app.py                   # Streamlit dashboard
│   ├── preprocess.py            # Preprocessing script
│   ├── train.py                 # Training script
│   ├── requirements.txt         # Backend dependencies
│   ├── data/                    # Dataset directory
│   │   └── car_resale_prices.csv
│   ├── models/                  # Saved models & metrics
│   │   ├── best_model.pkl
│   │   └── ...
│   └── charts/                  # Generated EDA charts
│       ├── correlation_heatmap.png
│       └── ...
├── docs/                        # Project documentation / personal files
│   └── Dev_Narayan_Cover_Letter.pdf   # Cover Letter / Application
├── .gitignore                   # Global gitignore configuration
└── README.md                    # Main project overview
```

---

## ⚙️ Setup & Installation

### Option A: Running the Python Streamlit Dashboard (Standalone)

#### Step 1 – Navigate to server directory
```bash
cd /Users/devnarayan/Desktop/capstone/server
```

#### Step 2 – Create virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

#### Step 3 – Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 4 – Train the model
```bash
python train.py
```
This will:
- Clean & preprocess the dataset
- Train Linear Regression, Random Forest, XGBoost
- Auto-select the best model by R² score
- Save model to `models/best_model.pkl`
- Generate EDA charts in `charts/`

#### Step 5 – Launch the Streamlit dashboard
```bash
streamlit run app.py
```
Opens at: **http://localhost:8501**

### Option B: Running the Client-Server Web Application (FastAPI + React)

#### 1. Start the FastAPI Backend
```bash
cd /Users/devnarayan/Desktop/capstone/server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Opens at: **http://localhost:8000**

#### 2. Start the React Frontend
```bash
cd /Users/devnarayan/Desktop/capstone/client
npm install
npm run dev
```
Opens at: **http://localhost:5173** (or the port specified in terminal)

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

`Python 3.10+` · `Pandas` · `NumPy` · `Scikit-learn` · `XGBoost` · `Streamlit` · `Plotly` · `Matplotlib` · `Seaborn`

---

*Capstone Project – Used Vehicle Price Prediction System | 2026*
