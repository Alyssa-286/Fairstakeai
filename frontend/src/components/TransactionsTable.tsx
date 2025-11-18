import type { FinanceTransaction } from '../types'

interface Props {
  transactions: FinanceTransaction[]
}

export const TransactionsTable = ({ transactions }: Props) => {
  if (!transactions.length) {
    return <p className="text-sm text-slate-500">No transactions parsed yet.</p>
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-2 text-left font-semibold text-slate-600">Date</th>
            <th className="px-4 py-2 text-left font-semibold text-slate-600">Direction</th>
            <th className="px-4 py-2 text-right font-semibold text-slate-600">Amount</th>
            <th className="px-4 py-2 text-left font-semibold text-slate-600">Bank</th>
            <th className="px-4 py-2 text-left font-semibold text-slate-600">Reference</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {transactions.map((txn) => (
            <tr key={txn.ref}>
              <td className="px-4 py-2 text-slate-900">{txn.date}</td>
              <td className="px-4 py-2 capitalize text-slate-700">{txn.direction}</td>
              <td className="px-4 py-2 text-right font-medium text-slate-900">₹{txn.amount.toFixed(2)}</td>
              <td className="px-4 py-2 text-slate-700">{txn.bank}</td>
              <td className="px-4 py-2 text-xs text-slate-500">{txn.ref}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


