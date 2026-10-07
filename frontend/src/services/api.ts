import type {
  AirlineRequestRecord,
  ApiErrorBody,
  BookingDetail,
  BookingSummary,
  CancellationPreview,
  Fare,
  HoldResponse,
  PaymentRecord,
  WebhookEventRecord,
} from '../types/api'
import { ApiError } from '../types/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || '/api'

const PARTNER_KEY_STORAGE = 'travelpk_partner_key'
const CUSTOMER_TOKENS_STORAGE = 'travelpk_customer_tokens'

export function getPartnerKey(): string {
  return localStorage.getItem(PARTNER_KEY_STORAGE) || 'partner-admin'
}

export function setPartnerKey(key: string): void {
  localStorage.setItem(PARTNER_KEY_STORAGE, key)
}

export function saveCustomerToken(reference: string, token: string): void {
  const raw = localStorage.getItem(CUSTOMER_TOKENS_STORAGE)
  const map: Record<string, string> = raw ? JSON.parse(raw) : {}
  map[reference] = token
  localStorage.setItem(CUSTOMER_TOKENS_STORAGE, JSON.stringify(map))
}

export function getCustomerToken(reference: string): string | undefined {
  const raw = localStorage.getItem(CUSTOMER_TOKENS_STORAGE)
  if (!raw) return undefined
  const map: Record<string, string> = JSON.parse(raw)
  return map[reference]
}

function authHeaderForBooking(reference?: string): string {
  if (reference) {
    const customer = getCustomerToken(reference)
    if (customer) return `Bearer ${customer}`
  }
  return `Bearer ${getPartnerKey()}`
}

async function request<T>(
  path: string,
  options: RequestInit & { bookingAuthRef?: string } = {},
): Promise<T> {
  const { bookingAuthRef, headers, ...rest } = options
  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      Authorization: authHeaderForBooking(bookingAuthRef),
      ...(headers as Record<string, string>),
    },
  })

  const text = await response.text()
  let body: unknown = null
  if (text) {
    try {
      body = JSON.parse(text)
    } catch {
      body = { error: { message: text } }
    }
  }

  if (!response.ok) {
    const err = body as ApiErrorBody
    throw new ApiError(
      response.status,
      err.error?.message || `Request failed (${response.status})`,
      err.error?.code,
    )
  }

  return body as T
}

export const api = {
  getFares: () =>
    request<Fare[]>('/fares', { method: 'GET', headers: { Authorization: `Bearer ${getPartnerKey()}` } }),

  createHold: (fareId: number, customerName: string) =>
    request<HoldResponse>('/holds', {
      method: 'POST',
      headers: { Authorization: `Bearer ${getPartnerKey()}` },
      body: JSON.stringify({ fare_id: fareId, customer_name: customerName }),
    }),

  getBookings: () =>
    request<BookingSummary[]>('/bookings', {
      method: 'GET',
      headers: { Authorization: `Bearer ${getPartnerKey()}` },
    }),

  getBooking: (reference: string) =>
    request<BookingDetail>(`/bookings/${encodeURIComponent(reference)}`, {
      method: 'GET',
      bookingAuthRef: reference,
    }),

  getCancellationPreview: (reference: string) =>
    request<CancellationPreview>(`/bookings/${encodeURIComponent(reference)}/cancellation-preview`, {
      method: 'GET',
      bookingAuthRef: reference,
    }),

  cancelBooking: (reference: string) =>
    request<{ booking_reference: string; status: string; refund_paisa: number; refund_status: string }>(
      `/bookings/${encodeURIComponent(reference)}/cancel`,
      { method: 'POST', bookingAuthRef: reference },
    ),

  startPayment: (reference: string, idempotencyKey: string) =>
    request<{ id: number; booking_reference: string; status: string; amount_paisa: number; currency: string }>(
      '/payments',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${getPartnerKey()}`,
          'Idempotency-Key': idempotencyKey,
        },
        body: JSON.stringify({ booking_reference: reference }),
      },
    ),

  getPayments: () =>
    request<PaymentRecord[]>('/admin/payments', {
      method: 'GET',
      headers: { Authorization: `Bearer ${getPartnerKey()}` },
    }),

  getWebhookEvents: () =>
    request<WebhookEventRecord[]>('/admin/webhook-events', {
      method: 'GET',
      headers: { Authorization: `Bearer ${getPartnerKey()}` },
    }),

  getAirlineRequests: () =>
    request<AirlineRequestRecord[]>('/admin/airline-requests', {
      method: 'GET',
      headers: { Authorization: `Bearer ${getPartnerKey()}` },
    }),
}
