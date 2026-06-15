import AppLayout from '../components/layout/AppLayout'
import { Terminal } from 'lucide-react'

export default function AgentLogsPage() {
  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto">
        <div className="card p-12 text-center animate-scale-in">
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] flex items-center justify-center shadow-lg">
            <Terminal size={24} className="text-white" />
          </div>
          <h2 className="text-xl font-bold text-[#0d1b4b] mb-2">Agent Reasoning Logs</h2>
          <p className="text-[#4a5a8a] text-sm">Real-time stream of agent decisions will appear here as you submit refund requests in the Chat tab.</p>
        </div>
      </div>
    </AppLayout>
  )
}
