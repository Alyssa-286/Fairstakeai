# FairStake AI — API Documentation

This document describes all API endpoints for the FairStake AI platform.

**Base URL**: `http://localhost:8000` (development)

---

## Health & Privacy

### GET `/health`

Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET `/privacy`

Privacy policy information.

**Response**:
```json
{
  "message": "FairStake AI processes all data in-memory. No user data is persisted to disk.",
  "data_retention": "none",
  "processing": "local_only"
}
```

---

## SchemeSense — Scheme Bias Auditor

### POST `/api/schemesense/upload`

Upload a scheme PDF and analyze for bias clauses.

**Request**:
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (file): PDF file containing scheme text

**Response**:
```json
{
  "fairness_score": 61,
  "clauses": [
    {
      "id": 1,
      "text": "Applicant must have 6 months salary slips",
      "label": "exclusion_income",
      "confidence": 0.87,
      "suggestion": "Allow alternatives: bank inflows, gig platform statements, school stipend receipts."
    },
    {
      "id": 2,
      "text": "Only urban residents eligible",
      "label": "geographic_bias",
      "confidence": 0.92,
      "suggestion": "Extend eligibility to rural and semi-urban applicants with equivalent documentation."
    }
  ],
  "summary": "Income verification clauses favor salaried individuals; consider alternative documentation options for students/gig workers."
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid file or parsing error
- `500`: Server error

---

## Finance360 — SMS Financial Analysis

### POST `/api/finance360/sms_parse`

Parse SMS transaction notifications and generate financial insights.

**Request**:
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "sms_text": "Rs.150.00 debited A/cXX6597 and credited to Vedamurthy M S via UPI Ref No 108589157513 on 17Nov25. Call 18001031906, if not done by you. -BOI\nRs.5000.00 credited to A/cXX6597 on 20Nov25. -BOI"
}
```

**Response**:
```json
{
  "transactions": [
    {
      "date": "2025-11-17",
      "type": "upi_debit",
      "amount": 150.00,
      "merchant": "Vedamurthy M S",
      "raw": "Rs.150.00 debited A/cXX6597 and credited to Vedamurthy M S via UPI Ref No 108589157513 on 17Nov25. Call 18001031906, if not done by you. -BOI"
    },
    {
      "date": "2025-11-20",
      "type": "bank_credit",
      "amount": 5000.00,
      "merchant": null,
      "raw": "Rs.5000.00 credited to A/cXX6597 on 20Nov25. -BOI"
    }
  ],
  "monthly_summary": {
    "inflow": 12000,
    "outflow": 9500,
    "volatility": 0.32
  },
  "financial_health_score": 72,
  "nudges": [
    "Reduce impulsive spends: shoe purchases this month contributed 12% to discretionary outflow"
  ],
  "unparsed_transactions": []
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid input
- `500`: Server error

---

## FairScore — Behaviour-Based Credit Scoring

### POST `/api/fairscore/score`

Calculate FairScore from user financial and academic features.

**Request**:
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "user_features": {
    "avg_monthly_inflow": 12000,
    "avg_monthly_outflow": 9000,
    "savings_rate": 0.15,
    "volatility": 0.22,
    "part_time_income": 3000,
    "academic_score": 8.5,
    "emi_count": 0
  }
}
```

**Response**:
```json
{
  "fairscore": 68,
  "explanations": [
    {
      "feature": "savings_rate",
      "contribution": 8,
      "description": "Strong savings pattern increases score"
    },
    {
      "feature": "volatility",
      "contribution": -6,
      "description": "Moderate spending volatility slightly reduces score"
    },
    {
      "feature": "academic_score",
      "contribution": 5,
      "description": "Good academic performance positively impacts score"
    }
  ],
  "improvement_suggestions": [
    "Save ₹500/month increases score by ~4 points",
    "Reduce spending volatility by 10% could add 3 points"
  ]
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid features
- `500`: Model loading or prediction error

---

## LoanGuard — Predatory Loan Detector

### POST `/api/loanguard/analyze`

Analyze loan document for predatory terms and risks.

**Request**:
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file` (file): PDF or text file containing loan offer

**Response**:
```json
{
  "risk_score": 80,
  "risky_clauses": [
    {
      "text": "This loan auto-renews unless cancelled 30 days before expiry",
      "type": "auto_renew",
      "severity": "high",
      "recommendation": "Clarify opt-out and pre-notice period. Ensure easy cancellation process."
    },
    {
      "text": "Processing fee of ₹5000 (non-refundable) applies",
      "type": "hidden_fees",
      "severity": "medium",
      "recommendation": "Request breakdown of all fees upfront. Verify if processing fee is standard or excessive."
    },
    {
      "text": "APR: 48% per annum",
      "type": "high_apr",
      "severity": "critical",
      "recommendation": "APR exceeds regulatory limits. Consider alternative lenders or negotiate terms."
    }
  ],
  "summary": "High risk due to auto-renew clause, hidden processing fees, and excessive APR. Review terms carefully before signing."
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid file or parsing error
- `500`: Server error

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description",
  "detail": "Additional error details (optional)"
}
```

**Common Status Codes**:
- `400 Bad Request`: Invalid input or missing required fields
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server-side error
- `503 Service Unavailable`: Service temporarily unavailable (e.g., model not loaded)

---

## Rate Limiting

Currently, no rate limiting is implemented for MVP. Production should add rate limiting per IP/user.

---

## Authentication

Currently, no authentication is required for MVP. Production should add API keys or OAuth2.

---

## CORS

The API allows CORS from `http://localhost:5173` (Vite default) for development. Production should configure allowed origins appropriately.



