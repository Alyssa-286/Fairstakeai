# FairStake AI — Demo Script (2–3 minutes)

This script guides you through a complete demo of all 4 FairStake AI modules.

---

## Pre-Demo Setup

1. **Start Backend**:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or: source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   python app/models/train_fairscore.py  # First time only
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Open Browser**: Navigate to `http://localhost:5173` (or the port Vite assigns)

---

## Demo Flow

### 1. Introduction (10 seconds)

**Say**: "FairStake AI is a unified platform that audits financial fairness across four dimensions. Let me show you each module."

**Action**: Point to the 4 tabs at the top:
- SchemeSense
- Finance360
- FairScore
- LoanGuard

---

### 2. Finance360 — SMS Financial Analysis (40 seconds)

**Say**: "First, let's analyze financial behavior from SMS transaction data. This is especially useful for students and gig workers who may not have traditional credit history."

**Actions**:
1. Click **Finance360** tab
2. Click **"Load Sample SMS Data"** button (or paste from `data/synthetic_sms_examples.txt`)
3. Check the **consent checkbox**
4. Click **"Analyze SMS"**

**Show**:
- Parsed transactions table (dates, amounts, types)
- **Financial Health Score** badge (e.g., 72/100)
- Monthly summary (inflow, outflow, volatility)
- **Nudges** section (actionable insights)
- Transaction trend chart (if visible)

**Say**: "Notice how we extract UPI transactions, bank credits, and EMIs. The system identifies spending patterns and provides personalized nudges."

---

### 3. FairScore — Behaviour-Based Credit Scoring (30 seconds)

**Say**: "Now let's calculate a FairScore using alternative features that don't rely on traditional credit history."

**Actions**:
1. Click **FairScore** tab
2. Click **"Load Sample Features"** (or manually enter values)
3. Click **"Calculate FairScore"**

**Show**:
- **FairScore** badge (e.g., 68/100)
- **Top 3 Explanations** (SHAP-style feature contributions)
  - "savings_rate: +8 points"
  - "volatility: -6 points"
  - "academic_score: +5 points"
- **Improvement Suggestions** list

**Say**: "The FairScore uses spending consistency, savings patterns, academic performance, and part-time income. Each factor is explained transparently, so users know how to improve their score."

---

### 4. SchemeSense — Scheme Bias Auditor (30 seconds)

**Say**: "Let's audit a government scheme for potential bias that might exclude certain groups."

**Actions**:
1. Click **SchemeSense** tab
2. Click **"Load Sample Scheme"** (or upload from `data/sample_scheme_texts/scheme_urban_bias.txt`)
3. Check **consent checkbox**
4. Click **"Analyze Scheme"**

**Show**:
- **Fairness Score** badge (e.g., 61/100)
- **Clause Highlights** list:
  - Each clause with label (e.g., "exclusion_income", "geographic_bias")
  - Confidence score
  - **Suggestion** for rewriting the clause
- **Summary** paragraph

**Say**: "We identify clauses that favor salaried individuals, urban residents, or specific demographics. Each biased clause gets a rewrite suggestion to make the scheme more inclusive."

---

### 5. LoanGuard — Predatory Loan Detector (20 seconds)

**Say**: "Finally, let's check a loan offer for predatory terms like hidden fees, auto-renewal traps, or excessive APR."

**Actions**:
1. Click **LoanGuard** tab
2. Click **"Load Sample Loan"** (or upload from `data/sample_loans/loan_predatory_pack.txt`)
3. Check **consent checkbox**
4. Click **"Analyze Loan"**

**Show**:
- **Risk Score** badge (e.g., 80/100 — high risk)
- **Risky Clauses** list:
  - Clause text
  - Risk type (auto_renew, hidden_fees, high_apr, etc.)
  - Severity (critical, high, medium)
  - **Recommendation** for each clause
- **Summary** paragraph

**Say**: "LoanGuard flags auto-renewal clauses, hidden processing fees, and APR that exceeds regulatory limits. Each risk comes with a clear recommendation."

---

### 6. Combined Report (10 seconds)

**Say**: "Users can download a combined Fairness Report that includes all four analyses — giving a complete picture of financial fairness."

**Action**: (If implemented) Show download button or mention it's available in production.

---

## Key Talking Points

### Privacy & Security
- **Mention**: "All data is processed in-memory. We don't store SMS or PDF data. Users must consent before analysis."

### Use Cases
- **Students**: FairScore using academic performance + part-time income
- **Gig Workers**: Finance360 for transaction-based credit assessment
- **Policy Makers**: SchemeSense to audit scheme inclusivity
- **Borrowers**: LoanGuard to avoid predatory loans

### Technical Highlights
- **NLP**: Clause segmentation and bias detection
- **ML**: XGBoost model with SHAP explainability
- **Regex Parsing**: Robust SMS transaction extraction
- **Modular Architecture**: Each module is independent and reusable

---

## Troubleshooting

### Backend Not Starting
- Check Python version: `python --version` (should be 3.11+)
- Ensure virtual environment is activated
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is not in use

### Frontend Not Starting
- Check Node.js version: `node --version` (should be 18+)
- Install dependencies: `npm install`
- Check if port 5173 is available (Vite will use next available)

### API Errors
- Check backend is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/app/main.py`
- Check browser console for CORS errors

### Model Not Found
- Run training script: `python backend/app/models/train_fairscore.py`
- Check `backend/app/models/fairscore_model.pkl` exists

---

## Sample Data Locations

- **SMS**: `data/synthetic_sms_examples.txt`
- **Schemes**: `data/sample_scheme_texts/*.txt`
- **Loans**: `data/sample_loans/*.txt`
- **FairScore Dataset**: `data/synthetic_fairscore_dataset.csv`

---

## Post-Demo Q&A

**Q: How accurate is the FairScore model?**  
A: The MVP uses synthetic data. Production would require real labeled data and validation.

**Q: Can it handle scanned PDFs?**  
A: Currently supports text PDFs. OCR (Tesseract) can be added for scanned documents.

**Q: Is this production-ready?**  
A: This is an MVP for hackathon demo. Production would need authentication, rate limiting, database, and real model training.

**Q: How do you ensure privacy?**  
A: All processing is in-memory. No data is persisted. Production should add encryption and minimal retention policies.

---

## Demo Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Sample data files accessible
- [ ] All 4 modules functional
- [ ] Consent modals working
- [ ] Results displaying correctly
- [ ] Charts rendering (if applicable)
- [ ] No console errors

---

**Total Demo Time**: ~2–3 minutes  
**Target Audience**: Hackathon judges, investors, potential users

