import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Menu, LogOut } from 'lucide-react'
import { useState } from 'react'

export const Header = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="bg-primary text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold">
          🔍 Tool-21
        </Link>
        
        <nav className="hidden md:flex gap-8 items-center">
          <Link to="/" className="hover:text-gray-200">Dashboard</Link>
          <Link to="/audits" className="hover:text-gray-200">Audits</Link>
          <Link to="/analytics" className="hover:text-gray-200">Analytics</Link>
        </nav>

        <div className="flex items-center gap-4">
          <span className="text-sm">{user?.name || 'User'}</span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-secondary px-3 py-2 rounded hover:bg-red-600 transition"
          >
            <LogOut size={18} />
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
