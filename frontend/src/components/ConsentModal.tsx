interface ConsentModalProps {
  open: boolean
  onAccept: () => void
  onDecline: () => void
}

export const ConsentModal = ({ open, onAccept, onDecline }: ConsentModalProps) => {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 px-4">
      <div className="max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
        <h3 className="text-xl font-semibold text-slate-900">Consent required</h3>
        <p className="mt-3 text-sm text-slate-600">
          By pasting SMS data you consent to in-memory analysis for this demo. We do not persist, log, or transmit your
          SMS content outside this browser session.
        </p>
        <div className="mt-6 flex justify-end gap-3">
          <button
            className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
            onClick={onDecline}
          >
            Cancel
          </button>
          <button
            className="rounded-full bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
            onClick={onAccept}
          >
            I consent
          </button>
        </div>
      </div>
    </div>
  )
}




