import type { Clause } from '../types'

interface Props {
  clauses: Clause[]
}

const labelColors: Record<string, string> = {
  neutral: 'bg-slate-100 text-slate-700',
  income_exclusion: 'bg-amber-100 text-amber-700',
  gender_bias: 'bg-rose-100 text-rose-700',
  location_bias: 'bg-indigo-100 text-indigo-700',
}

export const ClauseList = ({ clauses }: Props) => {
  if (!clauses.length) return <p className="text-sm text-slate-500">No clauses detected yet.</p>
  return (
    <div className="space-y-4">
      {clauses.map((clause) => (
        <div key={clause.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <div className="flex items-center justify-between gap-2">
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${labelColors[clause.label] ?? ''}`}>
              {clause.label.replace('_', ' ')}
            </span>
            <span className="text-xs text-slate-500">Confidence {(clause.confidence * 100).toFixed(0)}%</span>
          </div>
          <p className="mt-2 text-sm text-slate-800">{clause.text}</p>
          <p className="mt-2 text-xs text-slate-500">Suggestion: {clause.suggestion}</p>
        </div>
      ))}
    </div>
  )
}


