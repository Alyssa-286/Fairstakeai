import type { PropsWithChildren } from 'react'

interface SectionCardProps extends PropsWithChildren {
  title: string
  description?: string
  actions?: React.ReactNode
}

export const SectionCard = ({ title, description, actions, children }: SectionCardProps) => (
  <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
    <div className="mb-4 flex items-start justify-between gap-4">
      <div>
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        {description && <p className="text-sm text-slate-500">{description}</p>}
      </div>
      {actions}
    </div>
    <div className="space-y-4">{children}</div>
  </section>
)


