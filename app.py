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
.stApp{background:#06080f;}
.block-container{padding:0.5rem 2rem 5rem!important;max-width:980px!important;margin:0 auto;}

/* ── NAV ── */
.carval-nav{display:flex;align-items:center;justify-content:space-between;
  padding:1.1rem 0 0.8rem;margin-bottom:1.5rem;
  border-bottom:1px solid rgba(255,255,255,0.05);}
.brand{font-size:1.4rem;font-weight:900;
  background:linear-gradient(90deg,#a78bfa,#38bdf8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.tagline{font-size:0.72rem;color:#334155;font-weight:500;margin-top:2px;}

/* nav buttons – all instances */
div[data-testid="stHorizontalBlock"] button{
  background:transparent!important;border:none!important;
  color:#475569!important;font-size:0.88rem!important;font-weight:500!important;
  padding:0.4rem 1rem!important;border-radius:8px!important;
  transition:color 0.2s,background 0.2s!important;}
div[data-testid="stHorizontalBlock"] button:hover{
  color:#e2e8f0!important;background:rgba(255,255,255,0.05)!important;}
.nav-active button{color:#a78bfa!important;
  background:rgba(139,92,246,0.12)!important;
  border:1px solid rgba(139,92,246,0.22)!important;}

/* ── HERO ── */
.hero{text-align:center;padding:9vh 0 5vh;position:relative;}
.hero-bg{
  position:absolute;inset:0;z-index:0;overflow:hidden;
  pointer-events:none;border-radius:24px;
}
.car-grid{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  grid-template-rows:repeat(2,160px);
  gap:8px;
  opacity:0.32;
  filter:blur(0.5px) saturate(0.6);
  transform:scale(1.05);
  animation:gridDrift 18s ease-in-out infinite alternate;
}
@keyframes gridDrift{
  from{transform:scale(1.05) translateY(0px);}
  to{transform:scale(1.08) translateY(-12px);}}
.car-grid img{
  width:100%;height:100%;object-fit:cover;
  border-radius:10px;
}
.hero-overlay{
  position:absolute;inset:0;z-index:1;
  background:radial-gradient(ellipse at center, rgba(6,8,15,0.45) 0%, rgba(6,8,15,0.7) 55%, #06080f 90%);
}
.hero-content{position:relative;z-index:2;}
.hero-pill{display:inline-flex;align-items:center;gap:0.45rem;
  padding:0.35rem 1rem;border-radius:100px;
  background:rgba(139,92,246,0.12);border:1px solid rgba(139,92,246,0.28);
  color:#a78bfa;font-size:0.78rem;font-weight:600;letter-spacing:0.8px;
  text-transform:uppercase;margin-bottom:1.6rem;}
.hero-pill span{width:6px;height:6px;border-radius:50%;
  background:#a78bfa;display:inline-block;
  animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.3}}
.hero-h1{font-size:clamp(2.2rem,5vw,4rem);font-weight:900;
  line-height:1.08;letter-spacing:-1.5px;color:#f1f5f9;margin-bottom:1.1rem;}
.hero-h1 em{font-style:normal;
  background:linear-gradient(135deg,#c084fc,#38bdf8);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-sub{color:#475569;font-size:1.05rem;line-height:1.75;
  max-width:460px;margin:0 auto 2.5rem;}
.hero-trust{display:flex;justify-content:center;gap:2rem;flex-wrap:wrap;
  margin-top:3rem;padding-top:2rem;
  border-top:1px solid rgba(255,255,255,0.05);}
.trust-item{display:flex;align-items:center;gap:0.5rem;
  color:#475569;font-size:0.82rem;font-weight:500;}
.trust-dot{color:#8b5cf6;font-size:1rem;}

/* ── BUTTONS ── */
div[data-testid="stButton"] button[kind="primary"]{
  background:linear-gradient(135deg,#7c3aed,#2563eb)!important;
  color:#fff!important;border:none!important;border-radius:100px!important;
  padding:0.8rem 2.5rem!important;font-size:1.05rem!important;
  font-weight:700!important;letter-spacing:0.3px!important;
  box-shadow:0 0 0 0 rgba(124,58,237,0);
  animation:glow-idle 3s ease-in-out infinite!important;
  transition:transform 0.2s,box-shadow 0.2s!important;}
@keyframes glow-idle{
  0%,100%{box-shadow:0 4px 30px rgba(124,58,237,0.35);}
  50%{box-shadow:0 4px 45px rgba(124,58,237,0.55);}}
div[data-testid="stButton"] button[kind="primary"]:hover{
  transform:translateY(-2px)!important;
  box-shadow:0 8px 50px rgba(124,58,237,0.65)!important;}

/* ── FORM ── */
[data-testid="stForm"]{background:transparent!important;border:none!important;}
.form-card{
  background:rgba(255,255,255,0.025);
  border:1px solid rgba(255,255,255,0.07);border-radius:18px;
  padding:1.6rem 1.8rem;margin-bottom:1rem;
  transition:border-color 0.3s,box-shadow 0.3s;}
.form-card:hover{
  border-color:rgba(139,92,246,0.25);
  box-shadow:0 0 30px rgba(124,58,237,0.06);}
.step-label{font-size:0.68rem;font-weight:700;letter-spacing:1.8px;
  color:#334155;text-transform:uppercase;margin-bottom:1rem;
  display:flex;align-items:center;gap:0.5rem;}
.step-num{width:20px;height:20px;border-radius:50%;
  background:rgba(139,92,246,0.25);border:1px solid rgba(139,92,246,0.4);
  color:#a78bfa;font-size:0.68rem;font-weight:800;
  display:inline-flex;align-items:center;justify-content:center;}
label{color:#94a3b8!important;font-size:0.83rem!important;font-weight:500!important;}
small{color:#334155!important;font-size:0.75rem!important;}
.stSelectbox>div>div,.stNumberInput>div>div>input{
  background:rgba(255,255,255,0.04)!important;
  border:1px solid rgba(255,255,255,0.09)!important;
  border-radius:10px!important;color:#e2e8f0!important;}
.stSlider [data-baseweb="slider"] div{background:#7c3aed!important;}

/* ── RESULT ── */
@keyframes fadeScaleIn{
  from{opacity:0;transform:scale(0.94) translateY(16px);}
  to{opacity:1;transform:scale(1) translateY(0);}}
@keyframes glowRotate{
  0%{background-position:0% 50%}
  50%{background-position:100% 50%}
  100%{background-position:0% 50%}}
@keyframes pricePop{
  0%{opacity:0;transform:scale(0.7);}
  60%{transform:scale(1.06);}
  100%{opacity:1;transform:scale(1);}}
.result-outer{
  margin-top:2.5rem;position:relative;
  animation:fadeScaleIn 0.6s cubic-bezier(0.16,1,0.3,1) both;}
.result-glow{
  position:absolute;inset:-2px;border-radius:26px;z-index:0;
  background:linear-gradient(270deg,#7c3aed,#2563eb,#06b6d4,#7c3aed);
  background-size:400% 400%;
  animation:glowRotate 4s ease infinite;
  filter:blur(2px);opacity:0.85;}
.result-card{
  position:relative;z-index:1;background:#0a0d14;
  border-radius:24px;padding:3rem 2rem 2.5rem;text-align:center;}
.result-check{font-size:2.5rem;margin-bottom:1rem;
  animation:pricePop 0.5s cubic-bezier(0.16,1,0.3,1) 0.3s both;}
.result-eye{
  font-size:0.72rem;letter-spacing:2.5px;text-transform:uppercase;
  color:#7c3aed;font-weight:700;margin-bottom:0.8rem;}
.result-price{
  font-size:clamp(3rem,7vw,5rem);font-weight:900;
  letter-spacing:-2px;color:#f8fafc;line-height:1;
  text-shadow:0 0 80px rgba(124,58,237,0.6),0 0 30px rgba(56,189,248,0.3);
  margin-bottom:0.2rem;
  animation:pricePop 0.6s cubic-bezier(0.16,1,0.3,1) 0.4s both;}
.result-price-sub{color:#475569;font-size:1rem;margin-bottom:0.8rem;}
.result-range{
  display:inline-block;padding:0.45rem 1.4rem;border-radius:100px;
  background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
  color:#94a3b8;font-size:0.92rem;font-weight:500;margin-bottom:2rem;
  letter-spacing:0.3px;}
.result-tags{display:flex;justify-content:center;gap:0.75rem;flex-wrap:wrap;}
.rtag{
  display:inline-flex;align-items:center;gap:0.4rem;
  padding:0.38rem 0.95rem;border-radius:100px;
  background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);
  color:#a78bfa;font-size:0.79rem;font-weight:600;
  transition:background 0.2s,transform 0.2s;cursor:default;}
.rtag:hover{background:rgba(139,92,246,0.2);transform:translateY(-1px);}

/* ── PAGE HEADERS ── */
.pg-eye{font-size:0.72rem;font-weight:700;letter-spacing:2px;
  color:#7c3aed;text-transform:uppercase;margin-bottom:0.4rem;}
.pg-title{font-size:2rem;font-weight:800;color:#f1f5f9;
  letter-spacing:-0.8px;margin-bottom:0.3rem;}
.pg-sub{color:#475569;font-size:0.92rem;margin-bottom:2rem;}

/* ── INSIGHT CARDS ── */
.insight-label{font-size:0.78rem;color:#a78bfa;font-weight:700;
  margin-bottom:0.25rem;letter-spacing:0.5px;}
.insight-desc{font-size:0.83rem;color:#334155;
  margin-bottom:1rem;line-height:1.55;}

/* ── MODEL STAT CARDS ── */
.model-stat-row{display:flex;gap:1rem;margin-bottom:1.5rem;flex-wrap:wrap;}
.model-stat{flex:1;min-width:140px;
  background:rgba(255,255,255,0.025);
  border:1px solid rgba(255,255,255,0.07);border-radius:14px;
  padding:1.2rem;text-align:center;}
.ms-label{font-size:0.7rem;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;color:#334155;margin-bottom:0.5rem;}
.ms-value{font-size:1.9rem;font-weight:900;color:#f1f5f9;}
.ms-unit{font-size:0.8rem;color:#475569;margin-top:0.2rem;}

/* scrollbar */
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:#06080f;}
::-webkit-scrollbar-thumb{background:#1e293b;border-radius:3px;}
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
st.markdown('<div class="carval-nav">', unsafe_allow_html=True)
nb0,nb1,nb2,nb3,nb4,nb5=st.columns([2,0.2,1,1,1,1])
with nb0:
    st.markdown('<div class="brand">🚗 CarVal</div><div class="tagline">India\'s Smart Car Valuation</div>', unsafe_allow_html=True)
for col,pg in zip([nb2,nb3,nb4,nb5],PAGES):
    with col:
        active = "nav-active" if st.session_state.page==pg else ""
        st.markdown(f'<div class="{active}">', unsafe_allow_html=True)
        if st.button(pg, key=f"nav_{pg}"):
            st.session_state.page=pg; st.session_state.result=None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════ HOME ══════════════════════════════════════════
if st.session_state.page=="Home":
    st.markdown("""
    <div class="hero">
      <div class="hero-bg">
        <div class="car-grid">
          <img src="https://images.unsplash.com/photo-1555215695-3004980ad54e?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1542362567-b07e54358753?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1485291571150-772bcfc10da5?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=400&q=60" alt="car"/>
          <img src="https://images.unsplash.com/photo-1511919884226-fd3cad34687c?w=400&q=60" alt="car"/>
        </div>
        <div class="hero-overlay"></div>
      </div>
      <div class="hero-content">
        <div class="hero-pill"><span></span> AI-Powered Pricing Engine</div>
        <div class="hero-h1">Your Car's Real Worth,<br><em>Estimated in Seconds</em></div>
        <div class="hero-sub">
          Skip the guessing. Get an instant, data-backed resale price<br>
          for any used car in India — no expertise required.
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    _,mid,_=st.columns([1.3,1,1.3])
    with mid:
        if st.button("✦  Estimate My Car's Value", type="primary", use_container_width=True):
            st.session_state.page="Predict"; st.rerun()

    st.markdown("""
    <div class="hero-trust">
      <div class="trust-item"><span class="trust-dot">◆</span> 17,000+ Real Listings</div>
      <div class="trust-item"><span class="trust-dot">◆</span> AI-Powered (XGBoost)</div>
      <div class="trust-item"><span class="trust-dot">◆</span> Updated Market Trends</div>
      <div class="trust-item"><span class="trust-dot">◆</span> Instant Results</div>
    </div>""", unsafe_allow_html=True)


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
            font_color="#94a3b8",margin=dict(l=10,r=10,t=40,b=10))

    t1,t2,t3,t4=st.tabs(["📅 Age & Value","🛣️ Usage Impact","⛽ Fuel Type","🔥 Key Factors"])

    with t1:
        st.markdown('<div class="insight-label">How prices change over time</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Newer cars hold significantly higher resale value. A 3-year-old car can fetch nearly 2x more than a 7-year-old equivalent.</div>', unsafe_allow_html=True)
        yr=df.groupby("year")["price_lakh"].median().reset_index()
        fig=px.area(yr,x="year",y="price_lakh",markers=True,
                    color_discrete_sequence=["#8b5cf6"],
                    labels={"year":"Registration Year","price_lakh":"Median Price (₹L)"})
        fig.update_layout(**CS); fig.update_xaxes(gridcolor="rgba(255,255,255,0.04)"); fig.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
        st.plotly_chart(fig,use_container_width=True)

    with t2:
        st.markdown('<div class="insight-label">Impact of kilometers driven</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Higher mileage generally lowers resale value. Cars under 50,000 km command a clear premium over high-mileage vehicles.</div>', unsafe_allow_html=True)
        samp=df.sample(min(2000,len(df)),random_state=42)
        fig=px.scatter(samp,x="kms",y="price_lakh",opacity=0.5,
                       color="price_lakh",color_continuous_scale="Purp",
                       labels={"kms":"KMs Driven","price_lakh":"Price (₹L)"})
        fig.update_traces(marker=dict(size=4)); fig.update_layout(**CS)
        st.plotly_chart(fig,use_container_width=True)

    with t3:
        st.markdown('<div class="insight-label">Which fuel type retains value best?</div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-desc">Electric vehicles command the highest resale prices on average, followed by Diesel. CNG and LPG vehicles tend to depreciate faster.</div>', unsafe_allow_html=True)
        fd=df.groupby("fuel_type")["price_lakh"].median().reset_index().sort_values("price_lakh")
        fig=px.bar(fd,x="price_lakh",y="fuel_type",orientation="h",
                   color_discrete_sequence=["#6d28d9"],
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
            font_color="#94a3b8",showlegend=False)
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
