import { useLocation } from 'react-router-dom'
import { Cpu } from 'lucide-react'

const PAGE_META: Record<string, { title: string; subtitle: string }> = {
  '/chat':        { title: 'Customer Chat',       subtitle: 'AI-powered refund assistant' },
  '/dashboard':   { title: 'Manager Dashboard',   subtitle: 'Live operations overview' },
  '/analytics':   { title: 'Analytics & Insights',subtitle: 'Refund trends & metrics' },
  '/escalations': { title: 'Escalations',          subtitle: 'Cases requiring human review' },
  '/agent-logs':  { title: 'Agent Logs',           subtitle: 'Real-time reasoning traces' },
}

export default function Header() {
  const location = useLocation()
  const key = Object.keys(PAGE_META).find(k => location.pathname.startsWith(k))
  const meta = key ? PAGE_META[key] : { title: 'Dashboard', subtitle: '' }

  return (
    <header className="h-16 bg-white border-b border-[#dde6ff] flex items-center justify-between px-6 sticky top-0 z-10 shadow-sm">
      <div className="flex items-center gap-3 animate-fade-in">
        <div>
          <h2 className="text-base font-bold text-[#0d1b4b] leading-tight">{meta.title}</h2>
          {meta.subtitle && (
            <p className="text-xs text-[#8a9bcc] font-medium">{meta.subtitle}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          All Systems Online
        </span>
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] flex items-center justify-center shadow">
          <Cpu size={14} className="text-white" />
        </div>
      </div>
    </header>
  )
}
