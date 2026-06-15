import { useState, useEffect } from 'react'
import AppLayout from '../components/layout/AppLayout'
import { XCircle, Search, Filter } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { getRefundHistory, listEscalations, resolveEscalation } from '../lib/api'

export default function EscalationsPage() {
  const { user } = useAuth()
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Admin escalation modal state
  const [selectedEscalation, setSelectedEscalation] = useState<any>(null)
  const [notes, setNotes] = useState('')
  const [resolving, setResolving] = useState(false)

  useEffect(() => {
    fetchData()
  }, [user])

  async function fetchData() {
    setLoading(true)
    setError(null)
    try {
      if (user?.role === 'customer') {
        const history = await getRefundHistory()
        setData(history)
      } else {
        const escalations = await listEscalations()
        setData(escalations)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  async function handleResolve(decision: 'approved' | 'denied') {
    if (!selectedEscalation) return
    setResolving(true)
    try {
      await resolveEscalation(selectedEscalation.id, decision, notes)
      setSelectedEscalation(null)
      setNotes('')
      fetchData()
    } catch (err) {
      alert('Failed to resolve escalation')
    } finally {
      setResolving(false)
    }
  }

  const isCustomer = user?.role === 'customer'

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto flex flex-col h-[calc(100vh-4rem)]">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-[#0d1b4b]">
              {isCustomer ? 'My Requests' : 'Escalations & Reviews'}
            </h1>
            <p className="text-[#4a5a8a] mt-1 text-sm">
              {isCustomer 
                ? 'Track your past and current refund requests'
                : 'Review cases that require human intervention'
              }
            </p>
          </div>
          
          <div className="flex gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-[#8a9bcc]" size={16} />
              <input type="text" placeholder="Search..." className="input-gemini pl-9 py-2 text-sm w-64" />
            </div>
            <button className="btn-secondary px-3 flex items-center gap-2 text-sm">
              <Filter size={16} /> Filter
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-[#1a73e8] border-t-transparent" />
          </div>
        ) : error ? (
          <div className="flex-1 flex items-center justify-center text-red-500">
            {error}
          </div>
        ) : (
          <div className="card overflow-hidden flex-1 flex flex-col">
            <div className="overflow-x-auto flex-1">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-[#dde6ff] bg-[#f8faff]">
                    <th className="p-4 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">ID</th>
                    {!isCustomer && <th className="p-4 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Customer</th>}
                    <th className="p-4 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Order</th>
                    <th className="p-4 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Reason</th>
                    <th className="p-4 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Status</th>
                    <th className="p-4 text-xs font-semibold text-[#8a9bcc] uppercase tracking-wider">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#dde6ff]">
                  {data.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="p-8 text-center text-[#8a9bcc]">No records found</td>
                    </tr>
                  ) : (
                    data.map((item) => (
                      <tr 
                        key={item.id} 
                        className="hover:bg-[#f0f4ff]/50 transition-colors cursor-pointer group"
                        onClick={() => !isCustomer && setSelectedEscalation(item)}
                      >
                        <td className="p-4 text-sm font-medium text-[#0d1b4b]">#{item.id}</td>
                        {!isCustomer && (
                          <td className="p-4 text-sm text-[#4a5a8a]">
                            {item.customer_id}
                          </td>
                        )}
                        <td className="p-4 text-sm text-[#4a5a8a]">{item.order_id || item.order_number || 'N/A'}</td>
                        <td className="p-4 text-sm text-[#4a5a8a] max-w-xs truncate">{item.reason || item.escalation_reason}</td>
                        <td className="p-4">
                          <span className={`badge ${
                            item.status === 'approved' || item.status === 'resolved' ? 'badge-approved' :
                            item.status === 'denied' ? 'badge-denied' :
                            item.status === 'escalated' ? 'badge-escalated' : 'badge-pending'
                          }`}>
                            {item.status.toUpperCase()}
                          </span>
                        </td>
                        <td className="p-4 text-sm text-[#8a9bcc]">
                          {new Date(item.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Admin Resolution Modal */}
      {selectedEscalation && !isCustomer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0d1b4b]/20 backdrop-blur-sm animate-fade-in">
          <div className="card max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl animate-scale-in">
            <div className="p-6 border-b border-[#dde6ff] flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-[#0d1b4b]">Resolve Escalation #{selectedEscalation.id}</h3>
                <p className="text-sm text-[#8a9bcc] mt-1">Review case details and make a final decision</p>
              </div>
              <button onClick={() => setSelectedEscalation(null)} className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-[#f0f4ff] text-[#8a9bcc] transition-colors">
                <XCircle size={20} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-[#f8faff] rounded-xl border border-[#dde6ff]">
                  <p className="text-xs font-semibold text-[#8a9bcc] uppercase mb-1">Reason for Escalation</p>
                  <p className="text-sm text-[#0d1b4b] font-medium">{selectedEscalation.escalation_reason || selectedEscalation.reason}</p>
                </div>
                <div className="p-4 bg-[#f8faff] rounded-xl border border-[#dde6ff]">
                  <p className="text-xs font-semibold text-[#8a9bcc] uppercase mb-1">Current Status</p>
                  <span className="badge badge-escalated">{selectedEscalation.status.toUpperCase()}</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-[#0d1b4b] mb-2">Resolution Notes</label>
                <textarea 
                  value={notes}
                  onChange={e => setNotes(e.target.value)}
                  className="input-gemini w-full h-32 resize-none"
                  placeholder="Enter reasoning for your decision..."
                />
              </div>
            </div>
            
            <div className="p-6 border-t border-[#dde6ff] bg-[#f8faff] flex justify-end gap-3">
              <button 
                onClick={() => setSelectedEscalation(null)}
                className="btn-secondary px-5"
                disabled={resolving}
              >
                Cancel
              </button>
              <button 
                onClick={() => handleResolve('denied')}
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-red-600 hover:bg-red-700 transition-colors disabled:opacity-50"
                disabled={resolving}
              >
                Deny Refund
              </button>
              <button 
                onClick={() => handleResolve('approved')}
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 transition-colors disabled:opacity-50"
                disabled={resolving}
              >
                Approve Refund
              </button>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  )
}
