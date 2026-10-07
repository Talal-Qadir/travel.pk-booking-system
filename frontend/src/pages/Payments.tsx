import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../services/api'
import type { PaymentRecord } from '../types/api'
import { formatPaisa } from '../utils/money'

export function Payments() {
  const [payments, setPayments] = useState<PaymentRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    void (async () => {
      try {
        setPayments(await api.getPayments())
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) return <Loading label="Loading payments…" />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Payments</h2>
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-2">Payment ID</th>
              <th className="px-4 py-2">Booking</th>
              <th className="px-4 py-2">Amount</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Created</th>
              <th className="px-4 py-2">Updated</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id} className="border-t border-slate-100">
                <td className="px-4 py-2">{p.id}</td>
                <td className="px-4 py-2">
                  {p.booking_reference ? (
                    <Link className="text-sky-700 hover:underline" to={`/bookings/${p.booking_reference}`}>
                      {p.booking_reference}
                    </Link>
                  ) : (
                    '—'
                  )}
                </td>
                <td className="px-4 py-2">{formatPaisa(p.amount_paisa, p.currency)}</td>
                <td className="px-4 py-2">
                  <StatusBadge status={p.status} />
                </td>
                <td className="px-4 py-2">{new Date(p.created_at).toLocaleString()}</td>
                <td className="px-4 py-2">{new Date(p.updated_at).toLocaleString()}</td>
              </tr>
            ))}
            {payments.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                  No payment records yet.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  )
}
