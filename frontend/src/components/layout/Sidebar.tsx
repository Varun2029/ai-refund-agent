import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../lib/auth'
import { MessageSquare, LayoutDashboard, BarChart3, AlertTriangle, Terminal, LogOut, Sparkles } from 'lucide-react'

const adminNavItems = [
  { name: 'Dashboard',   path: '/dashboard',   icon: LayoutDashboard },
  { name: 'Analytics',   path: '/analytics',   icon: BarChart3 },
  { name: 'Escalations', path: '/escalations', icon: AlertTriangle },
  { name: 'Agent Logs',  path: '/agent-logs',  icon: Terminal },
]

const customerNavItems = [
  { name: 'Chat',        path: '/chat',        icon: MessageSquare },
  { name: 'My Escalations', path: '/escalations', icon: AlertTriangle },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="w-64 h-screen bg-white border-r border-[#dde6ff] flex flex-col shadow-sm" style={{ animation: 'slide-in-left 0.4s cubic-bezier(0.16,1,0.3,1) both' }}>
      {/* Logo */}
      <div className="px-6 py-5 border-b border-[#dde6ff]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] flex items-center justify-center shadow-lg">
            <Sparkles size={18} className="text-white" />
          </div>
          <div>
            <h1 className="font-bold text-[#0d1b4b] text-[15px] leading-tight">Refund AI</h1>
            <p className="text-[11px] text-[#8a9bcc] font-medium">Multi-Agent Platform</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {(user?.role === 'customer' ? customerNavItems : adminNavItems).map((item, i) => {
          const isActive = location.pathname.startsWith(item.path)
          const Icon = item.icon
          return (
            <Link
              key={item.path}
              to={item.path}
              style={{ animationDelay: `${i * 60}ms` }}
              className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 animate-fade-in ${
                isActive ? 'nav-active' : 'nav-inactive'
              }`}
            >
              <Icon size={17} strokeWidth={isActive ? 2.5 : 2} />
              <span>{item.name}</span>
              {isActive && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-[#1a73e8]" />
              )}
            </Link>
          )
        })}
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-[#dde6ff]">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] flex items-center justify-center text-white text-sm font-bold shadow-md">
            {user?.full_name?.charAt(0) ?? 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-[#0d1b4b] truncate">{user?.full_name}</p>
            <p className="text-xs text-[#8a9bcc] capitalize">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-[#f8faff] hover:bg-red-50 hover:text-red-600 text-[#4a5a8a] text-sm rounded-xl transition-all duration-200 border border-[#dde6ff] hover:border-red-200"
        >
          <LogOut size={14} />
          Sign Out
        </button>
      </div>
    </div>
  )
}
