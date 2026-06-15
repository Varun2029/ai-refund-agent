import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { register as registerAPI } from '../lib/api'
import { Sparkles, Mail, Lock, User, ArrowRight } from 'lucide-react'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    try {
      const response = await registerAPI(email, password, fullName)
      login(response.access_token, response.user)
      navigate('/chat')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%)' }}>
      {/* Decorative orbs */}
      <div className="gemini-orb" style={{ background: '#1a73e8', top: '-80px', left: '-80px' }} />
      <div className="gemini-orb" style={{ background: '#7c3aed', bottom: '-80px', right: '-80px' }} />
      
      {/* Main card */}
      <div className="relative z-10 w-full max-w-md mx-4 animate-scale-in">
        <div className="card card-elevated p-8">
          {/* Logo */}
          <div className="text-center mb-8">
            <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-br from-[#1a73e8] to-[#7c3aed] items-center justify-center mb-4 shadow-xl">
              <Sparkles size={28} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gemini mb-1">Create Account</h1>
            <p className="text-[#4a5a8a] text-sm font-medium">Join the AI Refund Platform</p>
          </div>

          {/* Form */}
          <form onSubmit={handleRegister} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-[#0d1b4b] mb-1.5">Full Name</label>
              <div className="relative">
                <User size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8a9bcc] pointer-events-none z-10" />
                <input
                  type="text"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  className="input-gemini"
                  style={{ paddingLeft: '2.75rem' }}
                  required
                  disabled={isLoading}
                  placeholder="John Doe"
                />
              </div>
            </div>

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
                  required
                  disabled={isLoading}
                  placeholder="john@example.com"
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
                  autoComplete="new-password"
                  required
                  disabled={isLoading}
                  placeholder="••••••••"
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
                  Creating account...
                </>
              ) : (
                <>
                  Sign Up
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-[#4a5a8a]">
              Already a member?{' '}
              <a href="/login" className="text-[#1a73e8] font-semibold hover:underline">
                Sign in
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
