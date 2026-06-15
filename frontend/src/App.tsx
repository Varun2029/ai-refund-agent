import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './lib/auth'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'
import AnalyticsPage from './pages/AnalyticsPage'
import EscalationsPage from './pages/EscalationsPage'
import AgentLogsPage from './pages/AgentLogsPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-blue-500 border-t-transparent"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-blue-500 border-t-transparent"></div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user?.role === 'customer') {
    return <Navigate to="/chat" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  const { isAuthenticated, user } = useAuth()

  return (
    <Routes>
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to={user?.role === 'admin' ? '/dashboard' : '/chat'} replace />
          ) : (
            <LoginPage />
          )
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? (
            <Navigate to={user?.role === 'admin' ? '/dashboard' : '/chat'} replace />
          ) : (
            <RegisterPage />
          )
        }
      />

      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/dashboard"
        element={
          <AdminRoute>
            <DashboardPage />
          </AdminRoute>
        }
      />

      <Route
        path="/analytics"
        element={
          <AdminRoute>
            <AnalyticsPage />
          </AdminRoute>
        }
      />

      <Route
        path="/escalations"
        element={
          <ProtectedRoute>
            <EscalationsPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/agent-logs"
        element={
          <AdminRoute>
            <AgentLogsPage />
          </AdminRoute>
        }
      />

      <Route path="/" element={<Navigate to={user?.role === 'admin' ? '/dashboard' : '/chat'} replace />} />
      <Route path="*" element={<Navigate to={user?.role === 'admin' ? '/dashboard' : '/chat'} replace />} />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
