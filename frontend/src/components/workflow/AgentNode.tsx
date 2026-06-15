import type { AgentLog } from '../../lib/ws'
import { getAgentColor, getAgentBgColor, formatDuration } from '../../lib/utils'

interface AgentNodeProps {
  name: string
  label: string
  icon: string
  isActive: boolean
  isDone: boolean
  log?: AgentLog
  isLast?: boolean
}

export default function AgentNode({ name, label, icon, isActive, isDone, log, isLast }: AgentNodeProps) {
  const colorClass = getAgentColor(name)
  const bgClass = getAgentBgColor(name)
  
  return (
    <div className="relative flex items-start gap-4 w-full">
      {/* Connecting line */}
      {!isLast && (
        <div className="absolute left-6 top-12 bottom-[-16px] w-0.5 bg-white/10">
          {isDone && <div className={`w-full h-full ${bgClass} opacity-50`}></div>}
          {isActive && (
            <div className="w-full h-1/2 bg-blue-500 animate-flow-down opacity-50"></div>
          )}
        </div>
      )}

      {/* Node Icon */}
      <div className={`relative z-10 w-12 h-12 rounded-full flex items-center justify-center text-xl transition-all duration-300 ${
        isActive 
          ? `${bgClass} ${colorClass} animate-pulse-glow scale-110` 
          : isDone 
            ? `${bgClass} text-white/90`
            : 'bg-white/5 border border-white/10 text-white/30'
      }`}>
        {icon}
        {isDone && !isActive && (
          <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-gray-900 flex items-center justify-center">
            <svg className="w-2 h-2 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )}
      </div>

      {/* Node Content */}
      <div className={`flex-1 pt-2 pb-6 transition-opacity duration-300 ${
        isActive || isDone ? 'opacity-100' : 'opacity-40'
      }`}>
        <div className="flex items-center justify-between mb-1">
          <h4 className={`font-semibold ${isActive || isDone ? 'text-white' : 'text-white/60'}`}>
            {label}
          </h4>
          {isActive && (
            <span className="text-xs font-medium text-blue-400 animate-pulse">Processing...</span>
          )}
          {isDone && log && (
            <span className="text-xs text-white/40">{formatDuration(log.duration_ms)}</span>
          )}
        </div>

        {log && (
          <div className="mt-2 text-sm">
            <div className="text-white/70 bg-white/5 rounded p-2 border border-white/10">
              <span className="text-white/40 block text-xs mb-1 uppercase tracking-wider">Action</span>
              {log.action}
            </div>
            {log.confidence > 0 && (
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-white/40">Confidence:</span>
                <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-500"
                    style={{ width: `${log.confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-white/70">
                  {Math.round(log.confidence * 100)}%
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
