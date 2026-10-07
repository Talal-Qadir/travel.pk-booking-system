import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../services/api'
import type { BookingSummary } from '../types/api'
import { formatPaisa } from '../utils/money'

const STATUSES = [
  'ALL',
  'HELD',
  'PAYMENT_PENDING',
  'PAID',
  'TICKETING',
  'TICKETED',
  'EXPIRED',
  'CANCELLED',
  'REFUNDED',
  'FAILED',
] as const

export function Bookings() {
  const [bookings, setBookings] = useState<BookingSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<(typeof STATUSES)[number]>('ALL')

  async function load() {
    setLoading(true)
    setError(null)
    try {
      setBookings(await api.getBookings())
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const filtered = useMemo(() => {
    return bookings.filter((b) => {
      const matchesSearch = b.booking_reference.toLowerCase().includes(search.toLowerCase())
      const matchesStatus = statusFilter === 'ALL' || b.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [bookings, search, statusFilter])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold">Bookings</h2>
        <button type="button" onClick={() => void load()} className="rounded-md border border-slate-300 px-3 py-1.5 text-sm">
          Refresh
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          placeholder="Search by reference"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as (typeof STATUSES)[number])}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {loading ? <Loading label="Loading bookings…" /> : null}
      {error ? <ErrorMessage error={error} /> : null}

      {!loading && !error ? (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-2">Reference</th>
                <th className="px-4 py-2">Route</th>
                <th className="px-4 py-2">Customer</th>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Payment</th>
                <th className="px-4 py-2">Booking status</th>
                <th className="px-4 py-2">PNR</th>
                <th className="px-4 py-2">Created</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((b) => (
                <tr key={b.booking_reference} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium">{b.booking_reference}</td>
                  <td className="px-4 py-2">{b.route}</td>
                  <td className="px-4 py-2">{b.customer_name}</td>
                  <td className="px-4 py-2">{formatPaisa(b.amount_paisa)}</td>
                  <td className="px-4 py-2">{b.payment_status ? <StatusBadge status={b.payment_status} /> : '—'}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={b.status} />
                  </td>
                  <td className="px-4 py-2">{b.pnr || '—'}</td>
                  <td className="px-4 py-2">{new Date(b.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2">
                    <Link className="text-sky-700 hover:underline" to={`/bookings/${b.booking_reference}`}>
                      Details
                    </Link>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-4 py-8 text-center text-slate-500">
                    No bookings match your filters.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  )
}
