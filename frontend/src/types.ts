export interface Clause {
  id: number
  text: string
  label: string
  confidence: number
  suggestion: string
}

export interface SchemeSenseResult {
  fairness_score: number
  clauses: Clause[]
  summary: string
}

export interface FinanceTransaction {
  date: string
  amount: number
  direction: 'credit' | 'debit'
  ref: string
  bank: string
  raw: string
}

export interface Finance360Result {
  transactions: FinanceTransaction[]
  monthly_summary: {
    inflow: number
    outflow: number
    volatility: number
  }
  financial_health_score: number
  nudges: string[]
  unparsed_transactions: string[]
  derived_features: Record<string, number>
}

export interface FairScoreResult {
  fairscore: number
  explanations: { feature: string; contribution: number }[]
  improvement_suggestions: string[]
}

export interface LoanClause {
  text: string
  type: string
  recommendation: string
}

export interface LoanGuardResult {
  risk_score: number
  risky_clauses: LoanClause[]
  summary: string
}


