/**
 * WebSocket client for real-time chat and agent log streaming
 */

export interface WebSocketMessage {
  type: 'user_message' | 'agent_log' | 'result' | 'error'
  data: Record<string, any>
}

export interface AgentLog {
  agent_name: string
  action: string
  input_summary: string
  output_summary: string
  reasoning: string
  confidence: number
  duration_ms: number
}

export interface WorkflowResult {
  request_id: string
  refund_id: number
  decision: 'approved' | 'denied' | 'escalated'
  decision_rationale: string
  fraud_score: number
  policy_check: string
  agent_logs: AgentLog[]
  status: string
}

export class ChatWebSocket {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000

  connect(
    onMessage: (msg: WebSocketMessage) => void,
    onError?: (err: Error) => void,
    onClose?: () => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Note: token auth handled server-side via cookie/query param if needed
        const defaultProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = import.meta.env.VITE_WS_URL 
          ? `${import.meta.env.VITE_WS_URL}/chat`
          : `${defaultProtocol}//${window.location.host}/ws/chat`

        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('[WS] Connected to chat')
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data)
            onMessage(msg)
          } catch (e) {
            console.error('[WS] Failed to parse message:', e)
          }
        }

        this.ws.onerror = (_event) => {
          const error = new Error('WebSocket error')
          console.error('[WS] Error:', error)
          onError?.(error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('[WS] Disconnected')
          onClose?.()
          this.attemptReconnect(onMessage, onError, onClose)
        }
      } catch (e) {
        reject(e)
      }
    })
  }

  private attemptReconnect(
    onMessage: (msg: WebSocketMessage) => void,
    onError?: (err: Error) => void,
    onClose?: () => void
  ) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`[WS] Attempting reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => {
        this.connect(onMessage, onError, onClose).catch(console.error)
      }, this.reconnectDelay)
    }
  }

  sendMessage(
    message: string,
    customerId?: number,
    orderNumber?: string
  ) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected')
    }

    const token = localStorage.getItem('token')
    this.ws.send(JSON.stringify({
      message,
      customer_id: customerId,
      order_number: orderNumber,
      token,
    }))
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export class LogsWebSocket {
  private ws: WebSocket | null = null

  connect(
    requestId: string,
    onMessage: (msg: WebSocketMessage) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const defaultProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = import.meta.env.VITE_WS_URL 
          ? `${import.meta.env.VITE_WS_URL}/logs/${requestId}`
          : `${defaultProtocol}//${window.location.host}/ws/logs/${requestId}`

        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log(`[WS-Logs] Connected for request ${requestId}`)
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data)
            onMessage(msg)
          } catch (e) {
            console.error('[WS-Logs] Failed to parse message:', e)
          }
        }

        this.ws.onerror = (event) => {
          console.error('[WS-Logs] Error:', event)
          reject(new Error('WebSocket error'))
        }

        this.ws.onclose = () => {
          console.log('[WS-Logs] Disconnected')
        }
      } catch (e) {
        reject(e)
      }
    })
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export class AllLogsWebSocket {
  private ws: WebSocket | null = null

  connect(
    onMessage: (msg: WebSocketMessage) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const defaultProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsUrl = import.meta.env.VITE_WS_URL 
          ? `${import.meta.env.VITE_WS_URL}/logs`
          : `${defaultProtocol}//${window.location.host}/ws/logs`

        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log(`[WS-Logs] Connected to all logs`)
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data)
            onMessage(msg)
          } catch (e) {
            console.error('[WS-Logs] Failed to parse message:', e)
          }
        }

        this.ws.onerror = (event) => {
          console.error('[WS-Logs] Error:', event)
          reject(new Error('WebSocket error'))
        }

        this.ws.onclose = () => {
          console.log('[WS-Logs] Disconnected')
        }
      } catch (e) {
        reject(e)
      }
    })
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
