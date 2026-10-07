import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { BookingTimeline } from '../components/BookingTimeline'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../services/api'
import type { BookingDetail, CancellationPreview } from '../types/api'
import { formatPaisa } from '../utils/money'

export function BookingDetails() {
  const { reference = '' } = useParams()
  const [booking, setBooking] = useState<BookingDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [actionError, setActionError] = useState<unknown>(null)
  const [paying, setPaying] = useState(false)
  const [showCancel, setShowCancel] = useState(false)
  const [cancelPreview, setCancelPreview] = useState<CancellationPreview | null>(null)
  const [cancelling, setCancelling] = useState(false)

  const load = useCallback(async () => {
    if (!reference) return
    setLoading(true)
    setError(null)
    try {
      setBooking(await api.getBooking(reference))
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }, [reference])

  useEffect(() => {
    void load()
  }, [load])

  useEffect(() => {
    if (!booking) return
    const shouldPoll = ['HELD', 'PAYMENT_PENDING', 'PAID', 'TICKETING'].includes(booking.status)
    if (!shouldPoll) return
    const id = window.setInterval(() => {
      void load()
    }, 3000)
    return () => window.clearInterval(id)
  }, [booking?.status, load])

  async function startPayment() {
    if (!reference) return
    setPaying(true)
    setActionError(null)
    try {
      const idempotencyKey = crypto.randomUUID()
      await api.startPayment(reference, idempotencyKey)
      await load()
    } catch (err) {
      setActionError(err)
    } finally {
      setPaying(false)
    }
  }

  async function openCancelDialog() {
    setActionError(null)
    try {
      setCancelPreview(await api.getCancellationPreview(reference))
      setShowCancel(true)
    } catch (err) {
      setActionError(err)
    }
  }

  async function confirmCancel() {
    setCancelling(true)
    setActionError(null)
    try {
      await api.cancelBooking(reference)
      setShowCancel(false)
      await load()
    } catch (err) {
      setActionError(err)
    } finally {
      setCancelling(false)
    }
  }

  if (loading && !booking) return <Loading label="Loading booking…" />
  if (error) return <ErrorMessage error={error} />
  if (!booking) return null

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold">{booking.booking_reference}</h2>
          <p className="text-sm text-slate-500">{booking.route}</p>
        </div>
        <StatusBadge status={booking.status} />
      </div>

      {actionError ? <ErrorMessage error={actionError} /> : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 font-semibold">Booking information</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Customer</dt>
              <dd>{booking.customer_name}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Fare</dt>
              <dd>
                {booking.fare.airline} {booking.fare.flight_number}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Amount</dt>
              <dd>{formatPaisa(booking.price_paisa)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Created</dt>
              <dd>{new Date(booking.created_at).toLocaleString()}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Hold expiry</dt>
              <dd>{booking.expires_at ? new Date(booking.expires_at).toLocaleString() : '—'}</dd>
            </div>
          </dl>

          <div className="mt-4 flex flex-wrap gap-2">
            {booking.can_pay ? (
              <button
                type="button"
                disabled={paying}
                onClick={() => void startPayment()}
                className="rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:opacity-60"
              >
                {paying ? 'Starting payment…' : 'Start payment'}
              </button>
            ) : null}
            {booking.can_cancel ? (
              <button
                type="button"
                onClick={() => void openCancelDialog()}
                className="rounded-md border border-rose-300 px-4 py-2 text-sm text-rose-700 hover:bg-rose-50"
              >
                Cancel booking
              </button>
            ) : null}
            <button type="button" onClick={() => void load()} className="rounded-md border border-slate-300 px-4 py-2 text-sm">
              Refresh
            </button>
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="mb-3 font-semibold">Booking timeline</h3>
          <BookingTimeline status={booking.status} />
        </section>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="mb-3 font-semibold">Payment</h3>
        {booking.payment ? (
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-slate-500">Payment ID</dt>
              <dd>{booking.payment.id}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Amount</dt>
              <dd>{formatPaisa(booking.payment.amount_paisa, booking.payment.currency)}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Status</dt>
              <dd>
                <StatusBadge status={booking.payment.status} />
              </dd>
            </div>
            <div>
              <dt className="text-slate-500">Idempotency key</dt>
              <dd className="break-all font-mono text-xs">{booking.payment.idempotency_key}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Created</dt>
              <dd>{new Date(booking.payment.created_at).toLocaleString()}</dd>
            </div>
          </dl>
        ) : (
          <p className="text-sm text-slate-500">No payment started yet.</p>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="mb-3 font-semibold">Ticket</h3>
        {booking.ticket || booking.pnr ? (
          <dl className="grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-slate-500">PNR</dt>
              <dd>{booking.pnr || booking.ticket?.pnr || '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Ticket status</dt>
              <dd>{booking.ticket ? <StatusBadge status={booking.ticket.status} /> : booking.status}</dd>
            </div>
            {booking.ticket?.last_error ? (
              <div className="sm:col-span-2">
                <dt className="text-slate-500">Airline response / error</dt>
                <dd>{booking.ticket.last_error}</dd>
              </div>
            ) : null}
            {booking.ticketed_at ? (
              <div>
                <dt className="text-slate-500">Ticketed at</dt>
                <dd>{new Date(booking.ticketed_at).toLocaleString()}</dd>
              </div>
            ) : null}
          </dl>
        ) : (
          <p className="text-sm text-slate-500">
            {booking.status === 'TICKETING'
              ? 'Ticketing in progress…'
              : 'Not ticketed yet. Complete payment to trigger airline ticketing.'}
          </p>
        )}
      </section>

      {showCancel && cancelPreview ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h3 className="text-lg font-semibold">Cancel booking?</h3>
            <p className="mt-2 text-sm text-slate-600">
              Are you sure you want to cancel this booking? This action cannot be undone.
            </p>
            <p className="mt-3 text-sm">
              Refund: <strong>{formatPaisa(cancelPreview.refund_paisa, cancelPreview.currency)}</strong>
            </p>
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" className="rounded-md border px-4 py-2 text-sm" onClick={() => setShowCancel(false)}>
                Keep booking
              </button>
              <button
                type="button"
                disabled={cancelling}
                className="rounded-md bg-rose-600 px-4 py-2 text-sm text-white"
                onClick={() => void confirmCancel()}
              >
                {cancelling ? 'Cancelling…' : 'Confirm cancel'}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
