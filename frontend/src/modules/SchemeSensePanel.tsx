import { useState } from 'react'
import { ClauseList } from '../components/ClauseList'
import { ScoreBadge } from '../components/ScoreBadge'
import { SectionCard } from '../components/SectionCard'
import { postFormData } from '../lib/api'
import { sampleSchemeResponse, sampleSchemeText } from '../data/samples'
import type { SchemeSenseResult } from '../types'

export const SchemeSensePanel = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [result, setResult] = useState<SchemeSenseResult | null>(null)
  const [status, setStatus] = useState<{ loading: boolean; error?: string }>({ loading: false })

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setStatus({ loading: false, error: 'Upload a PDF or text file to analyze.' })
      return
    }
    setStatus({ loading: true })
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      const response = await postFormData<SchemeSenseResult>('/api/schemesense/upload', formData)
      setResult(response)
      setStatus({ loading: false })
    } catch (error) {
      setStatus({ loading: false, error: error instanceof Error ? error.message : 'Analysis failed' })
    }
  }

  const handleSample = () => {
    const blob = new Blob([sampleSchemeText], { type: 'text/plain' })
    const sampleFile = new File([blob], 'sample_scheme.txt', { type: 'text/plain' })
    setSelectedFile(sampleFile)
    setResult(sampleSchemeResponse)
  }

  return (
    <div className="space-y-6">
      <SectionCard
        title="Upload scheme document"
        description="We only process files in-memory; nothing is persisted."
        actions={
          <button
            className="rounded-full border border-brand-500 px-4 py-2 text-sm font-semibold text-brand-600 hover:bg-brand-50"
            onClick={handleSample}
          >
            Load sample
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
          {status.loading ? 'Analyzing...' : 'Process file'}
        </button>
      </SectionCard>

      {result && (
        <SectionCard title="Fairness report" description="Top risk clauses and mitigation tips.">
          <div className="flex flex-wrap gap-4">
            <ScoreBadge label="Fairness score" value={result.fairness_score} variant={result.fairness_score > 70 ? 'success' : 'warning'} />
            <div className="rounded-2xl bg-slate-100 px-4 py-3 text-sm text-slate-600">{result.summary}</div>
          </div>
          <ClauseList clauses={result.clauses} />
        </SectionCard>
      )}
    </div>
  )
}


