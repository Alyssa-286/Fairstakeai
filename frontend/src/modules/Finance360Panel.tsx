import { useMemo, useState } from 'react'
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { ConsentModal } from '../components/ConsentModal'
import { ScoreBadge } from '../components/ScoreBadge'
import { SectionCard } from '../components/SectionCard'
import { TransactionsTable } from '../components/TransactionsTable'
import { sampleSMSDump } from '../data/samples'
import { postJson } from '../lib/api'
import type { Finance360Result } from '../types'

export const Finance360Panel = () => {
  const [smsText, setSmsText] = useState('')
  const [result, setResult] = useState<Finance360Result | null>(null)
  const [status, setStatus] = useState<{ loading: boolean; error?: string }>({ loading: false })
  const [consentGiven, setConsentGiven] = useState(false)
  const [showConsent, setShowConsent] = useState(false)

  const transactionTrend = useMemo(() => {
    if (!result) return []
    return result.transactions.map((txn) => ({
      date: txn.date,
      amount: txn.direction === 'credit' ? txn.amount : -txn.amount,
    }))
  }, [result])

  const processSMS = async () => {
    if (!smsText.trim()) {
      setStatus({ loading: false, error: 'Paste SMS alerts to analyze.' })
      return
    }
    setStatus({ loading: true })
    try {
      const data = await postJson<Finance360Result>('/api/finance360/sms_parse', { sms_text: smsText })
      setResult(data)
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Parsing failed' })
    }
  }

  const handleProcessClick = () => {
    if (!consentGiven) {
      setShowConsent(true)
      return
    }
    processSMS()
  }

  const handleConsentAccept = () => {
    setConsentGiven(true)
    setShowConsent(false)
    processSMS()
  }

  return (
    <>
      <ConsentModal open={showConsent} onAccept={handleConsentAccept} onDecline={() => setShowConsent(false)} />
      <div className="space-y-6">
        <SectionCard
          title="Paste SMS notifications"
          description="We redact SMS on the client and process them in-memory."
          actions={
            <button
              className="rounded-full border border-brand-500 px-4 py-2 text-sm font-semibold text-brand-600 hover:bg-brand-50"
              onClick={() => setSmsText(sampleSMSDump)}
            >
              Load sample SMS
            </button>
          }
        >
          <textarea
            value={smsText}
            onChange={(event) => setSmsText(event.target.value)}
            rows={8}
            className="w-full rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-800"
            placeholder="Paste SMS alerts here..."
          />
          {status.error && <p className="text-sm text-rose-600">{status.error}</p>}
          <div className="flex items-center gap-4">
            <button
              onClick={handleProcessClick}
              disabled={status.loading}
              className="rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
            >
              {status.loading ? 'Processing...' : 'Analyze SMS'}
            </button>
            <label className="flex items-center gap-2 text-xs text-slate-500">
              <input
                type="checkbox"
                checked={consentGiven}
                onChange={(event) => setConsentGiven(event.target.checked)}
                className="rounded border-slate-300 text-brand-500 focus:ring-brand-500"
              />
              I consent to in-memory analysis for this demo.
            </label>
          </div>
        </SectionCard>

        {result && (
          <>
            <SectionCard title="Financial health overview">
              <div className="flex flex-wrap gap-4">
                <ScoreBadge
                  label="Health score"
                  value={result.financial_health_score}
                  variant={result.financial_health_score > 70 ? 'success' : 'warning'}
                />
                <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-600">
                  Monthly inflow ₹{result.monthly_summary.inflow} | outflow ₹{result.monthly_summary.outflow} | volatility{' '}
                  {result.monthly_summary.volatility}
                </div>
              </div>
              <div className="mt-4 h-64 w-full">
                <ResponsiveContainer>
                  <AreaChart data={transactionTrend}>
                    <defs>
                      <linearGradient id="trend" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2b72ff" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#2b72ff" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="amount" stroke="#2b72ff" fillOpacity={1} fill="url(#trend)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-slate-700">Improvement nudges</h4>
                <ul className="list-disc space-y-1 pl-5 text-sm text-slate-600">
                  {result.nudges.map((nudge) => (
                    <li key={nudge}>{nudge}</li>
                  ))}
                </ul>
              </div>
            </SectionCard>

            <SectionCard title="Parsed transactions">
              <TransactionsTable transactions={result.transactions} />
              {result.unparsed_transactions.length > 0 && (
                <div className="rounded-2xl border border-dashed border-amber-300 bg-amber-50 p-4 text-xs text-amber-800">
                  Unparsed lines:
                  <ul className="list-disc pl-4">
                    {result.unparsed_transactions.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </div>
              )}
            </SectionCard>
          </>
        )}
      </div>
    </>
  )
}


