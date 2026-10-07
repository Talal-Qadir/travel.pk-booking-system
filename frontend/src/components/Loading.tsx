export function Loading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-4 py-8 text-slate-600">
      <span className="inline-block h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-sky-600" />
      {label}
    </div>
  )
}
