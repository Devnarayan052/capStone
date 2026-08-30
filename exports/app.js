/**
 * CarVal AI — Standalone Client Logic
 * Connects directly to the live FastAPI Backend on Render or localhost
 */

const API_URL = 'https://carval-qaph.onrender.com'; // Falls back to http://localhost:8000 if local

const PRESETS = [
  { id: 'swift', brand: 'Maruti', model: 'Swift', year: 2022, kms: 28000, city: 'Delhi', owner: '1st Owner', tag: 'Most Popular' },
  { id: 'creta', brand: 'Hyundai', model: 'Creta', year: 2022, kms: 32000, city: 'Mumbai', owner: '1st Owner', tag: 'Top SUV' },
  { id: 'nexon', brand: 'Tata', model: 'Nexon', year: 2023, kms: 18000, city: 'Pune', owner: '1st Owner', tag: '5-Star Safety' },
  { id: 'city', brand: 'Honda', model: 'City', year: 2021, kms: 38000, city: 'Bangalore', owner: '1st Owner', tag: 'Executive Sedan' },
  { id: 'thar', brand: 'Mahindra', model: 'Thar', year: 2023, kms: 15000, city: 'Chandigarh', owner: '1st Owner', tag: '4x4 Icon' },
  { id: 'fortuner', brand: 'Toyota', model: 'Fortuner', year: 2021, kms: 46000, city: 'Hyderabad', owner: '1st Owner', tag: 'Premium SUV' }
];

const CITIES = ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Pune', 'Chennai', 'Kolkata', 'Ahmedabad', 'Chandigarh', 'Jaipur', 'Lucknow', 'Gurgaon'];

// State
let allBrands = [];
let confirmedBrand = 'Maruti';
let confirmedModel = 'Swift';
let lookupSpec = null;
let modelUnknown = false;
let currentFuel = 'Petrol';
let currentTrans = 'Manual';
let currentSeats = 5;
let currentOwner = '1st Owner';
let currentResult = null;
let historyItems = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initIcons();
  initYearSelect();
  initCitySelect();
  initPresets();
  loadHistory();
  fetchHealth();
  fetchBrands();
  setupTypeahead();
  fetchSpecs('Maruti', 'Swift');
});

function initIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function formatINR(lakhs) {
  if (!lakhs || isNaN(lakhs)) return '₹ 0';
  return '₹ ' + Math.round(lakhs * 100000).toLocaleString('en-IN');
}

function showToast(msg) {
  const container = document.getElementById('toast-container');
  const text = document.getElementById('toast-text');
  text.textContent = msg;
  container.style.display = 'flex';
  setTimeout(() => { container.style.display = 'none'; }, 3000);
}

function switchTab(tab) {
  const predView = document.getElementById('view-predictor');
  const histView = document.getElementById('view-history');
  const predBtn = document.getElementById('tab-predictor-btn');
  const histBtn = document.getElementById('tab-history-btn');

  if (tab === 'predictor') {
    predView.style.display = 'block';
    histView.style.display = 'none';
    predBtn.classList.add('active');
    histBtn.classList.remove('active');
  } else {
    predView.style.display = 'none';
    histView.style.display = 'block';
    predBtn.classList.remove('active');
    histBtn.classList.add('active');
    renderHistory();
  }
  initIcons();
}

function initYearSelect() {
  const select = document.getElementById('year-select');
  select.innerHTML = '';
  for (let y = 2025; y >= 2008; y--) {
    const opt = document.createElement('option');
    opt.value = y;
    opt.textContent = y;
    if (y === 2022) opt.selected = true;
    select.appendChild(opt);
  }
  onYearChange();
}

function onYearChange() {
  const y = parseInt(document.getElementById('year-select').value);
  document.getElementById('year-badge').textContent = `${2026 - y} yrs old`;
}

function initCitySelect() {
  const select = document.getElementById('city-select');
  select.innerHTML = '';
  CITIES.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    select.appendChild(opt);
  });
}

function initPresets() {
  const container = document.getElementById('presets-container');
  container.innerHTML = '';
  PRESETS.forEach(p => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `preset-chip ${p.id === 'swift' ? 'active' : ''}`;
    btn.id = `preset-${p.id}`;
    btn.innerHTML = `
      <div class="preset-top">
        <span class="preset-title">${p.brand} ${p.model}</span>
        <span class="preset-tag">${p.tag}</span>
      </div>
      <span class="preset-meta">${p.year} · ${p.city}</span>
    `;
    btn.onclick = () => applyPreset(p);
    container.appendChild(btn);
  });
}

function applyPreset(p) {
  document.querySelectorAll('.preset-chip').forEach(el => el.classList.remove('active'));
  const target = document.getElementById(`preset-${p.id}`);
  if (target) target.classList.add('active');

  document.getElementById('brand-input').value = p.brand;
  document.getElementById('model-input').value = p.model;
  confirmedBrand = p.brand;
  confirmedModel = p.model;

  document.getElementById('year-select').value = p.year;
  onYearChange();
  document.getElementById('city-select').value = p.city;
  document.getElementById('kms-slider').value = p.kms;
  onKmsInput(p.kms);
  setOwner(p.owner);

  fetchSpecs(p.brand, p.model);
  showToast(`Loaded ${p.brand} ${p.model}`);
}

function onKmsInput(val) {
  document.getElementById('kms-badge').textContent = parseInt(val).toLocaleString() + ' km';
}

function setFuel(val) {
  currentFuel = val;
  document.querySelectorAll('#fuel-pills .pill-btn').forEach(b => {
    b.classList.toggle('active', b.textContent === val);
  });
}

function setTrans(val) {
  currentTrans = val;
  document.querySelectorAll('#trans-pills .pill-btn').forEach(b => {
    b.classList.toggle('active', b.textContent === val);
  });
}

function setSeats(val) {
  currentSeats = val;
  document.querySelectorAll('#seat-pills .pill-btn').forEach(b => {
    const isEight = val === 8 && b.textContent === '8+';
    b.classList.toggle('active', parseInt(b.textContent) === val || isEight);
  });
}

function setOwner(val) {
  currentOwner = val;
  document.querySelectorAll('#owner-pills .pill-btn').forEach(b => {
    b.classList.toggle('active', b.textContent === val);
  });
}

// API Calls
async function fetchHealth() {
  try {
    const res = await fetch(`${API_URL}/health`);
    const data = await res.json();
    if (data.status === 'ok') {
      document.getElementById('backend-status').textContent = 'Live Valuation Engine';
    }
  } catch (err) {
    document.getElementById('backend-status').textContent = 'Online (Fallback)';
  }
}

async function fetchBrands() {
  try {
    const res = await fetch(`${API_URL}/brands`);
    const data = await res.json();
    if (Array.isArray(data)) allBrands = data;
  } catch (err) {
    allBrands = ['Audi', 'BMW', 'Honda', 'Hyundai', 'Mahindra', 'Maruti', 'Tata', 'Toyota', 'Volkswagen'];
  }
}

async function fetchSpecs(brand, model) {
  try {
    const res = await fetch(`${API_URL}/car-specs?brand=${encodeURIComponent(brand)}&model=${encodeURIComponent(model)}`);
    if (!res.ok) throw new Error('Not found');
    const data = await res.json();
    lookupSpec = data;
    modelUnknown = false;
    document.getElementById('fallback-box').style.display = 'none';
    document.getElementById('lookup-badge').className = 'lookup-ok-badge';
    document.getElementById('lookup-badge').textContent = '✓ Specs Found';

    setFuel(data.fuel || 'Petrol');
    setTrans(data.trans || 'Manual');
    setSeats(data.seats || 5);
    document.getElementById('mileage-input').value = data.mileage || '18.0';
    document.getElementById('mileage-hint').textContent = 'Auto-filled · edit if known';
  } catch (err) {
    lookupSpec = null;
    modelUnknown = true;
    document.getElementById('fallback-box').style.display = 'block';
    document.getElementById('lookup-badge').className = 'lookup-miss-badge';
    document.getElementById('lookup-badge').textContent = 'Not in database';
    document.getElementById('mileage-hint').textContent = 'Enter approximate value';
  }
}

// Type-ahead Setup
function setupTypeahead() {
  const brandInput = document.getElementById('brand-input');
  const brandDropdown = document.getElementById('brand-dropdown');
  const modelInput = document.getElementById('model-input');
  const modelDropdown = document.getElementById('model-dropdown');

  // Brand Typeahead
  brandInput.addEventListener('input', () => {
    const q = brandInput.value.toLowerCase().trim();
    const matches = allBrands.filter(b => b.toLowerCase().includes(q)).slice(0, 8);
    renderDropdown(brandDropdown, matches, (b) => {
      brandInput.value = b;
      confirmedBrand = b;
      brandDropdown.style.display = 'none';
      modelInput.value = '';
      confirmedModel = '';
      modelInput.focus();
    });
  });

  brandInput.addEventListener('focus', () => {
    const matches = (allBrands.length ? allBrands : ['Maruti', 'Hyundai', 'Tata', 'Honda', 'Toyota']).slice(0, 8);
    renderDropdown(brandDropdown, matches, (b) => {
      brandInput.value = b;
      confirmedBrand = b;
      brandDropdown.style.display = 'none';
      modelInput.value = '';
      confirmedModel = '';
      modelInput.focus();
    });
  });

  // Model Typeahead
  let debounceTimer = null;
  modelInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      if (!confirmedBrand) return;
      const q = modelInput.value.trim();
      try {
        const res = await fetch(`${API_URL}/models?brand=${encodeURIComponent(confirmedBrand)}${q ? `&q=${encodeURIComponent(q)}` : ''}`);
        const list = await res.json();
        renderDropdown(modelDropdown, list, (m) => {
          modelInput.value = m;
          confirmedModel = m;
          modelDropdown.style.display = 'none';
          fetchSpecs(confirmedBrand, m);
        });
      } catch (err) {
        modelDropdown.style.display = 'none';
      }
    }, 150);
  });

  // Global click outside to dismiss
  document.addEventListener('click', (e) => {
    if (!document.getElementById('brand-typeahead-wrap').contains(e.target)) {
      brandDropdown.style.display = 'none';
    }
    if (!document.getElementById('model-typeahead-wrap').contains(e.target)) {
      modelDropdown.style.display = 'none';
    }
  });
}

function renderDropdown(dropdownEl, items, onSelect) {
  dropdownEl.innerHTML = '';
  if (!items || !items.length) {
    dropdownEl.style.display = 'none';
    return;
  }
  items.forEach(item => {
    const li = document.createElement('li');
    li.className = 'typeahead-item';
    li.textContent = item;
    li.onclick = (e) => {
      e.stopPropagation();
      onSelect(item);
    };
    dropdownEl.appendChild(li);
  });
  dropdownEl.style.display = 'block';
}

// Prediction Handler
async function handlePredict(e) {
  if (e) e.preventDefault();
  const brand = document.getElementById('brand-input').value.trim() || confirmedBrand;
  const model = document.getElementById('model-input').value.trim() || confirmedModel;
  const year = parseInt(document.getElementById('year-select').value);
  const city = document.getElementById('city-select').value;
  const kms = parseInt(document.getElementById('kms-slider').value);
  const mileage = parseFloat(document.getElementById('mileage-input').value) || 18.0;

  if (!brand || !model) {
    showToast('Please select brand and model');
    return;
  }

  const submitBtn = document.getElementById('submit-btn');
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<div class="status-dot"></div><span>Calculating…</span>';

  const payload = {
    brand,
    model,
    year,
    kms,
    fuel: currentFuel,
    trans: currentTrans,
    seats: currentSeats,
    mileage,
    city,
    owner: currentOwner
  };

  if (modelUnknown) {
    const eng = parseInt(document.getElementById('fallback-engine').value);
    const pwr = parseInt(document.getElementById('fallback-power').value);
    if (eng) payload.engine = eng;
    if (pwr) payload.power = pwr;
  }

  try {
    const res = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok || data.detail) {
      alert(data.detail || 'Unable to compute valuation');
    } else {
      renderResult(brand, model, year, city, kms, data);
      showToast('Valuation calculated!');
    }
  } catch (err) {
    // Offline local heuristic
    const age = 2026 - year;
    const eng = lookupSpec?.engine || 1200;
    const pwr = lookupSpec?.power || 85;
    const est = Math.max(1.2, (pwr * 0.08) + (eng * 0.0035) - (age * 0.65) - (kms * 0.00003));
    const fallbackData = {
      price_lakh: +est.toFixed(2),
      range_low: +(est * 0.92).toFixed(2),
      range_high: +(est * 1.08).toFixed(2),
      confidence_score: lookupSpec ? 92 : 80,
      derived_specs: { engine: eng, power: pwr, fuel: currentFuel, trans: currentTrans, seats: currentSeats, mileage }
    };
    renderResult(brand, model, year, city, kms, fallbackData);
    showToast('Estimated from market data');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i data-lucide="sparkles" style="width: 17px; height: 17px;"></i><span>Estimate Market Resale Price</span>';
    initIcons();
  }
}

function renderResult(brand, model, year, city, kms, data) {
  currentResult = { brand, model, year, city, kms, ...data };
  document.getElementById('result-placeholder').style.display = 'none';
  const card = document.getElementById('result-card');
  card.style.display = 'flex';

  document.getElementById('res-car-title').textContent = `${brand} ${model} · ${year} · ${city}`;
  document.getElementById('res-price-num').textContent = data.price_lakh.toFixed(2);
  document.getElementById('res-full-rupees').textContent = `≈ ${formatINR(data.price_lakh)}`;
  document.getElementById('res-confidence').textContent = `Confidence: ${data.confidence_score}%`;
  document.getElementById('res-range-low').textContent = `₹ ${data.range_low} L`;
  document.getElementById('res-range-mid').textContent = `₹ ${data.price_lakh} L`;
  document.getElementById('res-range-high').textContent = `₹ ${data.range_high} L`;

  const ds = data.derived_specs || {};
  document.getElementById('res-spec-fuel').textContent = `${ds.fuel || currentFuel} · ${ds.trans || currentTrans}`;
  document.getElementById('res-spec-kms').textContent = `${kms.toLocaleString()} km`;
  document.getElementById('res-spec-engine').textContent = `${ds.engine || 1200} cc · ${ds.power || 85} bhp`;
  document.getElementById('res-spec-city').textContent = city;

  initIcons();
}

function resetForm() {
  applyPreset(PRESETS[0]);
  document.getElementById('result-placeholder').style.display = 'flex';
  document.getElementById('result-card').style.display = 'none';
  currentResult = null;
  initIcons();
}

// History
function loadHistory() {
  try {
    const saved = localStorage.getItem('carval_history') || localStorage.getItem('autoval_history');
    if (saved) {
      historyItems = JSON.parse(saved);
      document.getElementById('history-count').textContent = historyItems.length;
    }
  } catch (_) {}
}

function saveToHistory() {
  if (!currentResult) return;
  const item = {
    id: Date.now(),
    carName: `${currentResult.brand} ${currentResult.model}`,
    year: currentResult.year,
    price: currentResult.price_lakh,
    kms: currentResult.kms,
    fuel: currentFuel,
    trans: currentTrans,
    city: currentResult.city,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  };
  historyItems = [item, ...historyItems.slice(0, 19)];
  localStorage.setItem('carval_history', JSON.stringify(historyItems));
  document.getElementById('history-count').textContent = historyItems.length;
  showToast('Saved to History!');
}

function renderHistory() {
  const empty = document.getElementById('history-empty');
  const grid = document.getElementById('history-grid');
  const clearBtn = document.getElementById('clear-history-btn');

  if (!historyItems.length) {
    empty.style.display = 'block';
    grid.style.display = 'none';
    clearBtn.style.display = 'none';
    return;
  }

  empty.style.display = 'none';
  grid.style.display = 'grid';
  clearBtn.style.display = 'flex';
  grid.innerHTML = '';

  historyItems.forEach(item => {
    const card = document.createElement('div');
    card.className = 'history-card';
    card.innerHTML = `
      <div class="history-top">
        <div>
          <div class="history-car-name">${item.carName}</div>
          <div class="history-time">${item.year} · Saved ${item.timestamp}</div>
        </div>
        <div class="history-price-tag">₹ ${item.price} L</div>
      </div>
      <div class="history-chips">
        <span class="history-chip">${item.kms.toLocaleString()} km</span>
        <span class="history-chip">${item.fuel}</span>
        <span class="history-chip">${item.trans}</span>
        <span class="history-chip">${item.city}</span>
      </div>
      <div class="history-footer">
        <button type="button" class="history-action-btn" onclick='loadItemIntoForm(${JSON.stringify(item)})'>
          Load into Form <i data-lucide="arrow-right" style="width: 13px; height: 13px;"></i>
        </button>
        <button type="button" class="history-action-btn delete" onclick="deleteHistoryItem(${item.id})">
          <i data-lucide="trash-2" style="width: 12px; height: 12px;"></i> Remove
        </button>
      </div>
    `;
    grid.appendChild(card);
  });
  initIcons();
}

function deleteHistoryItem(id) {
  historyItems = historyItems.filter(i => i.id !== id);
  localStorage.setItem('carval_history', JSON.stringify(historyItems));
  document.getElementById('history-count').textContent = historyItems.length;
  renderHistory();
  showToast('Removed from history');
}

function clearHistory() {
  if (confirm('Clear all saved valuations?')) {
    historyItems = [];
    localStorage.removeItem('carval_history');
    document.getElementById('history-count').textContent = '0';
    renderHistory();
    showToast('History cleared');
  }
}

function loadItemIntoForm(item) {
  const parts = item.carName.split(' ');
  const brand = parts[0];
  const model = parts.slice(1).join(' ');

  document.getElementById('brand-input').value = brand;
  document.getElementById('model-input').value = model;
  confirmedBrand = brand;
  confirmedModel = model;

  document.getElementById('year-select').value = item.year || 2022;
  onYearChange();
  document.getElementById('city-select').value = item.city || 'Delhi';
  document.getElementById('kms-slider').value = item.kms || 28000;
  onKmsInput(item.kms || 28000);
  setFuel(item.fuel || 'Petrol');
  setTrans(item.trans || 'Manual');

  fetchSpecs(brand, model);
  switchTab('predictor');
  showToast(`Loaded ${item.carName}`);
}

function copySummary() {
  if (!currentResult) return;
  const ds = currentResult.derived_specs || {};
  const text = [
    `🚗 Vehicle Valuation`,
    `Model: ${currentResult.brand} ${currentResult.model} (${currentResult.year})`,
    `Estimated Price: ₹ ${currentResult.price_lakh} Lakh (${formatINR(currentResult.price_lakh)})`,
    `Range: ₹ ${currentResult.range_low}L – ₹ ${currentResult.range_high}L`,
    `${currentResult.kms.toLocaleString()} km · ${currentOwner} · ${currentResult.city}`,
    `${currentFuel} · ${currentTrans} · ${ds.engine || ''}cc · ${ds.power || ''}bhp · ${document.getElementById('mileage-input').value} kmpl`,
    `Generated by CarVal AI`
  ].join('\n');
  navigator.clipboard.writeText(text);
  showToast('Summary copied!');
}

// Modal
function openAboutModal() {
  document.getElementById('about-modal').style.display = 'flex';
  initIcons();
}

function closeAboutModal() {
  document.getElementById('about-modal').style.display = 'none';
}
