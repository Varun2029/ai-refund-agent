import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { login as loginAPI } from '../lib/api'
import { Sparkles, Mail, Lock, ArrowRight, Zap } from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [role, setRole] = useState<'admin' | 'customer'>('customer')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Handle role toggle
  function handleRoleChange(newRole: 'admin' | 'customer') {
    setRole(newRole)
    if (newRole === 'admin') {
      setEmail('admin@refundai.com')
      setPassword('admin123')
    } else {
      setEmail('')
      setPassword('')
    }
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      const response = await loginAPI(email, password)
      login(response.access_token, response.user)
      navigate('/chat')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%)' }}>
      {/* Decorative orbs */}
      <div className="gemini-orb" style={{ background: '#1a73e8', top: '-80px', left: '-80px' }} />
      <div className="gemini-orb" style={{ background: '#7c3aed', bottom: '-80px', right: '-80px' }} />
      <div className="gemini-orb" style={{ background: '#0891b2', top: '40%', left: '60%', width: '200px', height: '200px' }} />

      {/* Floating feature pills */}
      <div className="absolute top-12 left-12 animate-slide-in-left delay-300 hidden lg:flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-md border border-[#dde6ff] text-sm text-[#4a5a8a] font-medium">
        <Zap size={14} className="text-[#1a73e8]" />
        5 AI Agents Working in Parallel
      </div>

      {/* Main card */}
      <div className="relative z-10 w-full max-w-md mx-4 animate-scale-in">
        <div className="card card-elevated p-8">
          {/* Logo */}
          <div className="text-center mb-6">
            <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] items-center justify-center mb-4 shadow-xl" style={{ animation: 'pulse-ring 2s ease-out infinite' }}>
              <Sparkles size={28} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gemini mb-1">Refund AI</h1>
            <p className="text-[#4a5a8a] text-sm font-medium">Multi-Agent Customer Operations Platform</p>
          </div>

          {/* Role Toggle */}
          <div className="flex rounded-xl bg-[#f0f4ff] p-1 mb-6 border border-[#dde6ff]">
            <button
              type="button"
              onClick={() => handleRoleChange('customer')}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                role === 'customer'
                  ? 'bg-white text-[#1a73e8] shadow-sm'
                  : 'text-[#8a9bcc] hover:text-[#4a5a8a]'
              }`}
            >
              Customer
            </button>
            <button
              type="button"
              onClick={() => handleRoleChange('admin')}
              className={`flex-1 py-2 text-sm font-semibold rounded-lg transition-all ${
                role === 'admin'
                  ? 'bg-white text-[#1a73e8] shadow-sm'
                  : 'text-[#8a9bcc] hover:text-[#4a5a8a]'
              }`}
            >
              Admin
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-[#0d1b4b] mb-1.5">Email</label>
              <div className="relative">
                <Mail size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8a9bcc] pointer-events-none z-10" />
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  className="input-gemini"
                  style={{ paddingLeft: '2.75rem' }}
                  autoComplete="email"
                  disabled={isLoading}
                  placeholder={role === 'customer' ? "you@example.com" : ""}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-[#0d1b4b] mb-1.5">Password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8a9bcc] pointer-events-none z-10" />
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="input-gemini"
                  style={{ paddingLeft: '2.75rem' }}
                  autoComplete="current-password"
                  disabled={isLoading}
                />
              </div>
            </div>

            {error && (
              <div className="animate-slide-up px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm font-medium">
                {error}
              </div>
            )}

            <button type="submit" disabled={isLoading} className="btn-gemini w-full flex items-center justify-center gap-2 mt-2">
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  Sign In
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Register Link / Info text */}
          <div className="mt-6 text-center">
            {role === 'customer' ? (
              <p className="text-sm text-[#4a5a8a]">
                New customer?{' '}
                <a href="/register" className="text-[#1a73e8] font-semibold hover:underline">
                  Create an account
                </a>
              </p>
            ) : (
              <p className="text-sm text-[#8a9bcc]">
                Admins log in with organizational email
              </p>
            )}
          </div>

          {/* Feature list */}
          <div className="mt-4 grid grid-cols-2 gap-2">
            {['RAG Policy Engine', 'Fraud Detection', 'Live Agent Logs', 'Voice Interface'].map((feat, i) => (
              <div key={feat} className={`flex items-center gap-1.5 text-xs text-[#4a5a8a] animate-fade-in delay-${(i + 1) * 100}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-[#1a73e8] to-[#7c3aed]" />
                {feat}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
