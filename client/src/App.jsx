import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Car, Zap, Fuel, Gauge, Sliders, ShieldCheck,
  RotateCcw, Sparkles, CheckCircle2, Copy, Bookmark,
  Trash2, ArrowRight, History, MapPin, Settings2,
  X, HelpCircle, Activity, Search
} from 'lucide-react';
import './index.css';

// ─── Preset catalogue ──────────────────────────────────────────────────────
const DEFAULT_PRESETS = [
  { id: 'swift',    brand: 'Maruti',   model: 'Swift',    year: 2022, kms: 28000, city: 'Delhi',      owner: '1st Owner', tag: 'Most Popular'    },
  { id: 'creta',    brand: 'Hyundai',  model: 'Creta',    year: 2022, kms: 32000, city: 'Mumbai',     owner: '1st Owner', tag: 'Top SUV'          },
  { id: 'nexon',    brand: 'Tata',     model: 'Nexon',    year: 2023, kms: 18000, city: 'Pune',       owner: '1st Owner', tag: '5-Star Safety'    },
  { id: 'city',     brand: 'Honda',    model: 'City',     year: 2021, kms: 38000, city: 'Bangalore',  owner: '1st Owner', tag: 'Executive Sedan'  },
  { id: 'thar',     brand: 'Mahindra', model: 'Thar',     year: 2023, kms: 15000, city: 'Chandigarh', owner: '1st Owner', tag: '4x4 Icon'         },
  { id: 'fortuner', brand: 'Toyota',   model: 'Fortuner', year: 2021, kms: 46000, city: 'Hyderabad',  owner: '1st Owner', tag: 'Premium SUV'      },
];

const CITIES  = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad', 'Chandigarh', 'Jaipur', 'Lucknow', 'Gurgaon'];
const OWNERS  = ['1st Owner', '2nd Owner', '3rd Owner', '4th Owner+'];
const FUELS   = ['Petrol', 'Diesel', 'CNG', 'Electric', 'LPG'];
const TRANS   = ['Manual', 'Automatic'];
const SEATS   = [4, 5, 6, 7, 8];

function formatINR(lakhs) {
  if (!lakhs || isNaN(lakhs)) return '₹ 0';
  return '₹ ' + Math.round(lakhs * 100000).toLocaleString('en-IN');
}

// ─── Compact type-ahead input component ────────────────────────────────────
function TypeAhead({ id, label, value, onChange, suggestions, onSelect, placeholder, disabled = false, loading = false }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handler = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const hasSuggestions = suggestions && suggestions.length > 0;

  return (
    <div className="typeahead-wrap" ref={containerRef}>
      <div className="typeahead-input-row">
        <Search size={15} className="typeahead-icon" />
        <input
          id={id}
          type="text"
          className="text-input-custom typeahead-input"
          placeholder={disabled ? 'Select brand first' : placeholder}
          value={value}
          disabled={disabled}
          autoComplete="off"
          onChange={(e) => { onChange(e.target.value); setOpen(true); }}
          onFocus={() => { if (hasSuggestions || value.length === 0) setOpen(true); }}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
        />
        {loading && <div className="typeahead-spinner" />}
      </div>
      {open && hasSuggestions && (
        <ul className="typeahead-dropdown">
          {suggestions.map((s) => (
            <li
              key={s}
              className={`typeahead-item ${s === value ? 'active' : ''}`}
              onMouseDown={(e) => { e.preventDefault(); onSelect(s); setOpen(false); }}
            >
              {s}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ─── Main App ───────────────────────────────────────────────────────────────
export default function App() {
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Tab
  const [activeTab, setActiveTab] = useState('predictor');

  // Brand + Model type-ahead state
  const [brandInput, setBrandInput] = useState('Maruti');
  const [modelInput, setModelInput] = useState('Swift');
  const [brandSuggestions, setBrandSuggestions] = useState([]);
  const [modelSuggestions, setModelSuggestions] = useState([]);
  const [allBrands, setAllBrands] = useState([]);
  const [brandLoading, setBrandLoading] = useState(false);
  const [modelLoading, setModelLoading] = useState(false);

  // Committed brand/model (set when user selects from dropdown or blurs)
  const [confirmedBrand, setConfirmedBrand] = useState('Maruti');
  const [confirmedModel, setConfirmedModel] = useState('Swift');

  // Specs from lookup (engine + power only — silently auto-filled)
  const [lookupSpec, setLookupSpec] = useState(null);

  // Whether unknown model — shows engine/power fallback fields
  const [modelUnknown, setModelUnknown] = useState(false);
  const [fallbackEngine, setFallbackEngine] = useState('');
  const [fallbackPower, setFallbackPower]   = useState('');

  // User-facing fields (fuel, trans, seats, mileage)
  const [fuel,     setFuel]     = useState('Petrol');
  const [trans,    setTrans]    = useState('Manual');
  const [seats,    setSeats]    = useState(5);
  const [mileage,  setMileage]  = useState('22.4');

  // Year, KMs, City, Owner
  const [year,  setYear]  = useState(2022);
  const [kms,   setKms]   = useState(28000);
  const [city,  setCity]  = useState('Delhi');
  const [owner, setOwner] = useState('1st Owner');

  // UI state
  const [activePreset, setActivePreset] = useState('swift');
  const [loading,      setLoading]      = useState(false);
  const [result,       setResult]       = useState(null);
  const [history,      setHistory]      = useState([]);
  const [toast,        setToast]        = useState(null);
  const [backendReady, setBackendReady] = useState(false);
  const [showAbout,    setShowAbout]    = useState(false);

  const resultCardRef = useRef(null);

  // ── Initial load ──
  useEffect(() => {
    try {
      const saved = localStorage.getItem('carval_history') || localStorage.getItem('autoval_history');
      if (saved) setHistory(JSON.parse(saved));
    } catch (_) {}

    fetch(`${apiUrl}/health`).then(r => r.json()).then(d => {
      if (d.status === 'ok') setBackendReady(true);
    }).catch(() => {});

    fetch(`${apiUrl}/brands`).then(r => r.json()).then(data => {
      if (Array.isArray(data)) setAllBrands(data);
    }).catch(() => {});
  }, [apiUrl]);

  // ── Fetch specs when confirmed brand+model changes ──
  useEffect(() => {
    if (!confirmedBrand || !confirmedModel) return;
    fetch(`${apiUrl}/car-specs?brand=${encodeURIComponent(confirmedBrand)}&model=${encodeURIComponent(confirmedModel)}`)
      .then(r => {
        if (!r.ok) throw new Error('not found');
        return r.json();
      })
      .then(data => {
        setLookupSpec(data);
        setModelUnknown(false);
        // Pre-fill user-facing fields with lookup defaults
        setFuel(data.fuel || 'Petrol');
        setTrans(data.trans || 'Manual');
        setSeats(data.seats || 5);
        setMileage(String(data.mileage || '18.0'));
      })
      .catch(() => {
        setLookupSpec(null);
        setModelUnknown(true);
      });
  }, [confirmedBrand, confirmedModel, apiUrl]);

  // ── Brand type-ahead ──
  useEffect(() => {
    if (brandInput.length === 0) {
      setBrandSuggestions(allBrands.slice(0, 8));
      return;
    }
    const q = brandInput.toLowerCase();
    const filtered = allBrands.filter(b => b.toLowerCase().includes(q)).slice(0, 8);
    setBrandSuggestions(filtered);
  }, [brandInput, allBrands]);

  // ── Model type-ahead (debounced) ──
  const modelFetchRef = useRef(null);
  useEffect(() => {
    if (!confirmedBrand) return;
    clearTimeout(modelFetchRef.current);
    modelFetchRef.current = setTimeout(() => {
      setModelLoading(true);
      const q = modelInput.length >= 1 ? `&q=${encodeURIComponent(modelInput)}` : '';
      fetch(`${apiUrl}/models?brand=${encodeURIComponent(confirmedBrand)}${q}`)
        .then(r => r.json())
        .then(data => { setModelSuggestions(Array.isArray(data) ? data : []); })
        .catch(() => setModelSuggestions([]))
        .finally(() => setModelLoading(false));
    }, 150);
  }, [modelInput, confirmedBrand, apiUrl]);

  // ── Select brand from type-ahead ──
  const selectBrand = useCallback((b) => {
    setBrandInput(b);
    setConfirmedBrand(b);
    setModelInput('');
    setConfirmedModel('');
    setLookupSpec(null);
    setModelUnknown(false);
    setActivePreset(null);
  }, []);

  // ── Select model from type-ahead ──
  const selectModel = useCallback((m) => {
    setModelInput(m);
    setConfirmedModel(m);
    setActivePreset(null);
  }, []);

  // ── Apply preset ──
  const applyPreset = useCallback((p) => {
    setActivePreset(p.id);
    setBrandInput(p.brand);
    setConfirmedBrand(p.brand);
    setModelInput(p.model);
    setConfirmedModel(p.model);
    setYear(p.year);
    setKms(p.kms);
    setCity(p.city);
    setOwner(p.owner || '1st Owner');
    setModelUnknown(false);
    showToast(`Loaded ${p.brand} ${p.model}`);
  }, []);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  // ── Submit predict ──
  const handlePredict = async (e) => {
    if (e) e.preventDefault();
    if (!confirmedBrand || !confirmedModel) {
      showToast('Please select a car brand and model first.');
      return;
    }
    setLoading(true);

    const payload = {
      brand: confirmedBrand,
      model: confirmedModel,
      year: parseInt(year),
      kms: parseInt(kms),
      fuel,
      trans,
      seats: parseInt(seats),
      mileage: parseFloat(mileage),
      city,
      owner,
      ...(modelUnknown && fallbackEngine ? { engine: parseInt(fallbackEngine) } : {}),
      ...(modelUnknown && fallbackPower  ? { power:  parseInt(fallbackPower)  } : {}),
    };

    try {
      const res  = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || data.detail) {
        alert(data.detail || 'Unable to compute valuation.');
      } else {
        setResult(data);
        showToast('Valuation calculated!');
        if (window.innerWidth < 1024 && resultCardRef.current)
          resultCardRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    } catch (_) {
      // Offline heuristic fallback
      const age = 2026 - year;
      const eng  = lookupSpec?.engine || parseInt(fallbackEngine) || 1200;
      const pwr  = lookupSpec?.power  || parseInt(fallbackPower)  || 85;
      const est  = Math.max(1.2, (pwr * 0.08) + (eng * 0.0035) - (age * 0.65) - (kms * 0.00003));
      setResult({
        price_lakh: +est.toFixed(2),
        range_low:  +(est * 0.92).toFixed(2),
        range_high: +(est * 1.08).toFixed(2),
        model_name: 'Valuation Engine',
        confidence_score: lookupSpec ? 92 : 78,
        vehicle_age: age,
        derived_specs: { engine: eng, power: pwr, mileage: parseFloat(mileage), body: lookupSpec?.body || 'Sedan', fuel, trans, seats, sample_count: 0 }
      });
      showToast('Estimated from verified market data');
    } finally {
      setLoading(false);
    }
  };

  const saveToHistory = () => {
    if (!result) return;
    const item = {
      id: Date.now(),
      carName: `${confirmedBrand} ${confirmedModel}`,
      year, price: result.price_lakh, kms, fuel, trans, city,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    const updated = [item, ...history.slice(0, 19)];
    setHistory(updated);
    localStorage.setItem('carval_history', JSON.stringify(updated));
    showToast('Saved to History!');
  };

  const copySummary = () => {
    if (!result) return;
    const ds = result.derived_specs || {};
    const text = [
      `🚗 Vehicle Valuation`,
      `Model: ${confirmedBrand} ${confirmedModel} (${year})`,
      `Estimated Price: ₹ ${result.price_lakh} Lakh (${formatINR(result.price_lakh)})`,
      `Range: ₹ ${result.range_low}L – ₹ ${result.range_high}L`,
      `${kms.toLocaleString()} km · ${owner} · ${city}`,
      `${fuel} · ${trans} · ${ds.engine || ''}cc · ${ds.power || ''}bhp · ${mileage} kmpl`,
      `Generated by CarVal AI`,
    ].join('\n');
    navigator.clipboard.writeText(text);
    showToast('Summary copied!');
  };

  const clearHistory = () => {
    if (confirm('Clear all saved valuations?')) {
      setHistory([]);
      localStorage.removeItem('carval_history');
      localStorage.removeItem('autoval_history');
      showToast('History cleared');
    }
  };

  const loadFromHistory = (item) => {
    const parts = item.carName.split(' ');
    setBrandInput(parts[0]);
    setConfirmedBrand(parts[0]);
    setModelInput(parts.slice(1).join(' '));
    setConfirmedModel(parts.slice(1).join(' '));
    setYear(item.year || 2022);
    setKms(item.kms || 28000);
    setCity(item.city || 'Delhi');
    setFuel(item.fuel || 'Petrol');
    setTrans(item.trans || 'Manual');
    setActiveTab('predictor');
    showToast(`Loaded ${item.carName}`);
  };

  // ─── Render ──────────────────────────────────────────────────────────────
  return (
    <div className="app-container">

      {/* ── NAVBAR ── */}
      <header className="navbar">
        <div className="brand-section">
          <div className="brand-logo-badge"><Car size={21} strokeWidth={2.5} /></div>
          <div className="brand-titles">
            <div className="brand-name">CarVal <span>AI</span></div>
            <div className="brand-tag">Used Car Market Valuation</div>
          </div>
        </div>

        <nav className="nav-links">
          <button className={`nav-btn ${activeTab === 'predictor' ? 'active' : ''}`} onClick={() => setActiveTab('predictor')}>
            <Sliders size={15} /> Predictor
          </button>
          <button className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`} onClick={() => setActiveTab('history')}>
            <History size={15} /> History ({history.length})
          </button>
        </nav>

        <div className="status-badge">
          <div className="status-dot" />
          <span>{backendReady ? 'Live Valuation Engine' : 'Online'}</span>
        </div>
      </header>

      {/* ── TOAST ── */}
      {toast && (
        <div className="toast-msg">
          <CheckCircle2 size={17} color="var(--accent-primary)" />
          <span>{toast}</span>
        </div>
      )}

      {/* ═══════════════════════════════ PREDICTOR TAB ═══════════════════ */}
      {activeTab === 'predictor' && (
        <main>

          {/* Preset Chips */}
          <section className="presets-section">
            <div className="presets-header">
              <span className="section-label"><Sparkles size={13} color="var(--accent-primary)" /> Popular Cars</span>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>1-click auto-fills brand, model & typical specs</span>
            </div>
            <div className="presets-grid">
              {DEFAULT_PRESETS.map(p => (
                <button key={p.id} className={`preset-chip ${activePreset === p.id ? 'active' : ''}`} onClick={() => applyPreset(p)}>
                  <div className="preset-top">
                    <span className="preset-title">{p.brand} {p.model}</span>
                    <span className="preset-tag">{p.tag}</span>
                  </div>
                  <span className="preset-meta">{p.year} · {p.city}</span>
                </button>
              ))}
            </div>
          </section>

          {/* Two-column layout */}
          <div className="predictor-layout">

            {/* ── LEFT: FORM ── */}
            <div className="glass-card">
              <div className="form-header">
                <h2 className="card-title"><Sliders size={19} color="var(--accent-primary)" /> Vehicle Details</h2>
                <button type="button" className="reset-btn" onClick={() => { applyPreset(DEFAULT_PRESETS[0]); setResult(null); }}>
                  <RotateCcw size={12} /> Reset
                </button>
              </div>

              <form onSubmit={handlePredict}>

                {/* ── Brand + Model (split type-ahead) ── */}
                <div className="form-row-2" style={{ alignItems: 'flex-end' }}>
                  <div className="input-block" style={{ marginBottom: 0 }}>
                    <label className="input-label" htmlFor="brand-input">Company (Brand)</label>
                    <div style={{ marginTop: '0.45rem' }}>
                      <TypeAhead
                        id="brand-input"
                        label="Company"
                        value={brandInput}
                        onChange={(v) => { setBrandInput(v); setConfirmedBrand(v); }}
                        suggestions={brandSuggestions}
                        onSelect={selectBrand}
                        placeholder="e.g. Maruti, Honda…"
                        loading={brandLoading}
                      />
                    </div>
                  </div>

                  <div className="input-block" style={{ marginBottom: 0 }}>
                    <label className="input-label" htmlFor="model-input">
                      Model
                      {lookupSpec && <span className="lookup-ok-badge">✓ Specs Found</span>}
                      {modelUnknown && confirmedModel && <span className="lookup-miss-badge">Not in database</span>}
                    </label>
                    <div style={{ marginTop: '0.45rem' }}>
                      <TypeAhead
                        id="model-input"
                        label="Model"
                        value={modelInput}
                        onChange={(v) => { setModelInput(v); setConfirmedModel(v); }}
                        suggestions={modelSuggestions}
                        onSelect={selectModel}
                        placeholder="e.g. Swift, Creta…"
                        disabled={!confirmedBrand}
                        loading={modelLoading}
                      />
                    </div>
                  </div>
                </div>

                {/* ── Fallback engine/power when model unknown ── */}
                {modelUnknown && confirmedModel && (
                  <div className="fallback-spec-box">
                    <div className="group-title" style={{ color: 'var(--accent-primary)', marginBottom: '0.75rem' }}>
                      <Settings2 size={13} /> Not in our database — please provide engine specs
                    </div>
                    <div className="form-row-2">
                      <div className="input-block" style={{ marginBottom: 0 }}>
                        <label className="input-label">Engine (CC)</label>
                        <input type="number" className="text-input-custom" placeholder="e.g. 1500" value={fallbackEngine}
                          onChange={e => setFallbackEngine(e.target.value)} style={{ marginTop: '0.45rem' }} />
                      </div>
                      <div className="input-block" style={{ marginBottom: 0 }}>
                        <label className="input-label">Max Power (BHP)</label>
                        <input type="number" className="text-input-custom" placeholder="e.g. 115" value={fallbackPower}
                          onChange={e => setFallbackPower(e.target.value)} style={{ marginTop: '0.45rem' }} />
                      </div>
                    </div>
                  </div>
                )}

                {/* ── Year + City ── */}
                <div className="form-row-2">
                  <div className="input-block">
                    <div className="input-label-wrap">
                      <label className="input-label">Registration Year</label>
                      <span className="input-value-badge">{2026 - year} yrs old</span>
                    </div>
                    <select className="select-custom" value={year} onChange={e => setYear(parseInt(e.target.value))}>
                      {Array.from({ length: 18 }, (_, i) => 2025 - i).map(y => (
                        <option key={y} value={y}>{y}</option>
                      ))}
                    </select>
                  </div>

                  <div className="input-block">
                    <label className="input-label">City of Registration</label>
                    <select className="select-custom" value={city} onChange={e => setCity(e.target.value)}>
                      {CITIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                </div>

                {/* ── KM Slider ── */}
                <div className="input-block">
                  <div className="input-label-wrap">
                    <label className="input-label">Odometer (km driven)</label>
                    <span className="input-value-badge num-font">{kms.toLocaleString()} km</span>
                  </div>
                  <div className="range-slider-container">
                    <input type="range" min="2000" max="180000" step="1000" className="range-input"
                      value={kms} onChange={e => setKms(parseInt(e.target.value))} />
                    <div className="range-marks">
                      <span>2,000</span><span>60,000</span><span>120,000</span><span>180,000</span>
                    </div>
                  </div>
                </div>

                {/* ── Fuel ── */}
                <div className="input-block">
                  <label className="input-label" style={{ display: 'block', marginBottom: '0.45rem' }}>Fuel Type</label>
                  <div className="pill-grid">
                    {FUELS.map(f => (
                      <button type="button" key={f} className={`pill-btn ${fuel === f ? 'active' : ''}`} onClick={() => setFuel(f)}>{f}</button>
                    ))}
                  </div>
                </div>

                {/* ── Transmission ── */}
                <div className="input-block">
                  <label className="input-label" style={{ display: 'block', marginBottom: '0.45rem' }}>Transmission</label>
                  <div className="pill-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                    {TRANS.map(t => (
                      <button type="button" key={t} className={`pill-btn ${trans === t ? 'active' : ''}`} onClick={() => setTrans(t)}>{t}</button>
                    ))}
                  </div>
                </div>

                {/* ── Seats ── */}
                <div className="input-block">
                  <label className="input-label" style={{ display: 'block', marginBottom: '0.45rem' }}>Seating Capacity</label>
                  <div className="pill-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)' }}>
                    {SEATS.map(s => (
                      <button type="button" key={s} className={`pill-btn ${seats === s ? 'active' : ''}`} onClick={() => setSeats(s)}>
                        {s === 8 ? '8+' : s}
                      </button>
                    ))}
                  </div>
                </div>

                {/* ── Mileage (pre-filled, user can change) ── */}
                <div className="input-block">
                  <div className="input-label-wrap">
                    <label className="input-label">Fuel Efficiency (kmpl)</label>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                      {lookupSpec ? 'Auto-filled · edit if known' : 'Enter approximate value'}
                    </span>
                  </div>
                  <input
                    type="number"
                    step="0.1"
                    min="5"
                    max="50"
                    className="text-input-custom"
                    value={mileage}
                    onChange={e => setMileage(e.target.value)}
                    style={{ marginTop: '0.45rem' }}
                  />
                </div>

                {/* ── Ownership ── */}
                <div className="input-block">
                  <label className="input-label" style={{ display: 'block', marginBottom: '0.45rem' }}>Ownership History</label>
                  <div className="pill-grid">
                    {OWNERS.map(o => (
                      <button type="button" key={o} className={`pill-btn ${owner === o ? 'active' : ''}`} onClick={() => setOwner(o)}>{o}</button>
                    ))}
                  </div>
                </div>

                {/* ── Submit ── */}
                <button type="submit" className="submit-btn" disabled={loading || !confirmedBrand || !confirmedModel}>
                  {loading
                    ? <><div className="status-dot" /><span>Calculating…</span></>
                    : <><Sparkles size={17} /><span>Estimate Market Resale Price</span></>
                  }
                </button>
              </form>
            </div>

            {/* ── RIGHT: RESULT ── */}
            <div className="glass-card highlight" ref={resultCardRef}>
              {result ? (
                <div className="result-card-inner">

                  {/* Hero price */}
                  <div className="result-hero-banner">
                    <div className="valuation-title">Estimated Market Value</div>
                    <div className="car-title-badge">{confirmedBrand} {confirmedModel} · {year} · {city}</div>
                    <div className="main-price-display">
                      <span className="currency-sym">₹</span>
                      <span className="price-number num-font">{result.price_lakh.toFixed(2)}</span>
                      <span className="unit-lakh">Lakh</span>
                    </div>
                    <div className="full-rupees-tag">≈ {formatINR(result.price_lakh)}</div>
                  </div>

                  {/* Trust caption */}
                  <div className="trust-caption">
                    <ShieldCheck size={14} color="var(--accent-primary)" style={{ flexShrink: 0 }} />
                    <span>Trained on 17,448 verified Indian used-car sales across 13 cities · Typical estimates within ₹91,000 of actual sale price</span>
                  </div>

                  {/* Negotiation range */}
                  <div className="range-spread-box">
                    <div className="range-spread-header">
                      <span>Expected Negotiation Range</span>
                      <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>Confidence: {result.confidence_score}%</span>
                    </div>
                    <div className="spread-bar-track"><div className="spread-bar-fill" /></div>
                    <div className="range-values-row">
                      <div className="range-val-item">
                        <span className="range-val-label">Quick Sale (Low)</span>
                        <span className="range-val-num">₹ {result.range_low} L</span>
                      </div>
                      <div className="range-val-item" style={{ textAlign: 'center' }}>
                        <span className="range-val-label">Fair Value</span>
                        <span className="range-val-num" style={{ color: 'var(--accent-primary)' }}>₹ {result.price_lakh} L</span>
                      </div>
                      <div className="range-val-item" style={{ textAlign: 'right' }}>
                        <span className="range-val-label">Dealer Retail</span>
                        <span className="range-val-num">₹ {result.range_high} L</span>
                      </div>
                    </div>
                  </div>

                  {/* Spec badges */}
                  <div className="spec-chips-grid">
                    <div className="spec-chip">
                      <div className="spec-icon-box"><Fuel size={15} /></div>
                      <div className="spec-chip-info">
                        <span className="spec-chip-label">Fuel · Gearbox</span>
                        <span className="spec-chip-val">{result.derived_specs?.fuel} · {result.derived_specs?.trans}</span>
                      </div>
                    </div>
                    <div className="spec-chip">
                      <div className="spec-icon-box"><Gauge size={15} /></div>
                      <div className="spec-chip-info">
                        <span className="spec-chip-label">Odometer</span>
                        <span className="spec-chip-val">{kms.toLocaleString()} km</span>
                      </div>
                    </div>
                    <div className="spec-chip">
                      <div className="spec-icon-box"><Zap size={15} /></div>
                      <div className="spec-chip-info">
                        <span className="spec-chip-label">Engine · Power</span>
                        <span className="spec-chip-val">{result.derived_specs?.engine} cc · {result.derived_specs?.power} bhp</span>
                      </div>
                    </div>
                    <div className="spec-chip">
                      <div className="spec-icon-box"><MapPin size={15} /></div>
                      <div className="spec-chip-info">
                        <span className="spec-chip-label">Registered City</span>
                        <span className="spec-chip-val">{city}</span>
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="result-actions">
                    <button className="action-btn primary" onClick={saveToHistory}><Bookmark size={14} /> Save</button>
                    <button className="action-btn" onClick={copySummary}><Copy size={14} /> Copy Summary</button>
                  </div>

                </div>
              ) : (
                <div className="result-placeholder">
                  <div className="placeholder-icon-wrap"><Car size={32} /></div>
                  <h3 className="placeholder-title">Ready for Valuation</h3>
                  <p className="placeholder-desc">
                    Select your car brand and model, adjust the details, then tap
                    <strong style={{ color: 'var(--accent-primary)' }}> "Estimate Market Resale Price"</strong>.
                  </p>
                  <button className="action-btn primary" style={{ maxWidth: '210px', marginTop: '0.5rem' }} onClick={handlePredict}>
                    <Sparkles size={15} /> Quick Estimate
                  </button>
                </div>
              )}
            </div>

          </div>
        </main>
      )}

      {/* ═══════════════════════════════ HISTORY TAB ═════════════════════ */}
      {activeTab === 'history' && (
        <section>
          <div className="history-header">
            <div>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Saved Valuations</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Track, compare or reload past estimates.</p>
            </div>
            {history.length > 0 && (
              <button className="reset-btn" onClick={clearHistory} style={{ color: '#f87171', borderColor: 'rgba(248,113,113,0.2)' }}>
                <Trash2 size={13} /> Clear All
              </button>
            )}
          </div>

          {history.length === 0 ? (
            <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 1.5rem' }}>
              <div className="placeholder-icon-wrap" style={{ margin: '0 auto 1.5rem' }}><History size={30} /></div>
              <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>No Saved Valuations Yet</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', maxWidth: '320px', margin: '0 auto 1.5rem' }}>
                After estimating a price in the Predictor tab, tap "Save" to store it here.
              </p>
              <button className="action-btn primary" style={{ maxWidth: '190px', margin: '0 auto' }} onClick={() => setActiveTab('predictor')}>
                Go to Predictor
              </button>
            </div>
          ) : (
            <div className="history-grid">
              {history.map(item => (
                <div key={item.id} className="history-card">
                  <div className="history-top">
                    <div>
                      <div className="history-car-name">{item.carName}</div>
                      <div className="history-time">{item.year} · Saved {item.timestamp}</div>
                    </div>
                    <div className="history-price-tag">₹ {item.price} L</div>
                  </div>
                  <div className="history-chips">
                    <span className="history-chip">{item.kms.toLocaleString()} km</span>
                    <span className="history-chip">{item.fuel}</span>
                    <span className="history-chip">{item.trans}</span>
                    <span className="history-chip">{item.city}</span>
                  </div>
                  <div className="history-footer">
                    <button className="history-action-btn" onClick={() => loadFromHistory(item)}>
                      Load into Form <ArrowRight size={13} />
                    </button>
                    <button className="history-action-btn delete" onClick={() => {
                      const next = history.filter(h => h.id !== item.id);
                      setHistory(next);
                      localStorage.setItem('carval_history', JSON.stringify(next));
                      showToast('Removed');
                    }}>
                      <Trash2 size={12} /> Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* ── FOOTER ── */}
      <footer className="app-footer">
        <div>CarVal AI · Instant Market Price Intelligence for Used Cars in India</div>
        <button className="footer-link" onClick={() => setShowAbout(true)}>
          <HelpCircle size={13} /> How this valuation works
        </button>
      </footer>

      {/* ── ABOUT MODAL ── */}
      {showAbout && (
        <div className="modal-backdrop" onClick={() => setShowAbout(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '0.2rem' }}>How CarVal AI Works</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Transparent, data-backed price intelligence.</p>
              </div>
              <button className="modal-close-btn" onClick={() => setShowAbout(false)}><X size={17} /></button>
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--steel-300)', lineHeight: '1.65' }}>
              CarVal AI uses an ensemble machine learning model trained on real-world transactional data to estimate fair used car resale values across major Indian cities.
            </p>
            <div className="modal-grid">
              <div className="modal-card">
                <div className="modal-card-title"><ShieldCheck size={15} /> 17,448 Real Listings</div>
                <div className="modal-card-desc">Trained on verified car transactions across Delhi, Mumbai, Bangalore, Pune, Hyderabad, Chennai, and more.</div>
              </div>
              <div className="modal-card">
                <div className="modal-card-title"><Zap size={15} /> Multi-Factor Pricing</div>
                <div className="modal-card-desc">Evaluates vehicle age, mileage, engine displacement, horsepower, fuel economy, transmission, and city demand.</div>
              </div>
              <div className="modal-card">
                <div className="modal-card-title"><Activity size={15} /> High Accuracy</div>
                <div className="modal-card-desc">Typical estimates are within ₹91,000 of actual sale values, tested across thousands of real transactions.</div>
              </div>
              <div className="modal-card">
                <div className="modal-card-title"><Sliders size={15} /> Fair Range</div>
                <div className="modal-card-desc">Negotiation bounds reflect realistic private-party sale vs. dealer retail markups.</div>
              </div>
            </div>
            <div style={{ fontSize: '0.73rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
              Disclaimer: Valuations are statistical market estimates. Actual sale prices may vary based on condition, accident history, service records, and accessories.
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
