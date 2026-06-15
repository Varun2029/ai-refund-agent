import type { AgentLog } from '../../lib/ws'
import AgentNode from './AgentNode'

interface WorkflowVisualizerProps {
  logs: AgentLog[]
  isComplete: boolean
}

export default function WorkflowVisualizer({ logs, isComplete }: WorkflowVisualizerProps) {
  const agents = [
    { id: 'customer_agent', label: 'Customer Triage', icon: '👤' },
    { id: 'crm_agent', label: 'CRM Verification', icon: '🔍' },
    { id: 'policy_agent', label: 'Policy Check', icon: '⚖️' },
    { id: 'fraud_agent', label: 'Fraud Assessment', icon: '🛡️' },
    { id: 'decision_agent', label: 'Final Decision', icon: '🎯' },
  ]

  // Find the currently active agent (last one in logs if not complete)
  const activeAgentId = !isComplete && logs.length > 0 
    ? logs[logs.length - 1].agent_name 
    : (logs.length === 0 && !isComplete ? 'customer_agent' : null)

  const processedAgentIds = new Set(logs.map(l => l.agent_name))

  return (
    <div className="bg-white/5 backdrop-blur-md rounded-2xl border border-white/10 p-6 shadow-xl h-full flex flex-col">
      <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
        <span className="text-blue-500">⚡</span> Live Workflow
      </h3>
      
      <div className="flex-1 overflow-y-auto pr-2">
        <div className="space-y-2">
          {agents.map((agent, index) => {
            const agentLog = [...logs].reverse().find(l => l.agent_name === agent.id)
            const isDone = processedAgentIds.has(agent.id) && activeAgentId !== agent.id
            const isActive = activeAgentId === agent.id

            return (
              <AgentNode
                key={agent.id}
                name={agent.id}
                label={agent.label}
                icon={agent.icon}
                isActive={isActive}
                isDone={isDone}
                log={agentLog}
                isLast={index === agents.length - 1}
              />
            )
          })}
        </div>
      </div>
    </div>
  )
}
