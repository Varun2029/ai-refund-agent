/**
 * HTTP API client for communicating with the FastAPI backend
 * Handles token injection, error handling, and JSON serialization
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api'

interface FetchOptions extends RequestInit {
  skipAuth?: boolean
}

export async function fetchAPI(
  endpoint: string,
  options: FetchOptions = {}
) {
  const { skipAuth = false, ...init } = options

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init.headers as Record<string, string>),
  }

  // Inject JWT token if available and not skipped
  if (!skipAuth) {
    const token = localStorage.getItem('token')
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }

  const url = endpoint.startsWith('http')
    ? endpoint
    : `${API_BASE}${endpoint}`

  const response = await fetch(url, {
    ...init,
    headers,
  })

  if (!response.ok) {
    if (response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

// Auth endpoints
export async function login(email: string, password: string) {
  return fetchAPI('/auth/login', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({ email, password }),
  })
}

export async function register(email: string, password: string, full_name: string) {
  return fetchAPI('/auth/register', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({ email, password, full_name }),
  })
}

export async function getCurrentUser() {
  return fetchAPI('/auth/me')
}

// Refund endpoints
export async function listRefunds(statusFilter?: string) {
  const params = new URLSearchParams()
  if (statusFilter) params.set('status_filter', statusFilter)
  return fetchAPI(`/refunds?${params.toString()}`)
}

export async function getRefund(id: number) {
  return fetchAPI(`/refunds/${id}`)
}

export async function getRefundHistory() {
  return fetchAPI('/refunds/history')
}

export async function createRefund(orderId: number, reason: string, amount?: number) {
  return fetchAPI('/refunds', {
    method: 'POST',
    body: JSON.stringify({
      order_id: orderId,
      reason,
      refund_amount: amount,
    }),
  })
}

export async function getRefundLogs(refundId: number) {
  return fetchAPI(`/refunds/${refundId}/logs`)
}

// Customer endpoints
export async function listCustomers() {
  return fetchAPI('/customers')
}

export async function getCustomer(id: number) {
  return fetchAPI(`/customers/${id}`)
}

// Dashboard endpoints
export async function getDashboardStats() {
  return fetchAPI('/dashboard/stats')
}

export async function getReviewQueue() {
  return fetchAPI('/dashboard/queue')
}

// Analytics endpoints
export async function getRefundAnalytics() {
  return fetchAPI('/analytics/refunds')
}

export async function getFraudAnalytics() {
  return fetchAPI('/analytics/fraud')
}

export async function getAgentPerformance() {
  return fetchAPI('/analytics/agents')
}

// Escalation endpoints
export async function listEscalations() {
  return fetchAPI('/escalations')
}

export async function resolveEscalation(
  escalationId: number,
  decision: 'approved' | 'denied',
  notes: string
) {
  return fetchAPI(`/escalations/${escalationId}/resolve`, {
    method: 'POST',
    body: JSON.stringify({
      decision,
      resolution_notes: notes,
    }),
  })
}

export async function getAgentAnalytics() {
  return fetchAPI('/analytics/agents')
}
