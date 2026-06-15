/**
 * ChatPage - Gemini-themed refund chat interface with real-time agent pipeline
 */

import { useState, useRef, useEffect } from 'react'
import { useWebSocketChat } from '../hooks/useWebSocket'
import { VoiceController } from '../lib/speech'
import { formatDuration } from '../lib/utils'
import { useAuth } from '../lib/auth'
import { Send, Mic, MicOff, RotateCcw, Volume2, CheckCircle2, Loader2, ChevronRight, Sparkles, Shield, FileCheck, Brain, UserCheck } from 'lucide-react'
import AppLayout from '../components/layout/AppLayout'

const AGENTS = [
  { id: 'customer_agent', label: 'Understanding Request',  icon: UserCheck,  color: '#1a73e8' },
  { id: 'crm_agent',      label: 'Checking Records',       icon: Brain,      color: '#7c3aed' },
  { id: 'policy_agent',   label: 'Reviewing Policies',     icon: FileCheck,  color: '#059669' },
  { id: 'fraud_agent',    label: 'Security Check',         icon: Shield,     color: '#d97706' },
  { id: 'decision_agent', label: 'Making Decision',        icon: Sparkles,   color: '#1a73e8' },
]

function decisionBadge(d: string) {
  const map: Record<string, string> = {
    approved:  'badge badge-approved',
    denied:    'badge badge-denied',
    escalated: 'badge badge-escalated',
    pending:   'badge badge-pending',
  }
  return map[d] || 'badge badge-blue'
}

export default function ChatPage() {
  const { user } = useAuth()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [messageText, setMessageText] = useState('')
  const [customerId, setCustomerId] = useState<number | undefined>()
  const [orderNumber, setOrderNumber] = useState<string | undefined>()
  const [voiceActive, setVoiceActive] = useState(false)
  const [transcript, setTranscript] = useState('')

  const { isConnected, messages, agentLogs, result, error, sendMessage, reset } = useWebSocketChat()
  const [voiceController] = useState(() => new VoiceController())

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, agentLogs, result])

  // Automatically speak the final result when it arrives
  useEffect(() => {
    if (result && result.decision_rationale && voiceController.isSupported()) {
      voiceController.speak(result.decision_rationale)
    }
  }, [result, voiceController])

  const isProcessing = messages.some(m => m.type === 'user_message') && !result && !error

  function handleSend(e: React.FormEvent) {
    e.preventDefault()
    const text = transcript || messageText
    if (!text.trim()) return
    
    sendMessage(text, customerId, orderNumber)
    setMessageText('')
    setTranscript('')
  }

  function toggleVoice() {
    if (!voiceController.isSupported()) return
    if (voiceActive) {
      voiceController.stopListening()
      setVoiceActive(false)
    } else {
      setVoiceActive(true)
      voiceController.startListening(
        (text, isFinal) => {
          setTranscript(text)
          if (isFinal) { setMessageText(text); voiceController.stopListening(); setVoiceActive(false) }
        },
        () => setVoiceActive(false)
      )
    }
  }

  return (
    <AppLayout>
      <div className="h-full flex gap-0 overflow-hidden">

        {/* ─── Chat Panel ─── */}
        <div className="flex-1 flex flex-col border-r border-[#dde6ff] overflow-hidden">

          {/* Chat header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#dde6ff] bg-white">
            <div>
              <h2 className="font-bold text-[#0d1b4b]">
                {user ? `Welcome back, ${user.full_name.split(' ')[0]} 👋` : 'AI Refund Assistant'}
              </h2>
              <p className="text-xs text-[#8a9bcc]">Describe your issue and our 5-agent system will handle it</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full ${isConnected ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
                {isConnected ? 'Connected' : 'Connecting…'}
              </span>
              <button onClick={reset} className="flex items-center gap-1.5 text-xs font-medium text-[#4a5a8a] px-3 py-1.5 rounded-full border border-[#dde6ff] hover:bg-[#f0f4ff] transition-all">
                <RotateCcw size={12} /> New Chat
              </button>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4 bg-[#f8faff]">

            {/* Empty state */}
            {messages.length === 0 && agentLogs.length === 0 && (
              <div className="h-full flex items-center justify-center animate-fade-in">
                <div className="text-center max-w-sm">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] flex items-center justify-center shadow-xl">
                    <Sparkles size={28} className="text-white" />
                  </div>
                  <h3 className="font-bold text-[#0d1b4b] text-lg mb-2">Start a Refund Request</h3>
                  <p className="text-sm text-[#4a5a8a] mb-6">Describe your issue below. Our AI agents will analyze it and provide a decision.</p>
                  <div className="grid grid-cols-1 gap-2 text-left">
                    {[
                      '"I want a refund for order ORD-1001, the headphones are broken"',
                      '"My order ORD-1003 was delivered damaged"',
                      '"Wrong item received for ORD-1002, need a refund"',
                    ].map(s => (
                      <button key={s} onClick={() => setMessageText(s.replace(/"/g, ''))}
                        className="text-left text-xs p-3 bg-white border border-[#dde6ff] rounded-xl text-[#4a5a8a] hover:border-[#1a73e8] hover:text-[#1a73e8] hover:bg-[#f0f4ff] transition-all duration-200 font-medium"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Actual messages */}
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.type === 'user_message' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
                {msg.type === 'user_message' && (
                  <div className="chat-bubble-user max-w-[70%] text-sm font-medium shadow-lg">
                    {msg.data.message}
                  </div>
                )}
                {msg.type === 'error' && (
                  <div className="chat-bubble-agent max-w-[70%] text-sm border-red-200 bg-red-50 text-red-700">
                    ⚠️ {msg.data.message}
                  </div>
                )}
              </div>
            ))}

            {/* Agent logs removed for customer view */}

            {/* Live processing steps for customer */}
            {(isProcessing || agentLogs.length > 0) && !result && (
              <div className="flex justify-start animate-fade-in">
                <div className="chat-bubble-agent flex flex-col p-5 gap-3 border border-[#dde6ff] shadow-sm min-w-[280px]">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="relative w-5 h-5 flex items-center justify-center">
                      <div className="absolute inset-0 border-2 border-[#dde6ff] rounded-full"></div>
                      <div className="absolute inset-0 border-2 border-[#1a73e8] rounded-full border-t-transparent animate-spin"></div>
                    </div>
                    <p className="text-sm font-bold text-[#0d1b4b]">Processing your request...</p>
                  </div>
                  
                  <div className="space-y-3 pl-2">
                    {agentLogs.map((log, idx) => {
                      const agentDef = AGENTS.find(a => a.id === log.agent_name)
                      return (
                        <div key={idx} className="flex items-start gap-2 animate-slide-up">
                          <CheckCircle2 size={16} className="text-emerald-500 mt-0.5 shrink-0" />
                          <div>
                            <p className="text-xs font-semibold text-[#4a5a8a]">{agentDef?.label || 'Agent'}</p>
                            <p className="text-xs text-[#8a9bcc] leading-relaxed">{log.output_summary}</p>
                          </div>
                        </div>
                      )
                    })}
                    
                    {/* Next step loading indicator */}
                    {isProcessing && (
                      <div className="flex items-center gap-2 animate-pulse mt-2">
                        <div className="w-4 h-4 rounded-full border-2 border-[#dde6ff] border-t-[#8a9bcc] animate-spin shrink-0" />
                        <p className="text-xs text-[#8a9bcc] italic">Analyzing next steps...</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Final result */}
            {result && (
              <div className="animate-scale-in card p-5 border-[#b3c4ff]" style={{ background: 'linear-gradient(135deg, #f0f4ff, #f5f0ff)' }}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={18} className="text-[#1a73e8]" />
                    <span className="font-bold text-[#0d1b4b]">Decision Complete</span>
                  </div>
                  <span className={decisionBadge(result.decision)}>
                    {result.decision === 'escalated' ? 'UNDER REVIEW' : result.decision.toUpperCase()}
                  </span>
                </div>
                <p className="text-sm text-[#4a5a8a] leading-relaxed mb-4">
                  {result.decision === 'escalated' ? 'Denied for now, will go for review' : result.decision_rationale}
                </p>
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-white rounded-xl p-3 border border-[#dde6ff] text-center">
                    <p className="text-xs text-[#8a9bcc] mb-1">Fraud Score</p>
                    <p className="text-lg font-bold text-[#0d1b4b]">{result.fraud_score?.toFixed(0) ?? 'N/A'}</p>
                  </div>
                  <div className="bg-white rounded-xl p-3 border border-[#dde6ff] text-center">
                    <p className="text-xs text-[#8a9bcc] mb-1">Policy</p>
                    <p className="text-sm font-bold text-[#0d1b4b] capitalize">{result.policy_check ?? 'N/A'}</p>
                  </div>
                  <div className="bg-white rounded-xl p-3 border border-[#dde6ff] text-center">
                    <p className="text-xs text-[#8a9bcc] mb-1">Agents</p>
                    <p className="text-lg font-bold text-[#0d1b4b]">{result.agent_logs?.length ?? 0}/5</p>
                  </div>
                </div>
                <button onClick={() => voiceController.speak(result.decision_rationale)}
                  className="mt-3 w-full flex items-center justify-center gap-2 py-2 text-sm text-[#4a5a8a] hover:text-[#1a73e8] border border-[#dde6ff] rounded-xl hover:border-[#b3c4ff] transition-all bg-white">
                  <Volume2 size={14} /> Speak Result
                </button>
              </div>
            )}

            {error && (
              <div className="animate-scale-in p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
                <p className="font-semibold mb-1">Error occurred</p>
                <p className="opacity-80 text-xs">{error}</p>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="px-6 py-4 bg-white border-t border-[#dde6ff]">
            <form onSubmit={handleSend} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  placeholder="Customer ID (optional)"
                  value={customerId || ''}
                  onChange={e => setCustomerId(e.target.value ? parseInt(e.target.value) : undefined)}
                  className="input-gemini text-xs py-2"
                />
                <input
                  type="text"
                  placeholder="Order Number e.g. ORD-1001"
                  value={orderNumber || ''}
                  onChange={e => setOrderNumber(e.target.value || undefined)}
                  className="input-gemini text-xs py-2"
                />
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={transcript || messageText}
                  onChange={e => setMessageText(e.target.value)}
                  placeholder={voiceActive ? '🎙️ Listening...' : 'Describe your refund request...'}
                  className="input-gemini flex-1"
                  disabled={!isConnected}
                />
                <button type="button" onClick={toggleVoice} disabled={!voiceController.isSupported()}
                  className={`w-11 h-11 rounded-xl flex items-center justify-center transition-all shrink-0 ${
                    voiceActive
                      ? 'bg-red-500 text-white shadow-lg scale-105'
                      : 'bg-[#f0f4ff] text-[#4a5a8a] hover:bg-[#dde6ff] border border-[#dde6ff]'
                  }`}
                >
                  {voiceActive ? <MicOff size={16} /> : <Mic size={16} />}
                </button>
                <button type="submit" disabled={!isConnected || isProcessing}
                  className="btn-gemini px-5 flex items-center gap-2 shrink-0 h-11"
                >
                  {isProcessing ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
                  {isProcessing ? 'Processing' : 'Send'}
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* ─── Pipeline Panel ─── */}
        {/* ─── Pipeline Panel (Admin Only) ─── */}
        {user?.role === 'admin' && (
          <div className="w-72 flex flex-col bg-white overflow-y-auto">
            <div className="px-5 py-4 border-b border-[#dde6ff]">
              <h3 className="font-bold text-[#0d1b4b] text-sm">Live Agent Pipeline</h3>
              <p className="text-xs text-[#8a9bcc]">Real-time workflow status</p>
            </div>

            <div className="flex-1 px-4 py-4">
              <div className="space-y-1">
                {AGENTS.map((agent, idx) => {
                  const log = agentLogs.find(l => l.agent_name === agent.id)
                  const isDone = !!log
                  const isActive = isProcessing && agentLogs.length === idx
                  const Icon = agent.icon

                  return (
                    <div key={agent.id}>
                      <div
                        className={`relative flex items-start gap-3 p-3 rounded-xl transition-all duration-300 ${
                          isDone ? 'bg-[#f0f4ff]' : isActive ? 'bg-[#fffbeb] border border-[#fcd34d]/50' : 'opacity-50'
                        }`}
                        style={isDone ? { animationDelay: `${idx * 100}ms` } : {}}
                      >
                        {/* Icon */}
                        <div
                          className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-all ${
                            isDone ? 'shadow-md' : isActive ? 'animate-pulse' : ''
                          }`}
                          style={{ background: isDone || isActive ? `${agent.color}18` : '#f0f4ff', border: `1.5px solid ${isDone || isActive ? agent.color + '40' : '#dde6ff'}` }}
                        >
                          {isDone
                            ? <CheckCircle2 size={15} style={{ color: agent.color }} className="animate-check-pop" />
                            : isActive
                            ? <Loader2 size={15} style={{ color: agent.color }} className="animate-spin" />
                            : <Icon size={14} style={{ color: '#8a9bcc' }} />
                          }
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <p className={`text-xs font-semibold ${isDone ? 'text-[#0d1b4b]' : isActive ? 'text-[#d97706]' : 'text-[#8a9bcc]'}`}>
                            {agent.label}
                          </p>
                          {log && (
                            <p className="text-[10px] text-[#8a9bcc] mt-0.5 truncate">{log.output_summary}</p>
                          )}
                          {log && (
                            <div className="flex items-center gap-2 mt-1">
                              <div className="flex-1 h-1 bg-[#dde6ff] rounded-full overflow-hidden">
                                <div className="h-full rounded-full transition-all duration-500" style={{ width: `${log.confidence * 100}%`, background: agent.color }} />
                              </div>
                              <span className="text-[10px] text-[#8a9bcc] shrink-0">{formatDuration(log.duration_ms)}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Connector */}
                      {idx < AGENTS.length - 1 && (
                        <div className="flex items-center justify-center py-1">
                          <div className="flex flex-col items-center gap-0.5">
                            <div className={`w-px h-3 transition-all duration-500 ${agentLogs.length > idx ? 'bg-gradient-to-b from-[#1a73e8] to-[#4f46e5]' : 'bg-[#dde6ff]'}`} />
                            <ChevronRight size={10} className={agentLogs.length > idx ? 'text-[#1a73e8] rotate-90' : 'text-[#dde6ff] rotate-90'} />
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>

              {/* Final verdict */}
              {result && (
                <div className={`mt-4 p-4 rounded-xl border animate-scale-in text-center ${
                  result.decision === 'approved' ? 'bg-emerald-50 border-emerald-200' :
                  result.decision === 'denied'   ? 'bg-red-50 border-red-200' :
                                                   'bg-amber-50 border-amber-200'
                }`}>
                  <p className="text-xs font-semibold text-[#8a9bcc] mb-1">FINAL VERDICT</p>
                  <p className={`text-xl font-black uppercase tracking-wide ${
                    result.decision === 'approved' ? 'text-emerald-700' :
                    result.decision === 'denied'   ? 'text-red-700' :
                                                     'text-amber-700'
                  }`}>
                    {result.decision}
                  </p>
                </div>
              )}

              {/* Order hint */}
              <div className="mt-6 p-3 bg-[#f8faff] border border-[#dde6ff] rounded-xl">
                <p className="text-[10px] font-semibold text-[#8a9bcc] uppercase tracking-wide mb-1">Quick Test Orders</p>
                {['ORD-1001','ORD-1002','ORD-1003','ORD-1004','ORD-1005'].map(o => (
                  <button key={o} onClick={() => setOrderNumber(o)}
                    className="w-full text-left text-xs text-[#1a73e8] hover:text-[#4f46e5] py-0.5 font-mono transition-colors"
                  >
                    → {o}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  )
}
