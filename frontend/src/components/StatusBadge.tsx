const styles: Record<string, string> = {
  HELD: 'bg-sky-100 text-sky-800',
  PAYMENT_PENDING: 'bg-amber-100 text-amber-900',
  PAID: 'bg-emerald-100 text-emerald-800',
  TICKETING: 'bg-indigo-100 text-indigo-800',
  TICKETED: 'bg-green-100 text-green-900',
  EXPIRED: 'bg-slate-200 text-slate-700',
  CANCELLED: 'bg-rose-100 text-rose-800',
  REFUNDED: 'bg-purple-100 text-purple-800',
  FAILED: 'bg-red-100 text-red-800',
  PENDING: 'bg-amber-100 text-amber-900',
  SUCCEEDED: 'bg-emerald-100 text-emerald-800',
  IN_PROGRESS: 'bg-indigo-100 text-indigo-800',
  COMPLETED: 'bg-green-100 text-green-900',
}

export function StatusBadge({ status }: { status: string }) {
  const cls = styles[status] || 'bg-slate-100 text-slate-700'
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${cls}`}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
