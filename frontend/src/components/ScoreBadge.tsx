interface Props {
  label: string
  value: number
  variant?: 'success' | 'warning' | 'danger'
}

const variantStyles: Record<NonNullable<Props['variant']>, string> = {
  success: 'bg-emerald-100 text-emerald-700',
  warning: 'bg-amber-100 text-amber-700',
  danger: 'bg-rose-100 text-rose-700',
}

export const ScoreBadge = ({ label, value, variant = 'success' }: Props) => (
  <div className={`inline-flex flex-col rounded-xl px-4 py-3 text-center ${variantStyles[variant]}`}>
    <span className="text-xs uppercase tracking-wide">{label}</span>
    <span className="text-2xl font-bold">{value}</span>
  </div>
)


