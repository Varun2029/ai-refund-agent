/**
 * Custom hooks for the frontend application
 */

import { useState, useEffect, useCallback } from 'react'
import { ChatWebSocket, LogsWebSocket, AllLogsWebSocket, type WebSocketMessage, type AgentLog, type WorkflowResult } from '../lib/ws'

export function useWebSocketChat() {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<WebSocketMessage[]>([])
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([])
  const [result, setResult] = useState<WorkflowResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [ws] = useState(() => new ChatWebSocket())

  useEffect(() => {
    ws.connect(
      (msg) => {
        if (msg.type === 'agent_log') {
          setAgentLogs(prev => [...prev, msg.data as AgentLog])
        } else if (msg.type === 'result') {
          setResult(msg.data as WorkflowResult)
        } else if (msg.type === 'error') {
          // Only show backend workflow errors, not connection errors
          setError(msg.data.message)
        } else {
          // user_message and other display messages
          setMessages(prev => [...prev, msg])
        }
      },
      (_err) => {
        // Swallow connection errors silently — the isConnected badge already
        // shows "Connecting…" so the user doesn't need a red error banner
        console.warn('[WS] Connection error — will retry automatically')
      },
      () => {
        setIsConnected(false)
      }
    ).then(() => {
      setIsConnected(true)
    }).catch(_err => {
      // Also suppress the initial connect rejection silently
      console.warn('[WS] Initial connection failed — retrying in background')
    })

    return () => {
      ws.disconnect()
    }
  }, [ws])

  const sendMessage = useCallback((
    message: string,
    customerId?: number,
    orderNumber?: string
  ) => {
    if (!isConnected) {
      setError('Not connected to chat')
      return
    }
    try {
      ws.sendMessage(message, customerId, orderNumber)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    }
  }, [isConnected, ws])

  const reset = useCallback(() => {
    setMessages([])
    setAgentLogs([])
    setResult(null)
    setError(null)
  }, [])

  return {
    isConnected,
    messages,
    agentLogs,
    result,
    error,
    sendMessage,
    reset,
  }
}

export function useAgentLogs(requestId: string | null) {
  const [logs, setLogs] = useState<AgentLog[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [ws] = useState(() => new LogsWebSocket())

  useEffect(() => {
    if (!requestId) return

    ws.connect(requestId, (msg) => {
      if (msg.type === 'agent_log') {
        setLogs(prev => [...prev, msg.data as AgentLog])
      }
    }).then(() => {
      setIsConnected(true)
    }).catch(console.error)

    return () => {
      ws.disconnect()
    }
  }, [requestId, ws])

  return { logs, isConnected }
}

export function useAllAgentLogs() {
  const [logs, setLogs] = useState<AgentLog[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [ws] = useState(() => new AllLogsWebSocket())

  useEffect(() => {
    ws.connect((msg) => {
      if (msg.type === 'agent_log') {
        setLogs(prev => [...prev, msg.data as AgentLog])
      }
    }).then(() => {
      setIsConnected(true)
    }).catch(console.error)

    return () => {
      ws.disconnect()
    }
  }, [ws])

  return { logs, isConnected }
}

export function useFetch<T>(
  url: string | null,
  fetcher: (url: string) => Promise<T>
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(!!url)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!url) {
      setData(null)
      setLoading(false)
      return
    }

    let mounted = true

    fetcher(url)
      .then(result => {
        if (mounted) {
          setData(result)
          setError(null)
        }
      })
      .catch(err => {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Unknown error')
          setData(null)
        }
      })
      .finally(() => {
        if (mounted) setLoading(false)
      })

    return () => {
      mounted = false
    }
  }, [url, fetcher])

  return { data, loading, error }
}

export function usePoll<T>(
  fetcher: () => Promise<T>,
  interval: number = 5000,
  enabled: boolean = true
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!enabled) return

    let timeoutId: ReturnType<typeof setTimeout>

    const poll = async () => {
      try {
        setLoading(true)
        const result = await fetcher()
        setData(result)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
        timeoutId = setTimeout(poll, interval)
      }
    }

    poll()

    return () => {
      if (timeoutId) clearTimeout(timeoutId)
    }
  }, [fetcher, interval, enabled])

  return { data, loading, error }
}
