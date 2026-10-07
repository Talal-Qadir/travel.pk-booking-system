import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { api, saveCustomerToken } from '../services/api'
import type { Fare, HoldResponse } from '../types/api'
import { formatPaisa } from '../utils/money'

function useCountdown(expiresAt: string | null) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    if (!expiresAt) return
    const id = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(id)
  }, [expiresAt])

  return useMemo(() => {
    if (!expiresAt) return null
    const diff = new Date(expiresAt).getTime() - now
    if (diff <= 0) return '00:00'
    const mins = Math.floor(diff / 60000)
    const secs = Math.floor((diff % 60000) / 1000)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }, [expiresAt, now])
}

export function CreateHold() {
  const [params] = useSearchParams()
  const preselected = params.get('fareId')
  const [fares, setFares] = useState<Fare[]>([])
  const [fareId, setFareId] = useState(preselected || '')
  const [customerName, setCustomerName] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<unknown>(null)
  const [result, setResult] = useState<HoldResponse | null>(null)
  const [expiredOnServer, setExpiredOnServer] = useState(false)

  const countdown = useCountdown(result?.expires_at ?? null)

  useEffect(() => {
    void (async () => {
      try {
        const data = await api.getFares()
        setFares(data)
        setFareId((current) => current || preselected || (data[0] ? String(data[0].id) : ''))
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    })()
  }, [preselected])

  useEffect(() => {
    if (!result || countdown !== '00:00') return
    void (async () => {
      try {
        const booking = await api.getBooking(result.booking_reference)
        if (booking.status === 'EXPIRED') setExpiredOnServer(true)
      } catch {
        setExpiredOnServer(true)
      }
    })()
  }, [countdown, result])

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    setResult(null)
    setExpiredOnServer(false)
    try {
      const hold = await api.createHold(Number(fareId), customerName.trim() || 'Guest')
      saveCustomerToken(hold.booking_reference, hold.customer_token)
      setResult(hold)
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <Loading label="Loading fares…" />

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h2 className="text-xl font-semibold">Create hold</h2>

      {!result ? (
        <form onSubmit={submit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <label className="block text-sm">
            Select fare
            <select
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
              value={fareId}
              onChange={(e) => setFareId(e.target.value)}
              required
            >
              {fares.map((fare) => (
                <option key={fare.id} value={fare.id}>
                  {fare.origin} → {fare.destination} — {formatPaisa(fare.total_price_paisa)} ({fare.seats_left} seats)
                </option>
              ))}
            </select>
          </label>

          <label className="block text-sm">
            Customer / passenger name
            <input
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
              placeholder="Full name"
              required
            />
          </label>

          <p className="text-xs text-slate-500">
            Price, taxes, booking reference, and inventory are assigned by the server when the hold is created.
          </p>

          {error ? <ErrorMessage error={error} /> : null}

          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:opacity-60"
          >
            {submitting ? 'Creating hold…' : 'Hold fare'}
          </button>
        </form>
      ) : (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-6">
          <h3 className="text-lg font-semibold text-emerald-900">Booking held successfully</h3>
          <dl className="mt-4 space-y-2 text-sm">
            <div>
              <dt className="text-slate-600">Reference</dt>
              <dd className="font-semibold">{result.booking_reference}</dd>
            </div>
            <div>
              <dt className="text-slate-600">Route</dt>
              <dd>{result.route}</dd>
            </div>
            <div>
              <dt className="text-slate-600">Amount</dt>
              <dd>{formatPaisa(result.price_snapshot_paisa)}</dd>
            </div>
            <div>
              <dt className="text-slate-600">Expires</dt>
              <dd>{new Date(result.expires_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</dd>
            </div>
            <div>
              <dt className="text-slate-600">Time remaining</dt>
              <dd className="text-lg font-semibold">{expiredOnServer ? 'Expired (server)' : countdown}</dd>
            </div>
          </dl>
          <div className="mt-4 flex gap-3">
            <Link
              to={`/bookings/${result.booking_reference}`}
              className="rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white"
            >
              View booking
            </Link>
            <button
              type="button"
              className="rounded-md border border-slate-300 px-4 py-2 text-sm"
              onClick={() => setResult(null)}
            >
              Create another
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
