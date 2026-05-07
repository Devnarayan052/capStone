import { useState, useRef } from 'react';
import { 
  CarFront, Zap, RefreshCw, Calculator, Clock, Home, 
  Info, Car, Activity, Fuel, Settings2, User, Route, ShieldCheck
} from 'lucide-react';
import './index.css';

function App() {
  const [tab, setTab] = useState('home');
  const [formData, setFormData] = useState({
    year: 2024, kms: 18000, fuel: 'CNG', trans: 'Manual',
    owner: 'First', body: 'Hatchback', city: 'Mumbai',
    seats: 5, engine: 1200, mileage: 18.0, power: 85, brand: 'Maruti Suzuki', modelName: 'Ertiga'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const resultRef = useRef(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          year: parseInt(formData.year),
          kms: parseInt(formData.kms),
          seats: parseInt(formData.seats),
          engine: parseInt(formData.engine),
          power: parseInt(formData.power),
          mileage: parseFloat(formData.mileage)
        })
      });
      const data = await response.json();
      if(data.error) {
        alert("Error: " + data.error);
      } else {
        setResult(data);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    } catch (err) {
      alert("Failed to connect to backend: " + err.message);
    }
    setLoading(false);
  };

  return (
    <>
      <div className="page-container">
        
        {/* DESKTOP NAVIGATION (Hidden on mobile) */}
        <div className="desktop-nav">
          <div>
            <div className="app-brand" style={{fontSize: '1.8rem'}}>CarVal <span>AI</span></div>
            <div className="app-subtitle">Premium used-car pricing</div>
          </div>
          <div className="d-tabs">
            <div className={`d-tab ${tab === 'home' ? 'active' : ''}`} onClick={() => setTab('home')}>Home</div>
            <div className={`d-tab ${tab === 'predict' ? 'active' : ''}`} onClick={() => setTab('predict')}>Predict</div>
            <div className={`d-tab ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>History</div>
            <div className={`d-tab ${tab === 'info' ? 'active' : ''}`} onClick={() => setTab('info')}>Info</div>
          </div>
          <div className="icon-btn"><CarFront size={20} /></div>
        </div>

        {/* MOBILE HEADER (Hidden on desktop) */}
        <div className="app-header">
          <div>
            <div className="app-brand">{tab === 'home' ? <>CarVal <span>AI</span></> : tab.charAt(0).toUpperCase() + tab.slice(1)}</div>
            {tab === 'home' && <div className="app-subtitle">Premium used-car pricing</div>}
          </div>
          {tab === 'predict' ? (
             <div style={{color: '#a1a1aa', fontSize: '0.8rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'}} onClick={() => setResult(null)}>
               <RefreshCw size={14} /> Reset
             </div>
          ) : (
            <div className="icon-btn"><CarFront size={20} /></div>
          )}
        </div>

        {/* HOME TAB */}
        {tab === 'home' && (
          <div className="home-layout">
            <div>
              <div className="card-primary" style={{marginBottom: '2rem'}}>
                <h3 style={{marginBottom: '0.5rem', color: '#fafafa', fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <Zap size={24} color="#d4af37" /> Get Instant Price
                </h3>
                <p style={{marginBottom: '2rem', fontSize: '0.9rem'}}>AI-powered valuation for your used car in seconds.</p>
                <button className="btn btn-primary" onClick={() => setTab('predict')}>
                  Predict Now
                </button>
              </div>

              <h3 className="section-title">Quick Actions</h3>
              <div className="quick-actions">
                <div className="qa-card" onClick={() => setTab('predict')}>
                  <div className="qa-icon"><Calculator size={20} /></div>
                  <div className="qa-title">Predict Price</div>
                  <div className="qa-desc">Estimate value</div>
                </div>
                <div className="qa-card" onClick={() => setTab('history')}>
                  <div className="qa-icon"><Clock size={20} /></div>
                  <div className="qa-title">View History</div>
                  <div className="qa-desc">Past results</div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="section-title">Popular in India</h3>
              <div className="h-scroll">
                <div className="brand-card"><Car size={32} color="#fafafa" style={{margin: '0 auto 10px'}}/><h4>Maruti Swift</h4><p>3-7 L</p></div>
                <div className="brand-card"><Car size={32} color="#fafafa" style={{margin: '0 auto 10px'}}/><h4>Hyundai i20</h4><p>4-9 L</p></div>
                <div className="brand-card"><Car size={32} color="#fafafa" style={{margin: '0 auto 10px'}}/><h4>Tata Nexon</h4><p>6-12 L</p></div>
                <div className="brand-card"><Car size={32} color="#fafafa" style={{margin: '0 auto 10px'}}/><h4>Honda City</h4><p>5-15 L</p></div>
              </div>

              <h3 className="section-title" style={{marginTop: '2rem'}}>Platform Stats</h3>
              <div className="stats-row">
                <div className="stat-box"><h4>16+</h4><p>Brands</p></div>
                <div className="stat-box"><h4>13</h4><p>Cities</p></div>
                <div className="stat-box"><h4>~90%</h4><p>Accuracy</p></div>
              </div>
            </div>
          </div>
        )}

        {/* PREDICT TAB */}
        {tab === 'predict' && (
          <div className="predict-layout">
            
            {/* Left side: Results */}
            <div className="predict-results-col" ref={resultRef}>
              {result ? (
                <div className="card-primary" style={{height: '100%'}}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '15px', marginBottom: '1.5rem'}}>
                    <div className="icon-btn" style={{width: 40, height: 40}}><Activity size={18} /></div>
                    <div>
                      <div style={{fontSize: '0.75rem', color: '#a1a1aa', textTransform: 'uppercase'}}>Estimated Market Price</div>
                      <div style={{fontSize: '1.1rem', fontWeight: 600, color: '#fafafa'}}>{formData.brand} {formData.modelName} {formData.year}</div>
                    </div>
                  </div>
                  
                  <div style={{textAlign: 'center', padding: '1rem 0'}}>
                    <div className="hero-price">₹{result.price_lakh.toFixed(2)} <span>L</span></div>
                    <div className="price-range">Range: ₹{result.range_low.toFixed(1)}L - ₹{result.range_high.toFixed(1)}L</div>
                  </div>

                  <div className="confidence-wrapper">
                    <div className="conf-header"><span>Confidence</span><span style={{color: '#d4af37'}}>88%</span></div>
                    <div className="conf-bar"><div className="conf-fill" style={{width: '88%'}}></div></div>
                  </div>

                  <div className="features-row">
                    <div className="feature-item"><span className="feature-icon"><Fuel size={18} /></span>{formData.fuel}</div>
                    <div className="feature-item"><span className="feature-icon"><Settings2 size={18} /></span>{formData.trans}</div>
                    <div className="feature-item"><span className="feature-icon"><User size={18} /></span>{formData.owner}</div>
                    <div className="feature-item"><span className="feature-icon"><Route size={18} /></span>{formData.kms / 1000}k km</div>
                  </div>
                </div>
              ) : (
                <div className="card-primary" style={{height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px', textAlign: 'center'}}>
                  <div className="icon-btn" style={{width: 60, height: 60, marginBottom: '1rem'}}><CarFront size={30} /></div>
                  <h3 style={{color: '#fafafa', marginBottom: '0.5rem'}}>Awaiting Details</h3>
                  <p>Fill out the form to instantly get an AI-powered valuation for your vehicle.</p>
                </div>
              )}
            </div>

            {/* Right side: Form */}
            <div>
              <h3 className="section-title" style={{fontSize: '1rem', color: '#fafafa', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                Vehicle Details
                <span style={{fontSize: '0.8rem', color: '#a1a1aa', fontWeight: 'normal', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'}} onClick={() => setResult(null)}>
                  <RefreshCw size={12} /> Reset Form
                </span>
              </h3>
              
              <form onSubmit={handlePredict}>
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Brand</label>
                    <select className="form-control" name="brand" value={formData.brand} onChange={handleChange}>
                      {['Maruti Suzuki', 'Hyundai', 'Tata', 'Honda', 'Toyota'].map(b => <option key={b}>{b}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Model Name</label>
                    <input type="text" className="form-control" name="modelName" value={formData.modelName} onChange={handleChange} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Year of Manufacture</label>
                    <select className="form-control" name="year" value={formData.year} onChange={handleChange}>
                      {Array.from({length: 20}, (_, i) => 2024 - i).map(y => <option key={y}>{y}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Kilometers Driven (km)</label>
                    <input type="number" className="form-control" name="kms" value={formData.kms} onChange={handleChange} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Fuel Type</label>
                    <select className="form-control" name="fuel" value={formData.fuel} onChange={handleChange}>
                      {['Petrol', 'Diesel', 'CNG', 'Electric'].map(f => <option key={f}>{f}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Transmission</label>
                    <select className="form-control" name="trans" value={formData.trans} onChange={handleChange}>
                      {['Manual', 'Automatic'].map(t => <option key={t}>{t}</option>)}
                    </select>
                  </div>
                  <div className="form-group full-width">
                    <label className="form-label">Ownership</label>
                    <select className="form-control" name="owner" value={formData.owner} onChange={handleChange}>
                      {['First', 'Second', 'Third'].map(o => <option key={o}>{o} Owner</option>)}
                    </select>
                  </div>
                </div>

                <button type="submit" className="btn btn-primary" style={{marginTop: '2rem'}} disabled={loading}>
                  {loading ? "Calculating..." : "Update Estimate"}
                </button>
              </form>
            </div>

          </div>
        )}

        {/* INFO TAB */}
        {tab === 'info' && (
          <div className="predict-layout">
            <div>
              <div className="card-primary" style={{textAlign: 'center', padding: '3rem 1rem'}}>
                <div className="icon-btn" style={{margin: '0 auto 1.5rem', width: 60, height: 60}}><ShieldCheck size={30} /></div>
                <h2 style={{color: '#fafafa', marginBottom: '0.4rem', fontSize: '2rem'}}>CarVal AI</h2>
                <p>Version 1.0.0</p>
                <p style={{marginTop: '1.5rem'}}>An advanced machine learning price estimator specifically tuned for the Indian automotive market.</p>
              </div>
              
              <h3 className="section-title" style={{marginTop: '2rem'}}>Disclaimer</h3>
              <div className="disclaimer">
                This app provides estimates only. Actual market prices may vary based on the car's condition, service history, accessories, and regional demand. Always consult a certified dealer before making a purchase decision.
              </div>
            </div>

            <div>
              <h3 className="section-title">How It Works</h3>
              <div className="step-card">
                <div className="step-num">1</div>
                <div className="step-content">
                  <h4>Enter Details</h4>
                  <p>Provide your car's brand, model, year, fuel type, transmission, ownership, and km driven.</p>
                </div>
              </div>
              <div className="step-card">
                <div className="step-num">2</div>
                <div className="step-content">
                  <h4>AI Calculation</h4>
                  <p>Our formula applies multivariate regression coefficients derived from real Indian used-car datasets.</p>
                </div>
              </div>
              <div className="step-card">
                <div className="step-num">3</div>
                <div className="step-content">
                  <h4>Get Estimate</h4>
                  <p>Receive an estimated price range with a confidence score to help you negotiate better.</p>
                </div>
              </div>

              <h3 className="section-title" style={{marginTop: '2.5rem'}}>Model Features</h3>
              <div className="badge-group">
                {['Brand', 'Year', 'KM Driven', 'Fuel Type', 'Transmission', 'Ownership', 'Location'].map(b => (
                  <div key={b} className="badge">{b}</div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* HISTORY TAB */}
        {tab === 'history' && (
          <div style={{textAlign: 'center', color: '#71717a', marginTop: '10vh'}}>
            <div style={{marginBottom: '1rem', display: 'flex', justifyContent: 'center'}}><Clock size={64} opacity={0.3} /></div>
            <h2 style={{color: '#fafafa'}}>No History Found</h2>
            <p style={{marginTop: '1rem'}}>Your recent predictions will appear here.</p>
          </div>
        )}

      </div>

      {/* MOBILE BOTTOM NAV */}
      <div className="bottom-nav">
        <div className={`nav-item ${tab === 'home' ? 'active' : ''}`} onClick={() => setTab('home')}>
          <div className="nav-icon"><Home size={22} /></div>
          <div>Home</div>
        </div>
        <div className={`nav-item ${tab === 'predict' ? 'active' : ''}`} onClick={() => setTab('predict')}>
          <div className="nav-icon"><Calculator size={22} /></div>
          <div>Predict</div>
        </div>
        <div className={`nav-item ${tab === 'history' ? 'active' : ''}`} onClick={() => setTab('history')}>
          <div className="nav-icon"><Clock size={22} /></div>
          <div>History</div>
        </div>
        <div className={`nav-item ${tab === 'info' ? 'active' : ''}`} onClick={() => setTab('info')}>
          <div className="nav-icon"><Info size={22} /></div>
          <div>Info</div>
        </div>
      </div>
    </>
  );
}

export default App;
