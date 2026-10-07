export interface Fare {
  id: number
  origin: string
  destination: string
  airline: string
  flight_number: string
  departure_time: string
  arrival_time: string
  base_price_paisa: number
  taxes_paisa: number
  total_price_paisa: number
  seats_left: number
  fare_rules: string
  refundable: boolean
}

export interface HoldResponse {
  booking_reference: string
  price_snapshot_paisa: number
  expires_at: string
  customer_token: string
  route: string
}

export interface BookingSummary {
  booking_reference: string
  route: string
  customer_name: string
  amount_paisa: number
  status: string
  payment_status: string | null
  pnr: string | null
  created_at: string
}

export interface PaymentInfo {
  id: number
  amount_paisa: number
  currency: string
  status: string
  idempotency_key: string
  psp_reference: string | null
  created_at: string
  updated_at: string
}

export interface TicketInfo {
  status: string
  pnr: string | null
  attempt_count: number
  idempotency_key: string | null
  last_error: string | null
  airline_reference: string | null
  updated_at: string
}

export interface BookingDetail {
  booking_reference: string
  route: string
  origin: string | null
  destination: string | null
  customer_name: string
  fare: {
    id: number
    airline: string
    flight_number: string
    refundable: boolean
  }
  price_paisa: number
  base_price_paisa: number
  taxes_paisa: number
  status: string
  expires_at: string | null
  payment: PaymentInfo | null
  payment_status: string | null
  ticket: TicketInfo | null
  pnr: string | null
  ticketed_at: string | null
  created_at: string
  updated_at: string
  refund_preview_paisa: number
  can_cancel: boolean
  can_pay: boolean
}

export interface PaymentRecord {
  id: number
  booking_reference: string | null
  amount_paisa: number
  currency: string
  status: string
  idempotency_key: string
  created_at: string
  updated_at: string
}

export interface WebhookEventRecord {
  id: number
  event_id: string
  provider: string
  event_type: string
  timestamp: string
  processed_at: string
  payload_hash: string
}

export interface AirlineRequestRecord {
  id: number
  booking_reference: string | null
  idempotency_key: string
  status: string
  pnr: string | null
  attempt_count: number
  last_error: string | null
  created_at: string
  updated_at: string
}

export interface CancellationPreview {
  booking_reference: string
  refund_paisa: number
  currency: string
  refundable_fare: boolean
}

export interface ApiErrorBody {
  error?: {
    code?: string
    message?: string
  }
}

export class ApiError extends Error {
  status: number
  code?: string

  constructor(status: number, message: string, code?: string) {
    super(message)
    this.status = status
    this.code = code
  }
}
