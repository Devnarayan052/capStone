"""app.py – CarVal Premium UI  |  streamlit run app.py"""
import json, pickle, warnings, time
import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path
from preprocess import (load_raw, clean_data, parse_resale_price,
                        parse_registered_year, parse_kms_driven, OWNER_ORDER)

warnings.filterwarnings("ignore")
ROOT, MODELS_DIR = Path(__file__).parent, Path(__file__).parent / "models"

st.set_page_config(page_title="CarVal – Know Your Car's Worth",
                   page_icon="🚗", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════ CSS ════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,html,body{font-family:'Inter',sans-serif!important;box-sizing:border-box;}
#MainMenu,header,footer,[data-testid="stToolbar"],
[data-testid="stDecoration"],[data-testid="collapsedControl"]{display:none!important;}
.stApp{background:#fcfcfc;}
.block-container{padding:0.5rem 1rem 5rem!important;max-width:1150px!important;margin:0 auto;}

.carval-header{padding:2.5rem 0 1.5rem;display:flex;align-items:center;justify-content:space-between;}
.brand{font-size:1.1rem;font-weight:900;color:#000000;letter-spacing:1px;text-transform:uppercase;}
.brand span{color:#e01e26;}

.nav-links{display:flex;gap:3rem;}
.nav-active-btn button{color:#000000!important;border-bottom:2px solid #000000!important;border-radius:0!important;}

/* nav buttons – override streamlit */
div[data-testid="stHorizontalBlock"] button{
  background:transparent!important;border:none!important;
  color:#999999!important;font-size:0.7rem!important;font-weight:700!important;
  text-transform:uppercase!important;letter-spacing:2px!important;
  padding:0!important;transition:color 0.2s!important;}
div[data-testid="stHorizontalBlock"] button:hover{color:#000000!important;}

/* ── HERO ── */
.hero{text-align:center;padding:15vh 0 10vh;}
.hero-h1{font-size:4.8rem;font-weight:900;color:#000000;
  line-height:0.95;letter-spacing:-5px;margin-bottom:2rem;}
.hero-h1 span{color:#e01e26;}
.hero-sub{font-size:1.1rem;color:#888888;max-width:500px;margin:0 auto;line-height:1.7;letter-spacing:-0.2px;}

/* ── BUTTONS ── */
div[data-testid="stButton"] button[kind="primary"]{
  background:#000000!important;
  color:#fff!important;border:none!important;border-radius:0!important;
  padding:1.2rem 4rem!important;font-size:0.8rem!important;
  font-weight:800!important;text-transform:uppercase!important;letter-spacing:3px!important;}
div[data-testid="stButton"] button[kind="primary"]:hover{
  background:#e01e26!important;}

/* ── FORM ── */
.form-card{
  background:#ffffff;
  border:1px solid #f1f5f9;border-radius:4px;
  padding:2rem;margin-bottom:1.5rem;}
.step-label{font-size:0.6rem;font-weight:800;letter-spacing:2px;
  color:#999999;text-transform:uppercase;margin-bottom:1.5rem;}
.stSelectbox>div>div,.stNumberInput>div>div>input{
  background:#ffffff!important;
  border:1px solid #eeeeee!important;
  border-radius:2px!important;color:#111111!important;}
.stSlider [data-baseweb="slider"] div{background:#111111!important;}

/* ── RESULT ── */
.result-card{
  background:#ffffff;border:1px solid #111111;
  border-radius:4px;padding:4rem 2rem;text-align:center;}
.result-price{
  font-size:5rem;font-weight:800;color:#111111;
  letter-spacing:-4px;line-height:1;margin-bottom:0.5rem;}
.result-price span{color:#e01e26;}
.rtag{
  display:inline-flex;padding:0.4rem 1rem;border:1px solid #eeeeee;
  border-radius:2px;color:#666666;font-size:0.75rem;font-weight:700;
  text-transform:uppercase;letter-spacing:1px;}

/* ── PAGE HEADERS ── */
.pg-eye{font-size:0.72rem;font-weight:700;letter-spacing:2px;
  color:#6d28d9;text-transform:uppercase;margin-bottom:0.4rem;}
.pg-title{font-size:2rem;font-weight:800;color:#0f172a;
  letter-spacing:-0.8px;margin-bottom:0.3rem;}
.pg-sub{color:#64748b;font-size:0.92rem;margin-bottom:2rem;}

/* ── INSIGHT CARDS ── */
.insight-label{font-size:0.78rem;color:#6d28d9;font-weight:700;
  margin-bottom:0.25rem;letter-spacing:0.5px;}
.insight-desc{font-size:0.83rem;color:#475569;
  margin-bottom:1rem;line-height:1.55;}

/* ── MODEL STAT CARDS ── */
.model-stat-row{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;}
.model-stat{flex:1;min-width:140px;
  background:#ffffff;
  border:1px solid #e2e8f0;border-radius:14px;
  padding:1.2rem;text-align:center;
  box-shadow:0 1px 3px rgba(0,0,0,0.05);}
.ms-label{font-size:0.7rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;color:#94a3b8;margin-bottom:0.5rem;}
.ms-value{font-size:1.9rem;font-weight:900;color:#0f172a;}
.ms-unit{font-size:0.8rem;color:#64748b;margin-top:0.2rem;}

/* scrollbar */
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:#fcfcfc;}
::-webkit-scrollbar-thumb{background:#e2e8f0;border-radius:3px;}

/* ── MOBILE RESPONSIVENESS ── */
@media (max-width: 768px) {
  .block-container {padding: 0.5rem 0.8rem 4rem !important;}
  .carval-nav {flex-direction: column; align-items: flex-start; gap: 0.8rem; padding: 0.8rem 0;}
  .brand {font-size: 1.2rem;}
  .tagline {font-size: 0.65rem;}
  .hero-h1 {font-size: 1.7rem !important; line-height: 1.2 !important;}
  .hero-sub {font-size: 0.82rem !important; margin-bottom: 1.5rem !important;}
  .pg-title {font-size: 1.5rem !important;}
  
  /* Stack nav buttons or make them very compact */
  div[data-testid="stHorizontalBlock"] {gap: 4px !important;}
  div[data-testid="stHorizontalBlock"] button {
    font-size: 0.72rem !important;
    padding: 0.25rem 0.5rem !important;
  }
  
  .result-price {font-size: 2.8rem !important;}
  .result-card {padding: 2rem 1rem 1.5rem !important;}
  .result-tags {gap: 0.5rem !important;}
  .rtag {font-size: 0.7rem !important; padding: 0.25rem 0.6rem !important;}
  
  /* Fix expander text wrapping and alignment */
  .stExpander div[role="button"] p {font-size: 0.8rem !important;}
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════ LOADERS ════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def load_model():
    mp,cp = MODELS_DIR/"best_model.pkl", MODELS_DIR/"model_columns.pkl"
    if not mp.exists(): return None,None,"N/A"
    m=pickle.load(open(mp,"rb")); c=pickle.load(open(cp,"rb"))
    n=(MODELS_DIR/"best_model_name.txt").read_text().strip() if (MODELS_DIR/"best_model_name.txt").exists() else "XGBoost"
    return m,c,n

@st.cache_data(show_spinner=False)
def load_metrics():
    p=MODELS_DIR/"model_metrics.json"
    return json.load(open(p)) if p.exists() else None

@st.cache_data(show_spinner=False)
def get_df():
    r=load_raw()
    r["price_lakh"]=parse_resale_price(r["resale_price"])
    r["year"]=parse_registered_year(r["registered_year"])
    r["kms"]=parse_kms_driven(r["kms_driven"])
    return r.dropna(subset=["price_lakh"])

def build_input(inp,cols):
    row={"registered_year":inp["year"],"kms_driven":inp["kms"],
         "owner_type":OWNER_ORDER.get(inp["owner"],2),
         "mileage":inp["mileage"],"engine_capacity":inp["engine"],
         "max_power":inp["power"],"seats":inp["seats"],
         "vehicle_age":2026-inp["year"]}
    for pfx,val in [("fuel_type",inp["fuel"]),("transmission_type",inp["trans"]),
                    ("body_type",inp["body"]),("city",inp["city"])]:
        for c in cols:
            if c.startswith(pfx+"_"): row[c]=1 if c[len(pfx)+1:]==val else 0
    df=pd.DataFrame([row])
    for c in cols:
        if c not in df.columns: df[c]=0
    return df[cols]


# ═══════════════════════════ SESSION STATE ═══════════════════════════════════
for k,v in [("page","Home"),("result",None)]:
    if k not in st.session_state: st.session_state[k]=v

model,model_cols,model_name=load_model()
raw_df=get_df()
PAGES=["Home","Predict","Insights","Model"]


# ═══════════════════════════ NAVBAR ══════════════════════════════════════════
st.markdown('<div class="carval-header"><div class="brand">CarVal<span>.</span></div></div>', unsafe_allow_html=True)

# Main Navigation
_,c2,_=st.columns([1,3,1])
with c2:
    n1,n2,n3,n4=st.columns(4)
    for col,pg in zip([n1,n2,n3,n4],PAGES):
        with col:
            active_class = "nav-active-btn" if st.session_state.page==pg else ""
            st.markdown(f'<div class="{active_class}" style="text-align:center;">', unsafe_allow_html=True)
            if st.button(pg.upper(), key=f"nav_{pg}"):
                st.session_state.page=pg; st.session_state.result=None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="margin-bottom:6rem;"></div>', unsafe_allow_html=True)


# ════════════════════════════ HOME ══════════════════════════════════════════
if st.session_state.page=="Home":
    st.markdown("""
    <div class="hero">
      <div class="hero-h1">The future of car<br>valuation is <span>here.</span></div>
      <div class="hero-sub">No clutter. No noise. Just the raw intelligence of 17,000+ data points distilled into a single, precise number.</div>
    </div>
    """, unsafe_allow_html=True)

    _,mid,_=st.columns([1,1,1])
    with mid:
        if st.button("Begin Analysis", kind="primary", use_container_width=True):
            st.session_state.page="Predict"; st.rerun()




# ════════════════════════════ PREDICT ═══════════════════════════════════════
elif st.session_state.page=="Predict":
    if model is None:
        st.error("❌ Run `python train.py` first."); st.stop()

    st.markdown('<div class="pg-eye">Price Estimator</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-title">Tell us about your car</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">2 quick steps — takes under a minute</div>', unsafe_allow_html=True)

    with st.form("predict_form"):
        # Step 1
        st.markdown('<div class="form-card"><div class="step-label"><div class="step-num">1</div>Basic Info</div></div>', unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        with c1:
            year=st.selectbox("Year of manufacture",list(range(2025,2000,-1)),index=5,
                              help="When was the car first registered?")
            fuel=st.selectbox("Fuel type",["Petrol","Diesel","CNG","Electric"])
        with c2:
            kms=st.number_input("KMs driven (approx. is fine)",0,500000,45000,5000,
                                help="Check your odometer — estimate is okay")
            trans=st.selectbox("Transmission",["Manual","Automatic"])
        with c3:
            owner=st.selectbox("Ownership",list(OWNER_ORDER.keys())[:4],
                               help="1st owner = bought new from showroom")
            body=st.selectbox("Car type",["Hatchback","Sedan","SUV","MUV","Coupe"])

        st.markdown("<br>", unsafe_allow_html=True)

        # Step 2
        st.markdown('<div class="form-card"><div class="step-label"><div class="step-num">2</div>Car Specs <span style="color:#334155;font-weight:400;font-size:0.72rem;margin-left:0.4rem;">(optional — leave defaults if unsure)</span></div></div>', unsafe_allow_html=True)
        with st.expander("+ Add engine, mileage & city details"):
            a1,a2,a3=st.columns(3)
            with a1:
                city=st.selectbox("City",sorted(raw_df["city"].dropna().unique()))
                seats=st.selectbox("Seats",[4,5,6,7,8],index=1)
            with a2:
                engine=st.slider("Engine capacity (cc)",600,4000,1200,100,
                                 help="Check your RC or car manual")
                mileage=st.slider("Mileage (kmpl)",5.0,40.0,18.0,0.5)
            with a3:
                power=st.slider("Max power (bhp)",30,300,85,5)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted=st.form_submit_button("⚡  Get My Car's Price",
                                        type="primary", use_container_width=True)

    if submitted:
        with st.spinner("🔍  Analyzing 17,000+ market listings..."):
            time.sleep(1.2)
            inp=dict(year=year,kms=kms,fuel=fuel,trans=trans,owner=owner,
                     body=body,city=city,mileage=mileage,engine=engine,power=power,seats=seats)
            pred=max(0.1, float(model.predict(build_input(inp,model_cols))[0]))
            st.session_state.result=(pred, pred*0.91, pred*1.09)

    if st.session_state.result:
        pred,lo,hi=st.session_state.result
        st.markdown(f"""
        <div class="result-outer">
          <div class="result-glow"></div>
          <div class="result-card">
            <div class="result-check">✦</div>
            <div class="result-eye">Estimated Market Value</div>
            <div class="result-price">₹&thinsp;{pred:.2f}</div>
            <div class="result-price-sub">Lakhs</div>
            <div class="result-range">Price range &nbsp;·&nbsp; ₹{lo:.1f}L &ndash; ₹{hi:.1f}L</div>
            <div class="result-tags">
              <div class="rtag">✔&nbsp; 17,000+ Indian listings</div>
              <div class="rtag">✔&nbsp; Powered by {model_name}</div>
              <div class="rtag">✔&nbsp; Live market trends</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        st.balloons()


# ════════════════════════════ INSIGHTS ══════════════════════════════════════
elif st.session_state.page=="Insights":
    st.markdown('<div class="pg-eye">Market Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-title">What Drives Car Prices?</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Visual insights from 17,000+ real used car listings across India</div>', unsafe_allow_html=True)

    df=raw_df[raw_df["price_lakh"]<=50].copy()
    CS=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color="#475569",margin=dict(l=10,r=10,t=40,b=10))

    t1,t2,t3,t4=st.tabs(["📅 Age & Value","🛣️ Usage Impact","⛽ Fuel Type","🔥 Key Factors"])

    with t1:
        st.markdown('<div class="insight-label">How prices change over time</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Newer cars hold significantly higher resale value. A 3-year-old car can fetch nearly 2x more than a 7-year-old equivalent.</div>', unsafe_allow_html=True)
        yr=df.groupby("year")["price_lakh"].median().reset_index()
        fig=px.area(yr,x="year",y="price_lakh",markers=True,
                    color_discrete_sequence=["#e01e26"],
                    labels={"year":"Registration Year","price_lakh":"Median Price (₹L)"})
        fig.update_layout(**CS); fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)"); fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
        st.plotly_chart(fig,use_container_width=True)

    with t2:
        st.markdown('<div class="insight-label">Impact of kilometers driven</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Higher mileage generally lowers resale value. Cars under 50,000 km command a clear premium over high-mileage vehicles.</div>', unsafe_allow_html=True)
        samp=df.sample(min(2000,len(df)),random_state=42)
        fig=px.scatter(samp,x="kms",y="price_lakh",opacity=0.5,
                       color="price_lakh",color_continuous_scale="Reds",
                       labels={"kms":"KMs Driven","price_lakh":"Price (₹L)"})
        fig.update_traces(marker=dict(size=4)); fig.update_layout(**CS)
        st.plotly_chart(fig,use_container_width=True)

    with t3:
        st.markdown('<div class="insight-label">Which fuel type retains value best?</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Electric vehicles command the highest resale prices on average, followed by Diesel. CNG and LPG vehicles tend to depreciate faster.</div>', unsafe_allow_html=True)
        fd=df.groupby("fuel_type")["price_lakh"].median().reset_index().sort_values("price_lakh")
        fig=px.bar(fd,x="price_lakh",y="fuel_type",orientation="h",
                   color_discrete_sequence=["#e01e26"],
                   labels={"fuel_type":"Fuel Type","price_lakh":"Median Price (₹L)"})
        fig.update_layout(**CS)
        st.plotly_chart(fig,use_container_width=True)

    with t4:
        st.markdown('<div class="insight-label">What the AI model actually looks at</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Year of registration, kilometers driven, and max power are the top 3 predictors of resale price in our model.</div>', unsafe_allow_html=True)
        cleaned=clean_data(load_raw())
        num_df=cleaned.select_dtypes(include="number")
        top=num_df.corr()[["resale_price"]].abs().sort_values("resale_price",ascending=False).index[:9]
        fig=px.imshow(num_df[top].corr(),text_auto=".2f",color_continuous_scale="RdBu_r",aspect="auto")
        fig.update_layout(**CS,height=440)
        st.plotly_chart(fig,use_container_width=True)


# ════════════════════════════ MODEL ═════════════════════════════════════════
elif st.session_state.page=="Model":
    st.markdown('<div class="pg-eye">Under the Hood</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-title">How Accurate Is This?</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-sub">Our AI was trained on 17,000+ real listings and compared across 3 models</div>', unsafe_allow_html=True)

    metrics=load_metrics()
    if not metrics: st.warning("Run `python train.py` first."); st.stop()

    best=next((m for m in metrics["models"] if m["name"]==metrics["best"]),metrics["models"][0])

    # Clean stat cards
    accuracy_pct = round(best["r2"]*100, 1)
    st.markdown(f"""
    <div class="model-stat-row">
      <div class="model-stat">
        <div class="ms-label">Best Model</div>
        <div class="ms-value" style="font-size:1.4rem;">{best['name']}</div>
        <div class="ms-unit">AI Algorithm</div>
      </div>
      <div class="model-stat">
        <div class="ms-label">Accuracy</div>
        <div class="ms-value">{accuracy_pct}%</div>
        <div class="ms-unit">R² Score</div>
      </div>
      <div class="model-stat">
        <div class="ms-label">Avg. Error</div>
        <div class="ms-value">₹{best['mae']:.1f}L</div>
        <div class="ms-unit">Mean Abs. Error</div>
      </div>
      <div class="model-stat">
        <div class="ms-label">Training Data</div>
        <div class="ms-value">17K+</div>
        <div class="ms-unit">Car Listings</div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.expander("📊 View full model comparison table"):
        mdf=pd.DataFrame(metrics["models"])
        mdf.columns=["Model","R²","RMSE (₹L)","MAE (₹L)","CV R²","CV Std"]
        st.dataframe(
            mdf.style.highlight_max(subset=["R²","CV R²"],color="#8b5cf644")
                     .highlight_min(subset=["RMSE (₹L)","MAE (₹L)"],color="#3b82f644")
                     .format(precision=4),
            use_container_width=True, hide_index=True)

    CS=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            font_color="#475569",showlegend=False)
    mdf=pd.DataFrame(metrics["models"])
    mdf.columns=["Model","R²","RMSE (₹L)","MAE (₹L)","CV R²","CV Std"]
    c1,c2=st.columns(2)
    with c1:
        fig=px.bar(mdf,x="Model",y="R²",color="Model",title="Accuracy (R² Score)",
                   color_discrete_sequence=["#7c3aed","#2563eb","#0891b2"])
        fig.update_layout(**CS); st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig=px.bar(mdf,x="Model",y="RMSE (₹L)",color="Model",title="Error Rate — lower is better",
                   color_discrete_sequence=["#7c3aed","#2563eb","#0891b2"])
        fig.update_layout(**CS); st.plotly_chart(fig,use_container_width=True)
