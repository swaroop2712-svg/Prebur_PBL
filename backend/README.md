# PreBurn Backend API

**PreBurn: A Predictive Early-Warning System for Stubble Burning in North India**

This is the Python FastAPI backend service powering the PreBurn dashboard. It manages administrative districts, NASA FIRMS satellite fire detections, meteorological forecasts, stubble-burning risk predictions, and alert notifications.

---

## 📁 Directory Structure

```text
backend/
├── app/
│   ├── main.py                     # FastAPI application instance, CORS, routers & lifespan
│   ├── config.py                   # Pydantic Settings & environment variable configuration
│   ├── database.py                 # SQLAlchemy engine, session maker, Base, and init_db()
│   ├── models/                     # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── state.py                # States table (Punjab, Haryana)
│   │   ├── district.py             # Districts table with coordinates
│   │   ├── risk_prediction.py      # Stubble burning probability & risk classifications
│   │   ├── fire_detection.py       # Satellite fire points (VIIRS/MODIS, FRP, confidence)
│   │   ├── weather_forecast.py     # 4-day meteorological outlook per district
│   │   └── alert.py                # Early-warning notification inbox & status
│   ├── schemas/                    # Pydantic validation & response schemas
│   │   ├── __init__.py
│   │   ├── geo.py                  # State & District serialization
│   │   ├── analytics.py            # Overview KPI cards & 7-day fire trends
│   │   ├── prediction.py           # Prediction request & response schemas
│   │   ├── fire.py                 # Fire detection items & paginated responses
│   │   ├── weather.py              # 4-day forecast data models
│   │   └── alert.py                # Alert items, unread counters & update models
│   ├── routers/                    # REST API route handlers (/api/v1)
│   │   ├── __init__.py
│   │   ├── geo.py                  # /api/v1/geo/*
│   │   ├── analytics.py            # /api/v1/analytics/*
│   │   ├── predictions.py          # /api/v1/predictions/*
│   │   ├── fires.py                # /api/v1/fires
│   │   ├── weather.py              # /api/v1/weather/*
│   │   └── alerts.py               # /api/v1/alerts/*
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── seed_service.py         # Automatic database seeder for Punjab & Haryana
│   │   └── prediction_service.py   # Temporary demo risk prediction engine
│   └── utils/                      # Helper utilities
│       ├── __init__.py
│       └── helpers.py              # Risk classification & date utilities
├── test_api.py                     # Automated endpoint verification suite
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .env                            # Active environment configuration
└── README.md                       # Documentation and setup guide
```

---

## ⚙️ Prerequisites

- Python 3.10+ (tested on Python 3.13)
- Optional: PostgreSQL 14+ (or use the built-in SQLite development default)

---

## 🚀 Quickstart & Setup Guide

### 1. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
cd "c:\Users\rutuj\OneDrive\Documents\Gauri Project\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Configuration

### Option A: Use PostgreSQL (Recommended for Production)

1. Ensure PostgreSQL is installed and running on your system.
2. Open `psql` or pgAdmin and create the database:
   ```sql
   CREATE DATABASE preburn_db;
   ```
3. Copy `.env.example` to `.env` (if not already done) and set your connection URL:
   ```env
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/preburn_db
   ```

### Option B: Use SQLite (Zero-Setup Local Development)

If you don't have PostgreSQL installed yet, the project includes out-of-the-box SQLite support in `.env`:
```env
DATABASE_URL=sqlite:///./preburn.db
```
The application will automatically create `preburn.db` and initialize all tables and seed records on first launch.

---

## ▶️ Running the Server

From inside the `backend` folder:

```bash
uvicorn app.main:app --reload --port 8000
```

Once running:
- **Interactive API Documentation (Swagger UI)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Alternative Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/geo/states-districts` | Returns full hierarchical tree of states with districts |
| `GET` | `/api/v1/geo/districts` | Returns flat list of districts (supports `?state=Punjab`) |
| `GET` | `/api/v1/analytics/overview-stats` | Returns the 5 core dashboard KPI cards dynamically |
| `GET` | `/api/v1/analytics/fire-trends` | Returns 7-day daily fire counts by state for the bar chart |
| `GET` | `/api/v1/predictions/latest` | Returns latest district risk predictions ordered by probability |
| `POST` | `/api/v1/predictions/predict` | Runs prediction for a district (`district_id`, `horizon_days`) |
| `GET` | `/api/v1/fires` | Paginated fire detections with search and `export_csv=true` |
| `GET` | `/api/v1/weather/{district_id}` | 4-day meteorological outlook for the selected district |
| `GET` | `/api/v1/alerts` | List of notifications with unread counter and read status |
| `PATCH` | `/api/v1/alerts/{id}/read` | Marks a single alert as read |
| `POST` | `/api/v1/alerts/mark-all-read` | Marks all system alerts as read |

---

## 🧪 Running Automated API Tests

To verify that all 11 endpoints and database seeding function correctly:

```bash
python test_api.py
```
