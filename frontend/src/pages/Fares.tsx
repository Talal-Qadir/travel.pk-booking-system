import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { api } from '../services/api'
import type { Fare } from '../types/api'
import { formatPaisa } from '../utils/money'

export function Fares() {
  const [fares, setFares] = useState<Fare[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    void (async () => {
      try {
        setFares(await api.getFares())
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) return <Loading label="Loading fares…" />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Fare inventory</h2>
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-2">Route</th>
              <th className="px-4 py-2">Origin</th>
              <th className="px-4 py-2">Destination</th>
              <th className="px-4 py-2">Base fare</th>
              <th className="px-4 py-2">Taxes</th>
              <th className="px-4 py-2">Total</th>
              <th className="px-4 py-2">Seats left</th>
              <th className="px-4 py-2">Refundable</th>
              <th className="px-4 py-2">Fare rules</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {fares.map((fare) => (
              <tr key={fare.id} className="border-t border-slate-100 align-top">
                <td className="px-4 py-3 font-medium">
                  {fare.origin} → {fare.destination}
                  <div className="text-xs font-normal text-slate-500">
                    {fare.airline} {fare.flight_number}
                  </div>
                </td>
                <td className="px-4 py-3">{fare.origin}</td>
                <td className="px-4 py-3">{fare.destination}</td>
                <td className="px-4 py-3">{formatPaisa(fare.base_price_paisa)}</td>
                <td className="px-4 py-3">{formatPaisa(fare.taxes_paisa)}</td>
                <td className="px-4 py-3 font-medium">{formatPaisa(fare.total_price_paisa)}</td>
                <td className="px-4 py-3">
                  <span className={fare.seats_left === 1 ? 'font-semibold text-amber-700' : ''}>
                    {fare.seats_left}
                    {fare.seats_left === 1 ? ' (last seat)' : ''}
                  </span>
                </td>
                <td className="px-4 py-3">
                  {fare.refundable ? (
                    <span className="text-emerald-700">Refundable</span>
                  ) : (
                    <span className="text-rose-700">Non-refundable</span>
                  )}
                </td>
                <td className="max-w-xs px-4 py-3 text-slate-600">{fare.fare_rules}</td>
                <td className="px-4 py-3">
                  <Link
                    to={`/holds/new?fareId=${fare.id}`}
                    className="text-sky-700 hover:underline"
                  >
                    Hold
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
