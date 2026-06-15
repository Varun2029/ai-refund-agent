import { getDashboardStats, getReviewQueue } from '../lib/api'
import { usePoll } from '../hooks/useWebSocket'
import { formatCurrency } from '../lib/utils'
import AppLayout from '../components/layout/AppLayout'
import { TrendingUp, ShieldCheck, Clock, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  const { data: stats } = usePoll(() => getDashboardStats(), 5000)
  const { data: queue } = usePoll(() => getReviewQueue(), 5000)

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[
            { title: 'Total Refunds',   value: stats?.total_refunds ?? '—',                 icon: TrendingUp,  color: '#1a73e8', bg: '#eff6ff' },
            { title: 'Approval Rate',   value: stats ? `${stats.approval_rate}%` : '—',     icon: ShieldCheck, color: '#16a34a', bg: '#f0fdf4' },
            { title: 'Avg Fraud Score', value: stats ? stats.avg_fraud_score?.toFixed(1) : '—', icon: AlertCircle, color: '#d97706', bg: '#fffbeb' },
            { title: 'Pending',         value: stats?.pending_refunds ?? '—',                icon: Clock,       color: '#7c3aed', bg: '#faf5ff' },
          ].map((s, i) => {
            const Icon = s.icon
            return (
              <div key={s.title} className={`card p-5 animate-slide-up delay-${(i + 1) * 100}`}>
                <div className="flex items-start justify-between mb-3">
                  <p className="text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">{s.title}</p>
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: s.bg }}>
                    <Icon size={16} style={{ color: s.color }} />
                  </div>
                </div>
                <p className="text-3xl font-black text-[#0d1b4b]">{s.value}</p>
              </div>
            )
          })}
        </div>

        {/* Review Queue */}
        <div className="card overflow-hidden animate-slide-up delay-300">
          <div className="px-6 py-4 border-b border-[#dde6ff] flex items-center justify-between">
            <div>
              <h2 className="font-bold text-[#0d1b4b]">Review Queue</h2>
              <p className="text-xs text-[#8a9bcc]">{queue?.length ?? 0} items pending review</p>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#dde6ff] bg-[#f8faff]">
                  <th className="text-left px-6 py-3 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Order</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Customer</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Amount</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Fraud Score</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody>
                {!queue && (
                  <tr><td colSpan={5} className="px-6 py-8 text-center text-[#8a9bcc] text-sm">Loading…</td></tr>
                )}
                {queue?.length === 0 && (
                  <tr><td colSpan={5} className="px-6 py-8 text-center text-[#8a9bcc] text-sm">No items in queue</td></tr>
                )}
                {queue?.slice(0, 10).map((item: any, i: number) => (
                  <tr key={item.id} className={`border-b border-[#dde6ff] hover:bg-[#f8faff] transition-colors animate-fade-in`} style={{ animationDelay: `${i * 50}ms` }}>
                    <td className="px-6 py-3 font-mono text-xs text-[#1a73e8] font-semibold">{item.order_number}</td>
                    <td className="px-6 py-3 text-[#0d1b4b] font-medium">{item.customer_name}</td>
                    <td className="px-6 py-3 text-[#0d1b4b] font-semibold">{formatCurrency(item.refund_amount)}</td>
                    <td className="px-6 py-3">
                      <span className={`font-bold text-sm ${Number(item.fraud_score) > 70 ? 'text-red-600' : Number(item.fraud_score) > 40 ? 'text-amber-600' : 'text-emerald-600'}`}>
                        {item.fraud_score?.toFixed(1) ?? 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <span className={`badge badge-${item.status}`}>{item.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
