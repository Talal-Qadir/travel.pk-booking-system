import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import { api } from '../services/api'
import type { AirlineRequestRecord, WebhookEventRecord } from '../types/api'

export function SystemEvents() {
  const [webhooks, setWebhooks] = useState<WebhookEventRecord[]>([])
  const [airline, setAirline] = useState<AirlineRequestRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<unknown>(null)

  useEffect(() => {
    void (async () => {
      try {
        const [wh, al] = await Promise.all([api.getWebhookEvents(), api.getAirlineRequests()])
        setWebhooks(wh)
        setAirline(al)
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) return <Loading label="Loading system events…" />
  if (error) return <ErrorMessage error={error} />

  return (
    <div className="space-y-8">
      <h2 className="text-xl font-semibold">System events</h2>

      <section className="space-y-3">
        <h3 className="font-semibold">PSP webhooks</h3>
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-2">Event ID</th>
                <th className="px-4 py-2">Event type</th>
                <th className="px-4 py-2">Timestamp</th>
                <th className="px-4 py-2">Processed</th>
                <th className="px-4 py-2">Payload hash</th>
              </tr>
            </thead>
            <tbody>
              {webhooks.map((e) => (
                <tr key={e.id} className="border-t border-slate-100">
                  <td className="px-4 py-2 font-mono text-xs">{e.event_id}</td>
                  <td className="px-4 py-2">{e.event_type}</td>
                  <td className="px-4 py-2">{new Date(e.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-2">{new Date(e.processed_at).toLocaleString()}</td>
                  <td className="px-4 py-2 font-mono text-xs">{e.payload_hash.slice(0, 16)}…</td>
                </tr>
              ))}
              {webhooks.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-slate-500">
                    No webhook events recorded yet.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-500">
          Signature verification is enforced server-side when PSP callbacks are received. Processed events indicate verified, accepted webhooks.
        </p>
      </section>

      <section className="space-y-3">
        <h3 className="font-semibold">Airline requests</h3>
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-50 text-left text-slate-600">
              <tr>
                <th className="px-4 py-2">Booking</th>
                <th className="px-4 py-2">Idempotency key</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">PNR</th>
                <th className="px-4 py-2">Attempts</th>
                <th className="px-4 py-2">Created</th>
              </tr>
            </thead>
            <tbody>
              {airline.map((r) => (
                <tr key={r.id} className="border-t border-slate-100">
                  <td className="px-4 py-2">
                    {r.booking_reference ? (
                      <Link className="text-sky-700 hover:underline" to={`/bookings/${r.booking_reference}`}>
                        {r.booking_reference}
                      </Link>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{r.idempotency_key}</td>
                  <td className="px-4 py-2">
                    <StatusBadge status={r.status} />
                  </td>
                  <td className="px-4 py-2">{r.pnr || '—'}</td>
                  <td className="px-4 py-2">{r.attempt_count}</td>
                  <td className="px-4 py-2">{new Date(r.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {airline.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                    No airline ticketing requests yet.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-slate-500">
          Airline failure simulation (slow/flaky modes) is available in the supplier stub but not exposed via a public API endpoint in this assessment build.
        </p>
      </section>
    </div>
  )
}
