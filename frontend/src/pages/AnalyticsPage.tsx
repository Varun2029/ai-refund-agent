import { useState, useEffect } from 'react'
import AppLayout from '../components/layout/AppLayout'
import { TrendingUp, AlertTriangle, Users } from 'lucide-react'
import { getRefundAnalytics, getFraudAnalytics, getAgentAnalytics } from '../lib/api'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts'

export default function AnalyticsPage() {
  const [refundData, setRefundData] = useState<any[]>([])
  const [fraudData, setFraudData] = useState<any[]>([])
  const [agentData, setAgentData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getRefundAnalytics(),
      getFraudAnalytics(),
      getAgentAnalytics()
    ]).then(([refunds, fraud, agents]) => {
      setRefundData(refunds)
      setFraudData(fraud)
      setAgentData(agents)
    }).finally(() => setLoading(false))
  }, [])



  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-[#0d1b4b]">Analytics & Insights</h1>
          <p className="text-[#4a5a8a] mt-1 text-sm">System performance and refund trend analysis</p>
        </div>

        {loading ? (
          <div className="h-64 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-[#1a73e8] border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Refund Volume Chart */}
            <div className="card p-5 animate-slide-up">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#eff6ff] flex items-center justify-center">
                  <TrendingUp size={16} className="text-[#1a73e8]" />
                </div>
                <h3 className="font-bold text-[#0d1b4b]">Refund Volume</h3>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={refundData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#dde6ff" vertical={false} />
                    <XAxis dataKey="date" stroke="#8a9bcc" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#8a9bcc" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #dde6ff', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                    <Legend iconType="circle" />
                    <Area type="monotone" dataKey="approved" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
                    <Area type="monotone" dataKey="denied" stackId="1" stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.2} />
                    <Area type="monotone" dataKey="escalated" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Fraud Distribution Chart */}
            <div className="card p-5 animate-slide-up" style={{ animationDelay: '100ms' }}>
              <div className="flex items-center gap-2 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#fffbeb] flex items-center justify-center">
                  <AlertTriangle size={16} className="text-[#d97706]" />
                </div>
                <h3 className="font-bold text-[#0d1b4b]">Fraud Score Distribution</h3>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={fraudData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#dde6ff" vertical={false} />
                    <XAxis dataKey="range_label" stroke="#8a9bcc" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#8a9bcc" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: '#f8faff' }} contentStyle={{ borderRadius: '12px', border: '1px solid #dde6ff' }} />
                    <Bar dataKey="count" name="Refund Requests" fill="#d97706" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Agent Performance Chart */}
            <div className="card p-5 animate-slide-up lg:col-span-2" style={{ animationDelay: '200ms' }}>
              <div className="flex items-center gap-2 mb-6">
                <div className="w-8 h-8 rounded-lg bg-[#faf5ff] flex items-center justify-center">
                  <Users size={16} className="text-[#7c3aed]" />
                </div>
                <h3 className="font-bold text-[#0d1b4b]">Agent Performance</h3>
              </div>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={agentData} layout="vertical" margin={{ left: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#dde6ff" horizontal={false} />
                    <XAxis type="number" stroke="#8a9bcc" fontSize={12} tickLine={false} axisLine={false} unit="ms" />
                    <YAxis dataKey="agent_name" type="category" stroke="#0d1b4b" fontSize={12} fontWeight="500" tickLine={false} axisLine={false} />
                    <Tooltip cursor={{ fill: '#f8faff' }} contentStyle={{ borderRadius: '12px', border: '1px solid #dde6ff' }} />
                    <Bar dataKey="avg_duration_ms" name="Avg Duration (ms)" fill="#7c3aed" radius={[0, 4, 4, 0]} barSize={24} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>
        )}
      </div>
    </AppLayout>
  )
}
