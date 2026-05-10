import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './hooks/ProtectedRoute'
import ErrorBoundary from './hooks/ErrorBoundary'
import { Header } from './components/Header'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { AuditListPage } from './pages/AuditListPage'
import { DetailPage } from './pages/DetailPage'
import { CreateEditPage } from './pages/CreateEditPage'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <>
                    <Header />
                    <DashboardPage />
                  </>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/audits"
              element={
                <ProtectedRoute>
                  <>
                    <Header />
                    <AuditListPage />
                  </>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/audits/new"
              element={
                <ProtectedRoute>
                  <>
                    <Header />
                    <CreateEditPage />
                  </>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/audits/:id"
              element={
                <ProtectedRoute>
                  <>
                    <Header />
                    <DetailPage />
                  </>
                </ProtectedRoute>
              }
            />
            
            <Route
              path="/audits/:id/edit"
              element={
                <ProtectedRoute>
                  <>
                    <Header />
                    <CreateEditPage isEdit={true} />
                  </>
                </ProtectedRoute>
              }
            />
            
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
