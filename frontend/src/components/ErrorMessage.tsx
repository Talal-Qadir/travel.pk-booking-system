import { ApiError } from '../types/api'

export function ErrorMessage({ error }: { error: unknown }) {
  if (!error) return null
  const message = error instanceof ApiError ? error.message : 'Something went wrong.'
  const status = error instanceof ApiError ? error.status : undefined
  const code = error instanceof ApiError ? error.code : undefined

  return (
    <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-rose-900">
      {status ? <p className="text-sm font-semibold">{status} {status === 409 ? 'Conflict' : ''}</p> : null}
      <p className="text-sm">{message}</p>
      {code ? <p className="mt-1 text-xs text-rose-700">Code: {code}</p> : null}
    </div>
  )
}
