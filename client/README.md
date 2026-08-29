# AutoVal AI — Frontend Client

The frontend for **AutoVal AI**, a modern, high-performance used vehicle price prediction web application built with **React 19**, **Vite**, and an automotive-inspired **Obsidian Charcoal & Warm Gold** design system.

---

## 🌟 Key Features

- **Live Split Type-Ahead Search**: High-responsiveness debounced autosuggest for 34 car brands and 276 vehicle models.
- **Intelligent Powertrain Auto-Fill**: Automatically resolves engine displacement, horsepower, fuel efficiency, and transmission profiles in real-time.
- **Selective User Input Controls**: Intuitive pill buttons and sliders for fuel type, transmission, seating capacity, kilometers driven, and city of registration.
- **Fallback Engine Override**: Gracefully exposes manual powertrain inputs only when an unlisted or custom vehicle model is detected.
- **Instant Fair Market Spread**: Computes quick-sale, fair market value, and dealer retail estimates with confidence weighting.
- **Client-Side Valuation History**: Persists estimated vehicles to browser `localStorage` with quick reload and export capabilities.
- **Methodology & Model Modal**: Plain-English, transparent explanation of the underlying machine learning model and dataset metrics.

---

## 🛠️ Tech Stack

- **Framework**: [React 19](https://react.dev/)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **Design System**: Vanilla CSS with custom HSL/HEX design tokens (Charcoal `#0E1013` & Warm Gold `#D4A24C`)

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn

### Installation
```bash
# Install dependencies
npm install

# Start local development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🌐 Environment Variables

Create a `.env.local` or `.env.production` file in this directory:

```env
# Backend API Base URL
VITE_API_URL=http://localhost:8000
```

For production on Vercel:
```env
VITE_API_URL=https://carval-qaph.onrender.com
```

---

## 📦 Project Structure

```
client/
├── public/              # Static assets & favicons
├── src/
│   ├── App.jsx          # Main application component & state logic
│   ├── index.css        # Core design tokens, theme styles & responsive layout
│   └── main.jsx         # React application entry point
├── package.json         # Dependencies and build scripts
├── vercel.json          # SPA routing rewrite rules for Vercel
└── vite.config.js       # Vite configuration & React plugins
```
