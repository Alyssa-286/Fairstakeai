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
      <table className="min-w-full divide-y divide-slate-200 text-xs">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Date</th>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Type</th>
            <th className="px-3 py-2 text-right font-semibold text-slate-600">Amount</th>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Merchant</th>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Account</th>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Balance</th>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Bank</th>
            <th className="px-3 py-2 text-left font-semibold text-slate-600">Ref</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {transactions.map((txn, idx) => (
            <tr key={`${txn.ref}-${idx}`} className="hover:bg-slate-50">
              <td className="px-3 py-2 text-slate-900 whitespace-nowrap">{txn.date}</td>
              <td className="px-3 py-2">
                <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                  txn.direction === 'credit' 
                    ? 'bg-emerald-100 text-emerald-700' 
                    : 'bg-rose-100 text-rose-700'
                }`}>
                  {txn.direction === 'credit' ? '↓ Credit' : '↑ Debit'}
                </span>
              </td>
              <td className="px-3 py-2 text-right font-semibold text-slate-900 whitespace-nowrap">
                ₹{txn.amount.toFixed(2)}
              </td>
              <td className="px-3 py-2 text-slate-700 max-w-[150px] truncate" title={txn.merchant}>
                {txn.merchant !== 'N/A' ? txn.merchant : '-'}
              </td>
              <td className="px-3 py-2 text-slate-600">
                <div className="flex flex-col">
                  <span className="text-xs text-slate-500">{txn.account_type}</span>
                  <span className="font-mono">{txn.account_number !== 'N/A' ? `XX${txn.account_number}` : '-'}</span>
                </div>
              </td>
              <td className="px-3 py-2 text-slate-700 whitespace-nowrap">
                {txn.balance !== 'N/A' ? `₹${parseFloat(txn.balance).toFixed(2)}` : '-'}
              </td>
              <td className="px-3 py-2 text-slate-700 font-medium">{txn.bank}</td>
              <td className="px-3 py-2 text-xs text-slate-500 font-mono max-w-[100px] truncate" title={txn.ref}>
                {txn.ref}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}


