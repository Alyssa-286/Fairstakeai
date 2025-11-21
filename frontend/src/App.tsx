import { useState } from 'react'
import { Finance360Panel } from './modules/Finance360Panel'
import { FairScorePanel } from './modules/FairScorePanel'
import { SchemeSensePanel } from './modules/SchemeSensePanel'
import { LoanGuardPanel } from './modules/LoanGuardPanel'
import { ClearClausePanel } from './modules/ClearClausePanel'

const tabs = [
  {
    id: 'schemesense',
    label: 'SchemeSense',
    description: 'Audit government schemes for exclusionary clauses.',
    component: <SchemeSensePanel />,
  },
  {
    id: 'finance360',
    label: 'Finance360',
    description: 'Parse SMS spending behaviour for financial health.',
    component: <Finance360Panel />,
  },
  {
    id: 'fairscore',
    label: 'FairScore',
    description: 'Behaviour-based scoring with SHAP transparency.',
    component: <FairScorePanel />,
  },
  {
    id: 'loanguard',
    label: 'LoanGuard',
    description: 'Highlight predatory loan clauses instantly.',
    component: <LoanGuardPanel />,
  },
  {
    id: 'clearclause',
    label: 'ClearClause',
    description: 'Legal document Q&A, summarization & translation.',
    component: <ClearClausePanel />,
  },
]

function App() {
  const [activeTab, setActiveTab] = useState(tabs[0].id)
  const active = tabs.find((tab) => tab.id === activeTab) ?? tabs[0]

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-brand-500">FairStake AI</p>
            <h1 className="text-2xl font-bold text-slate-900">Financial Fairness & Safety Intelligence</h1>
            <p className="text-sm text-slate-500">
              Audits schemes, analyses SMS cashflows, computes FairScore, and flags predatory loan clauses.
            </p>
          </div>
          <div className="rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white">
            In-memory demo · privacy-first
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-8 lg:flex-row">
        <aside className="w-full rounded-3xl border border-slate-200 bg-white p-4 lg:w-64">
          <nav className="space-y-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full rounded-2xl px-4 py-3 text-left text-sm font-semibold ${
                  activeTab === tab.id
                    ? 'bg-brand-500 text-white shadow-lg'
                    : 'bg-slate-50 text-slate-600 hover:bg-slate-100'
                }`}
              >
                <span className="block text-base">{tab.label}</span>
                <span
                  className={`text-xs font-normal ${
                    activeTab === tab.id ? 'text-white/80' : 'text-slate-500'
                  }`}
                >
                  {tab.description}
                </span>
              </button>
            ))}
          </nav>
          <div className="mt-6 rounded-2xl bg-slate-900 p-4 text-xs text-slate-100">
            <p className="font-semibold">Demo script</p>
            <ol className="mt-2 list-decimal space-y-1 pl-4">
              <li>Finance360 → paste sample SMS.</li>
              <li>FairScore → run with derived features.</li>
              <li>SchemeSense → upload sample scheme.</li>
              <li>LoanGuard → upload loan text.</li>
              <li>ClearClause → upload docs, Q&A, translate.</li>
            </ol>
          </div>
        </aside>

        <main className="flex-1">{active.component}</main>
      </div>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-6 text-xs text-slate-500 md:flex-row md:justify-between">
          <p>Uploads & SMS are processed locally and discarded after response generation.</p>
          <p>Need OCR or extended models? Marked as stretch goals.</p>
        </div>
      </footer>
    </div>
  )
}

export default App


