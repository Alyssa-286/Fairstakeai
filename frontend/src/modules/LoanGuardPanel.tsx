import { useState } from 'react'
import { ScoreBadge } from '../components/ScoreBadge'
import { SectionCard } from '../components/SectionCard'
import { sampleLoanText } from '../data/samples'
import { postFormData } from '../lib/api'
import type { LoanGuardResult } from '../types'

export const LoanGuardPanel = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<LoanGuardResult | null>(null)
  const [status, setStatus] = useState<{ loading: boolean; error?: string }>({ loading: false })

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setStatus({ loading: false, error: 'Upload a document to continue.' })
      return
    }
    setStatus({ loading: true })
    try {
      const form = new FormData()
      form.append('file', selectedFile)
      const response = await postFormData<LoanGuardResult>('/api/loanguard/analyze', form)
      setResult(response)
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Analysis failed' })
    }
  }

  const handleSample = () => {
    const blob = new Blob([sampleLoanText], { type: 'text/plain' })
    setSelectedFile(new File([blob], 'sample_loan.txt', { type: 'text/plain' }))
  }

  return (
    <div className="space-y-6">
      <SectionCard
        title="Upload loan offer"
        description="Detect hidden APR, auto-renew clauses, processing fees, and insurance bundling."
        actions={
          <button
            className="rounded-full border border-brand-500 px-4 py-2 text-sm font-semibold text-brand-600 hover:bg-brand-50"
            onClick={handleSample}
          >
            Load sample loan
          </button>
        }
      >
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
          className="block w-full cursor-pointer rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm"
        />
        {selectedFile && <p className="text-sm text-slate-500">Selected: {selectedFile.name}</p>}
        {status.error && <p className="text-sm text-rose-600">{status.error}</p>}
        <button
          onClick={handleAnalyze}
          disabled={status.loading}
          className="rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
        >
          {status.loading ? 'Analyzing...' : 'Analyze clauses'}
        </button>
      </SectionCard>

      {result && (
        <SectionCard title="Risk assessment">
          <ScoreBadge
            label="Risk score"
            value={result.risk_score}
            variant={result.risk_score > 70 ? 'danger' : 'warning'}
          />
          <p className="text-sm text-slate-600">{result.summary}</p>
          <div className="space-y-3">
            {result.risky_clauses.map((clause, index) => (
              <div key={`${clause.text}-${index}`} className="rounded-2xl border border-rose-200 bg-rose-50 p-4">
                <div className="flex items-center justify-between text-xs font-semibold uppercase text-rose-600">
                  <span>{clause.type.replace('_', ' ')}</span>
                  <span>Recommendation</span>
                </div>
                <p className="mt-2 text-sm text-slate-800">{clause.text}</p>
                <p className="mt-1 text-xs text-rose-600">{clause.recommendation}</p>
              </div>
            ))}
          </div>
        </SectionCard>
      )}
    </div>
  )
}


