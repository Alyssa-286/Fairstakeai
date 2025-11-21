# FairStake AI — Financial Fairness & Safety Intelligence Platform

**A modular web platform that audits policy bias, analyzes user financial behaviour via SMS, and detects predatory loan/salary anomalies — producing a transparent FairScore and actionable fairness report.**

---

## 🎯 Project Overview

FairStake AI is a unified fintech fairness platform with 4 core modules:

1. **SchemeSense** — Government Scheme Bias Auditor (NLP + PDF Parsing)

   - Upload scheme PDFs → Extract clauses → Detect biased eligibility rules → Highlight exclusion risks → Generate Fairness Score

2. **LoanGuard** — Predatory Loan Clause Detector (OCR + NLP)

   - Upload loan offers → Detect illegal APR, hidden fees, insurance bundling, auto-renew traps → Generate Risk Report

3. **Finance360** — SMS-Based Financial Behaviour Intelligence

   - Paste SMS notifications → Extract UPI spends/income/EMIs → Detect impulsive spending, volatility → Provide nudges → Generate Financial Health Score

4. **FairScore** — Behaviour-Based Credit Scoring (ML + SHAP explainability)
   - Alternative features: spending consistency, savings pattern, UPI cash-flow trends, part-time/gig income, academic stability
   - Output: FairScore (0–100), SHAP Explanation, Score improvement suggestions

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **Git**

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train the FairScore model (first time only)
python app/models/train_fairscore.py

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173` (or the port Vite assigns)

### Production Build

```bash
# Frontend
cd frontend
npm run build
# Output in frontend/dist/

# Backend (use a production ASGI server like gunicorn)
# gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000
```

---

## 📁 Project Structure

```
fairstake/
├── frontend/              # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── modules/      # Module-specific panels
│   │   ├── lib/          # API client, utilities
│   │   ├── data/         # Sample data
│   │   └── types.ts      # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI app entry
│   │   ├── routes/       # API route handlers
│   │   │   ├── schemesense.py
│   │   │   ├── finance360.py
│   │   │   ├── fairscore.py
│   │   │   └── loanguard.py
│   │   ├── utils/        # Core utilities
│   │   │   ├── pdf_text_extractor.py
│   │   │   ├── clause_segmenter.py
│   │   │   ├── nlp_classifier.py
│   │   │   ├── sms_parser.py
│   │   │   └── feature_builder.py
│   │   ├── models/       # ML models
│   │   │   ├── fairscore_model.py
│   │   │   └── train_fairscore.py
│   │   └── explainers/   # SHAP explainability
│   │       └── shap_viz.py
│   └── requirements.txt
│
├── data/                 # Sample data & synthetic datasets
│   ├── synthetic_sms_examples.txt
│   ├── synthetic_fairscore_dataset.csv
│   ├── sample_scheme_texts/
│   ├── sample_loans/
│   └── sample_salary_slips/
│
└── docs/                 # Documentation
    ├── API.md
    └── DEMO_SCRIPT.md
```

---

## 🔌 API Endpoints

### SchemeSense

**POST** `/api/schemesense/upload`

Upload a scheme PDF and get bias analysis.

- **Input**: `multipart/form-data` with `file` (PDF)
- **Output**: JSON with `fairness_score`, `clauses` array, `summary`

### Finance360

**POST** `/api/finance360/sms_parse`

Parse SMS transaction data.

- **Input**: JSON `{ "sms_text": "..." }`
- **Output**: JSON with `transactions`, `monthly_summary`, `financial_health_score`, `nudges`

### FairScore

**POST** `/api/fairscore/score`

Calculate FairScore from user features.

- **Input**: JSON with `user_features` object
- **Output**: JSON with `fairscore`, `explanations`, `improvement_suggestions`

### LoanGuard

**POST** `/api/loanguard/analyze`

Analyze loan document for predatory terms.

- **Input**: `multipart/form-data` with `file` (PDF or text)
- **Output**: JSON with `risk_score`, `risky_clauses`, `summary`

See `docs/API.md` for detailed request/response schemas.

---

## 🧪 Testing with Sample Data

### Sample SMS Data

Use `data/synthetic_sms_examples.txt` — contains realistic SMS transaction dumps.

### Sample Scheme PDFs

Use files in `data/sample_scheme_texts/`:

- `scheme_urban_bias.txt` — Example with urban bias
- `scheme_student_grant.txt` — Student grant scheme
- `scheme_gig_inclusive.txt` — Inclusive gig worker scheme

### Sample Loan Documents

Use files in `data/sample_loans/`:

- `loan_predatory_pack.txt` — Example with predatory terms
- `loan_fair_offer.txt` — Fair loan offer example

### FairScore Dataset

The synthetic dataset at `data/synthetic_fairscore_dataset.csv` contains 1000 rows with features:

- `avg_inflow`, `avg_outflow`, `savings_rate`, `volatility`
- `academic_score`, `part_time_income`, `emi_count`
- `label_score` (target)

---

## 🔒 Privacy & Security

- **In-Memory Processing**: All SMS and PDF data is processed in-memory and not persisted to disk
- **Consent Modal**: Users must consent before uploading sensitive data
- **No Database**: MVP uses no persistent storage for user data
- **Local-Only**: Designed for local/demo use; production should add encryption and minimal retention policies

---

## 🛠️ Development

### Backend Development

```bash
cd backend
# Activate venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dev dependencies (if any)
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Type Checking

```bash
# Frontend
cd frontend
npm run build  # Runs TypeScript compiler

# Backend (optional)
pip install mypy
mypy app/
```

---

## 📊 Demo Flow (2–3 minutes)

1. **Open app** → Show module tabs (10s)
2. **Finance360** → Paste sample SMS → Show parsed transactions + Health Score + nudges (40s)
3. **FairScore** → Pre-fill features → Run → Show FairScore + SHAP (30s)
4. **SchemeSense** → Upload simple scheme text PDF → Show clause highlights & fairness score (30s)
5. **LoanGuard** → Upload sample loan text → Show predatory highlights (20s)
6. **Show combined "Fairness Report" download** (10s)

See `docs/DEMO_SCRIPT.md` for detailed demo script.

---

## 🎯 MVP Acceptance Criteria

✅ User can paste SMS text and get parsed transactions + Financial Health Score  
✅ User can upload a simple text-based scheme PDF and get clause highlights + fairness score  
✅ User can input structured feature JSON to `/api/fairscore/score` and receive fairscore with top 3 explanations  
✅ User can upload a simple loan text and get highlighted risky clauses  
✅ All results displayed in frontend with clear demo data buttons  
✅ Basic README with run instructions

---

## 🚧 Known Limitations & Future Work

- **OCR**: Currently supports text PDFs only; scanned PDFs require OCR (Tesseract) — optional stretch
- **BERT Classifier**: Falls back to keyword rules if GPU/BERT unavailable
- **SMS Parsing**: Some formats may not parse; unparsed lines listed for manual inspection
- **Model Training**: FairScore model uses synthetic data; production should use real labeled data
- **Production**: Add authentication, rate limiting, proper error handling, database for persistence

---

## 📝 License

This project is built for hackathon/demo purposes.

---

## 👥 Team

Built for hackathon demo in 8–10 hours with modular architecture for easy collaboration.

---

## 🙏 Acknowledgments

- FastAPI for the backend framework
- React + Vite for the frontend
- HuggingFace Transformers for NLP capabilities
- XGBoost + SHAP for ML explainability
- TailwindCSS for styling
