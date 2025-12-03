# Salem Portfolio Analysis - React + FastAPI Migration

**Modern Institutional-Grade Portfolio Analysis Platform**

This project has been migrated from a Streamlit-based application to a professional React + FastAPI architecture, suitable for enterprise wealth management platforms.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (TypeScript)               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │    Inputs    │  │   Scenarios  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        API Client (Axios) + State Management         │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────────┐
│               FastAPI Backend (Python)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Routers: /simulation, /presets, /health        │  │
│  └────────────────┬─────────────────────────────────────┘  │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │     Pydantic Models (Request/Response Validation)    │  │
│  └────────────────┬─────────────────────────────────────┘  │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │    Core Simulation Engine (Pure Python Logic)       │  │
│  │  - Monte Carlo Simulation                            │  │
│  │  - Goal Probability Calculations                     │  │
│  │  - Sensitivity Analysis                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
portfolio-monte-carlo-app/
├── backend/                    # FastAPI Backend
│   ├── api/                   # API route handlers
│   │   ├── simulation.py     # Monte Carlo endpoints
│   │   ├── presets.py        # Assumption presets
│   │   └── health.py         # Health checks
│   ├── core/                  # Pure Python business logic
│   │   └── simulation.py     # Monte Carlo engine (NO UI deps)
│   ├── models/                # Pydantic data models
│   │   └── schemas.py        # Request/Response schemas
│   ├── tests/                 # Backend tests
│   │   └── test_api.py       # API endpoint tests
│   ├── main.py               # FastAPI app entry point
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   └── layout/      # AppHeader, Sidebar, Layout
│   │   ├── pages/           # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── InputsPage.tsx
│   │   │   ├── ScenariosPage.tsx
│   │   │   └── ReportsPage.tsx
│   │   ├── lib/             # Utilities
│   │   │   └── api.ts       # API client layer
│   │   ├── types/           # TypeScript interfaces
│   │   │   └── index.ts
│   │   ├── App.tsx          # Main app component
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Global styles + Tailwind
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── app.py                     # (Legacy Streamlit - deprecated)
├── README.md                  # This file
└── MIGRATION.md              # Migration documentation
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and npm/yarn
- **Git**

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server**:
   ```bash
   # Development mode with auto-reload
   python main.py

   # Or using uvicorn directly
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Verify backend is running**:
   - API docs: http://localhost:8000/api/docs
   - Health check: http://localhost:8000/api/health

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open in browser**:
   - Frontend: http://localhost:3000
   - Auto-proxies API requests to backend

## 🧪 Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📚 API Documentation

### Key Endpoints

#### Health & Status
- `GET /api/health` - Health check
- `GET /api/status` - Detailed system status

#### Simulations
- `POST /api/simulation/run` - Run Monte Carlo simulation
- `POST /api/simulation/validate` - Validate inputs
- `POST /api/simulation/sensitivity` - Run sensitivity analysis

#### Presets
- `GET /api/presets/` - List all assumption presets
- `GET /api/presets/{name}` - Get specific preset

### Example API Call

```typescript
// TypeScript/React example
import apiClient from './lib/api';

const runSimulation = async () => {
  const request = {
    client_info: {
      client_name: "John Doe",
      advisor_name: "Jane Smith"
    },
    inputs: {
      starting_portfolio: 2000000,
      years_to_model: 30,
      current_age: 55,
      horizon_age: 85,
      monthly_spending: -8000,
      equity_pct: 0.6,
      fi_pct: 0.3,
      cash_pct: 0.1,
      // ... other parameters
    }
  };

  const result = await apiClient.runSimulation(request);
  console.log('Success probability:', result.metrics.success_probability);
};
```

```python
# Python example
import requests

response = requests.post('http://localhost:8000/api/simulation/run', json={
    "client_info": {
        "client_name": "John Doe",
        "advisor_name": "Jane Smith"
    },
    "inputs": {
        "starting_portfolio": 2000000,
        "years_to_model": 30,
        "current_age": 55,
        "horizon_age": 85,
        "monthly_spending": -8000,
        "equity_pct": 0.6,
        "fi_pct": 0.3,
        "cash_pct": 0.1,
        "n_scenarios": 200
    }
})

data = response.json()
print(f"Success probability: {data['metrics']['success_probability']:.1%}")
```

## 🎨 Design System

### Color Palette

The application uses Salem Investment Counselors' institutional dark mode design system:

```typescript
// Primary Colors
primary-600: '#0F3B63'  // Salem Navy Deep
primary-500: '#1F4F7C'  // Salem Navy
primary-300: '#7AA6C4'  // Salem Blue Light

// Brand
brand-gold: '#B49759'   // Salem Gold

// Surfaces (Dark Mode)
surface-900: '#0C0E12'  // Background
surface-800: '#12141A'  // Card Background
surface-700: '#1A1D24'  // Input Background
surface-600: '#262A33'  // Border

// Text
text-primary: '#E6E8EC'    // Primary text
text-secondary: '#9AA0A6'  // Secondary text
text-muted: '#6F767D'      // Muted text

// Status
success: '#4CAF50'
warning: '#FFC107'
danger: '#D9534F'
```

### Typography

- **Font Family**: Inter (body), Nunito Sans (headings)
- **Font Weights**: 300, 400, 500, 600, 700, 800

### Component Classes

```css
/* Tailwind utility classes */
.card          // Card container with dark background
.btn-primary   // Primary action button (gold)
.btn-secondary // Secondary button (dark)
.input         // Form input styling
.label         // Form label styling
```

## 🔄 Migration Notes

### What Changed

1. **UI Layer**: Streamlit → React + TypeScript
2. **Backend**: Embedded logic → FastAPI REST API
3. **Styling**: Streamlit CSS → Tailwind CSS + Custom Design System
4. **State Management**: Streamlit session state → React hooks/Zustand
5. **Data Validation**: Streamlit inputs → Pydantic models

### What Stayed the Same

✅ **All Monte Carlo simulation logic** - Preserved exactly
✅ **Financial calculations** - No changes to core algorithms
✅ **Assumption presets** - Same CFP Board, Morningstar, etc.
✅ **Input validation rules** - Same business rules
✅ **Return/volatility models** - Identical computation

### Key Benefits

- **Professional UI**: Modern, responsive, institutional-grade design
- **API-First**: Can integrate with other systems
- **Better Performance**: Optimized React rendering, API caching
- **Testing**: Comprehensive test coverage for API endpoints
- **Maintainability**: Clear separation of concerns
- **Scalability**: Can deploy frontend and backend independently

## 🚢 Deployment

### Backend Deployment

```bash
# Using Docker
docker build -t salem-portfolio-api ./backend
docker run -p 8000:8000 salem-portfolio-api

# Using Gunicorn (production)
gunicorn backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

```bash
# Build for production
cd frontend
npm run build

# Serve static files
npm run preview

# Or deploy to Vercel, Netlify, AWS S3, etc.
```

## 🛠️ Development Workflow

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend && python main.py
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd frontend && npm run dev
   ```

3. **Open Browser**: http://localhost:3000

4. **Make Changes**:
   - Backend changes auto-reload (FastAPI reload mode)
   - Frontend changes hot-reload (Vite HMR)

## 📖 Additional Documentation

- **API Documentation**: http://localhost:8000/api/docs (when backend is running)
- **Component Storybook**: (Coming soon)
- **Architecture Decision Records**: See `/docs/architecture/`

## 🤝 Contributing

1. Backend changes: Update `backend/` and add tests in `backend/tests/`
2. Frontend changes: Update `frontend/src/` and maintain type safety
3. Run tests before committing
4. Follow existing code style (FastAPI, React best practices)

## 📝 License

Proprietary - Salem Investment Counselors

## 👥 Team

- **Original Streamlit App**: [Previous developers]
- **React Migration**: [Migration team]
- **Maintained by**: Salem Investment Counselors Technology Team

---

**Note**: The legacy Streamlit `app.py` is still present but deprecated. Use the new React + FastAPI stack for all new development.
