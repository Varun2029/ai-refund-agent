import { useEffect, useRef } from 'react'
import AppLayout from '../components/layout/AppLayout'
import { Terminal, CheckCircle2, Shield, Brain, FileCheck, UserCheck, Sparkles } from 'lucide-react'
import { useAllAgentLogs } from '../hooks/useWebSocket'
import { formatDuration } from '../lib/utils'

const AGENTS = [
  { id: 'customer_agent', label: 'Understanding Request',  icon: UserCheck,  color: '#1a73e8' },
  { id: 'crm_agent',      label: 'Checking Records',       icon: Brain,      color: '#7c3aed' },
  { id: 'policy_agent',   label: 'Reviewing Policies',     icon: FileCheck,  color: '#059669' },
  { id: 'fraud_agent',    label: 'Security Check',         icon: Shield,     color: '#d97706' },
  { id: 'decision_agent', label: 'Making Decision',        icon: Sparkles,   color: '#1a73e8' },
]

export default function AgentLogsPage() {
  const { logs, isConnected } = useAllAgentLogs()
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  return (
    <AppLayout>
      <div className="flex flex-col h-[calc(100vh-4rem)] bg-[#0a0a0f]">
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#222236] bg-[#12121a]">
          <div className="flex items-center gap-3">
            <Terminal className="text-[#3b82f6]" size={20} />
            <div>
              <h1 className="font-bold text-[#f0f0f5]">Global Agent Reasoning Logs</h1>
              <p className="text-xs text-[#8888a0]">Real-time stream of all AI decisions across the platform</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-full ${isConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
              {isConnected ? 'Connected to Stream' : 'Connecting…'}
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 font-mono text-sm space-y-4">
          {logs.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center opacity-50">
              <Terminal size={48} className="text-[#55556a] mb-4" />
              <p className="text-[#8888a0]">Waiting for agent activity...</p>
            </div>
          ) : (
            logs.map((log, idx) => {
              const agentDef = AGENTS.find(a => a.id === log.agent_name) || AGENTS[0]
              const Icon = agentDef.icon
              return (
                <div key={idx} className="bg-[#1a1a2e] border border-[#2a2a40] rounded-xl p-4 animate-slide-up shadow-lg">
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center justify-between border-b border-[#2a2a40] pb-3">
                      <div className="flex items-center gap-2">
                        <Icon size={16} style={{ color: agentDef.color }} />
                        <span className="font-bold text-[#f0f0f5]">{agentDef.label}</span>
                        <span className="text-xs text-[#55556a]">[{log.agent_name}]</span>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-[#8888a0]">
                        <span>Confidence: {(log.confidence * 100).toFixed(1)}%</span>
                        <span>{formatDuration(log.duration_ms)}</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs text-[#55556a] uppercase tracking-wider font-semibold block mb-1">Input Context</span>
                        <p className="text-[#8888a0] text-xs leading-relaxed">{log.input_summary}</p>
                      </div>
                      <div>
                        <span className="text-xs text-[#55556a] uppercase tracking-wider font-semibold block mb-1">Action Result</span>
                        <p className="text-[#f0f0f5] text-xs leading-relaxed font-semibold">{log.output_summary}</p>
                      </div>
                    </div>
                    
                    <div className="bg-[#0a0a0f] border border-[#222236] rounded-lg p-3 mt-1">
                      <span className="text-xs text-[#55556a] uppercase tracking-wider font-semibold block mb-1">Chain of Thought</span>
                      <p className="text-emerald-400 text-xs leading-relaxed">{log.reasoning}</p>
                    </div>
                  </div>
                </div>
              )
            })
          )}
          <div ref={logsEndRef} />
        </div>
      </div>
    </AppLayout>
  )
}
