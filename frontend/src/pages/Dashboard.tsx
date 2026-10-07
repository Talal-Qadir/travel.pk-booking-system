import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatCard } from '../components/StatCard'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../services/api'
import type { BookingSummary, Fare } from '../types/api'
import { formatPaisa } from '../utils/money'

export function Dashboard() {
  const [fares, setFares] = useState<Fare[]>([])
  const [bookings, setBookings] = useState<BookingSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const [faresData, bookingsData] = await Promise.all([api.getFares(), api.getBookings()])
      setFares(faresData)
      setBookings(bookingsData)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  if (loading) return <Loading label="Loading dashboard…" />
  if (error) return <ErrorMessage error={error} />

  const seats = fares.reduce((sum, f) => sum + f.seats_left, 0)
  const count = (status: string) => bookings.filter((b) => b.status === status).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Dashboard</h2>
        <button type="button" onClick={() => void load()} className="rounded-md border border-slate-300 px-3 py-1.5 text-sm">
          Refresh
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total fares" value={fares.length} />
        <StatCard label="Available seats" value={seats} />
        <StatCard label="Active holds" value={count('HELD')} />
        <StatCard label="Payment pending" value={count('PAYMENT_PENDING')} />
        <StatCard label="Paid bookings" value={count('PAID')} />
        <StatCard label="Ticketed bookings" value={count('TICKETED')} />
        <StatCard label="Expired bookings" value={count('EXPIRED')} />
        <StatCard label="Cancelled / refunded" value={count('CANCELLED') + count('REFUNDED')} />
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-4 py-3">
          <h3 className="font-semibold">Recent bookings</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-2">Reference</th>
                <th className="px-4 py-2">Route</th>
                <th className="px-4 py-2">Customer</th>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Created</th>
                <th className="px-4 py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bookings.slice(0, 10).map((b) => (
                <tr key={b.booking_reference} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-medium">{b.booking_reference}</td>
                  <td className="px-4 py-2">{b.route}</td>
                  <td className="px-4 py-2">{b.customer_name}</td>
                  <td className="px-4 py-2">{formatPaisa(b.amount_paisa)}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={b.status} />
                  </td>
                  <td className="px-4 py-2">{new Date(b.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2">
                    <Link className="text-sky-700 hover:underline" to={`/bookings/${b.booking_reference}`}>
                      View
                    </Link>
                  </td>
                </tr>
              ))}
              {bookings.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-slate-500">
                    No bookings yet. Create a hold to get started.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
