import { StatusBadge } from './StatusBadge'

const FLOW = ['HELD', 'PAYMENT_PENDING', 'PAID', 'TICKETING', 'TICKETED'] as const

function activeIndex(status: string): number {
  if (status === 'EXPIRED' || status === 'CANCELLED' || status === 'REFUNDED' || status === 'FAILED') {
    return -1
  }
  const idx = FLOW.indexOf(status as (typeof FLOW)[number])
  return idx >= 0 ? idx : FLOW.findIndex((s) => s === 'PAID')
}

export function BookingTimeline({ status }: { status: string }) {
  const terminal = ['EXPIRED', 'CANCELLED', 'REFUNDED', 'FAILED'].includes(status)
  const current = activeIndex(status)

  if (terminal) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-4">
        <p className="mb-2 text-sm font-medium text-slate-600">Booking ended</p>
        <StatusBadge status={status} />
      </div>
    )
  }

  return (
    <ol className="space-y-3">
      {FLOW.map((step, index) => {
        const done = index <= current
        return (
          <li key={step} className="flex items-center gap-3">
            <span
              className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                done ? 'bg-sky-600 text-white' : 'bg-slate-200 text-slate-500'
              }`}
            >
              {index + 1}
            </span>
            <div>
              <p className={`text-sm font-medium ${done ? 'text-slate-900' : 'text-slate-500'}`}>
                {step.replace(/_/g, ' ')}
              </p>
              {index === current ? <StatusBadge status={status} /> : null}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
