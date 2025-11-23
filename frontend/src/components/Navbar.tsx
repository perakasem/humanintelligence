import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <nav className="sticky top-0 z-40 bg-white/80 backdrop-blur-sm border-b border-stone-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center gap-3">
              <div className="w-9 h-9 bg-primary-600 rounded-xl flex items-center justify-center shadow-warm">
                <span className="text-white font-serif font-semibold text-sm">HF</span>
              </div>
              <span className="font-serif font-semibold text-stone-800 text-lg">HI FI</span>
            </Link>
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <>
                <Link
                  to="/profile"
                  className="text-sm text-stone-500 hover:text-primary-600"
                >
                  Profile
                </Link>
                <div className="flex items-center gap-3">
                  {user.picture && (
                    <img
                      src={user.picture}
                      alt={user.name || 'User'}
                      className="w-8 h-8 rounded-full ring-2 ring-stone-100"
                    />
                  )}
                  <span className="text-sm text-stone-600 hidden sm:block">
                    {user.name || user.email}
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="text-sm text-stone-500 hover:text-primary-600"
                >
                  Sign out
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
