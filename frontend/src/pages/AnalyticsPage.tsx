import AppLayout from '../components/layout/AppLayout'
import { BarChart3 } from 'lucide-react'

export default function AnalyticsPage() {
  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto">
        <div className="card p-12 text-center animate-scale-in">
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-[#1a73e8] to-[#0891b2] flex items-center justify-center shadow-lg">
            <BarChart3 size={24} className="text-white" />
          </div>
          <h2 className="text-xl font-bold text-[#0d1b4b] mb-2">Analytics & Insights</h2>
          <p className="text-[#4a5a8a] text-sm">Charts for refund trends, fraud distribution, and agent performance will appear here as data is generated.</p>
        </div>
      </div>
    </AppLayout>
  )
}
