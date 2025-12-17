import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Campaigns from './pages/Campaigns'
import Contacts from './pages/Contacts'
import Calls from './pages/Calls'
import Agents from './pages/Agents'
import Queues from './pages/Queues'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import Profile from './pages/Profile'

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useSelector((state) => state.auth)
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <Layout>{children}</Layout>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/campaigns"
        element={
          <ProtectedRoute>
            <Campaigns />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/contacts"
        element={
          <ProtectedRoute>
            <Contacts />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/calls"
        element={
          <ProtectedRoute>
            <Calls />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/agents"
        element={
          <ProtectedRoute>
            <Agents />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/queues"
        element={
          <ProtectedRoute>
            <Queues />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <Reports />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App
