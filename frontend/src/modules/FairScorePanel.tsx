import { useState } from 'react'
import { ScoreBadge } from '../components/ScoreBadge'
import { SectionCard } from '../components/SectionCard'
import { sampleFairScoreFeatures } from '../data/samples'
import { postJson } from '../lib/api'
import type { FairScoreResult } from '../types'

const featureFields: { key: keyof typeof sampleFairScoreFeatures; label: string; step?: number }[] = [
  { key: 'avg_monthly_inflow', label: 'Avg monthly inflow (₹)', step: 500 },
  { key: 'avg_monthly_outflow', label: 'Avg monthly outflow (₹)', step: 500 },
  { key: 'savings_rate', label: 'Savings rate', step: 0.01 },
  { key: 'volatility', label: 'Volatility', step: 0.01 },
  { key: 'part_time_income', label: 'Part-time income (₹)', step: 500 },
  { key: 'academic_score', label: 'Academic score', step: 0.1 },
  { key: 'emi_count', label: 'EMI count', step: 1 },
]

export const FairScorePanel = () => {
  const [features, setFeatures] = useState(sampleFairScoreFeatures)
  const [result, setResult] = useState<FairScoreResult | null>(null)
  const [status, setStatus] = useState<{ loading: boolean; error?: string }>({ loading: false })

  const handleSubmit = async () => {
    setStatus({ loading: true })
    try {
      const data = await postJson<FairScoreResult>('/api/fairscore/score', { user_features: features })
      setResult(data)
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Scoring failed' })
    }
  }

  const handleFieldChange = (key: keyof typeof sampleFairScoreFeatures, value: string) => {
    const numericValue = Number(value)
    setFeatures((prev) => ({ ...prev, [key]: isNaN(numericValue) ? 0 : numericValue }))
  }

  return (
    <div className="space-y-6">
      <SectionCard
        title="Behavioural feature inputs"
        description="Seed the scorer with Finance360 derived features or tweak manually."
        actions={
          <button
            className="rounded-full border border-brand-500 px-4 py-2 text-sm font-semibold text-brand-600 hover:bg-brand-50"
            onClick={() => setFeatures(sampleFairScoreFeatures)}
          >
            Reset sample
          </button>
        }
      >
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {featureFields.map((field) => (
            <label key={field.key} className="text-sm font-semibold text-slate-600">
              {field.label}
              <input
                type="number"
                step={field.step ?? 0.01}
                value={features[field.key]}
                onChange={(event) => handleFieldChange(field.key, event.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-200 bg-white p-3 text-sm text-slate-800"
              />
            </label>
          ))}
        </div>
        {status.error && <p className="text-sm text-rose-600">{status.error}</p>}
        <button
          onClick={handleSubmit}
          disabled={status.loading}
          className="rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
        >
          {status.loading ? 'Scoring...' : 'Generate FairScore'}
        </button>
      </SectionCard>

      {result && (
        <SectionCard title="FairScore insights">
          <ScoreBadge label="FairScore" value={result.fairscore} variant={result.fairscore > 70 ? 'success' : 'warning'} />
          <div>
            <h4 className="text-sm font-semibold text-slate-700">Top drivers</h4>
            <ul className="mt-2 space-y-2 text-sm text-slate-600">
              {result.explanations.map((item) => (
                <li key={item.feature} className="flex items-center justify-between rounded-xl bg-slate-50 px-4 py-2">
                  <span className="capitalize">{item.feature.replaceAll('_', ' ')}</span>
                  <span className={item.contribution >= 0 ? 'text-emerald-600' : 'text-rose-600'}>
                    {item.contribution >= 0 ? '+' : ''}
                    {item.contribution}
                  </span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-700">Improvement suggestions</h4>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
              {result.improvement_suggestions.map((suggestion) => (
                <li key={suggestion}>{suggestion}</li>
              ))}
            </ul>
          </div>
        </SectionCard>
      )}
    </div>
  )
}


