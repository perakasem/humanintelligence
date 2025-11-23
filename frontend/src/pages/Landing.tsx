import { useEffect, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: object) => void
          renderButton: (element: HTMLElement, config: object) => void
        }
      }
    }
  }
}

export default function Landing() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleCredentialResponse = useCallback(
    async (response: { credential: string }) => {
      try {
        await login(response.credential)
        navigate('/dashboard')
      } catch (error) {
        console.error('Login failed:', error)
      }
    },
    [login, navigate]
  )

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID

    if (window.google && clientId) {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredentialResponse,
      })

      const buttonElement = document.getElementById('google-signin-button')
      if (buttonElement) {
        window.google.accounts.id.renderButton(buttonElement, {
          theme: 'outline',
          size: 'large',
          text: 'continue_with',
          width: 280,
        })
      }
    }
  }, [handleCredentialResponse])

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-50 to-white">
      {/* Header */}
      <header className="py-6 px-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">HF</span>
            </div>
            <span className="font-semibold text-gray-900">HI FI</span>
          </div>
          <Link to="/about" className="text-gray-600 hover:text-gray-900">
            About
          </Link>
        </div>
      </header>

      {/* Hero */}
      <main className="max-w-7xl mx-auto px-4 pt-20 pb-32">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
            Take control of your
            <span className="text-primary-600"> student finances</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Get personalized financial guidance powered by AI. Understand your spending,
            reduce stress, and build better money habits—all tailored for student life.
          </p>

          {/* Google Sign In */}
          <div className="flex flex-col items-center gap-4 mb-8">
            <div id="google-signin-button"></div>
            <p className="text-sm text-gray-500">
              Free to use. No credit card required.
            </p>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="text-center p-6">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Track Your Spending
            </h3>
            <p className="text-gray-600">
              See where your money goes with clear visualizations and breakdowns by category.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Get Risk Insights
            </h3>
            <p className="text-gray-600">
              Our ML model analyzes your patterns to identify overspending and stress risks.
            </p>
          </div>

          <div className="text-center p-6">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-6 h-6 text-primary-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Chat with Your Coach
            </h3>
            <p className="text-gray-600">
              Get personalized advice, action items, and mini lessons from your AI financial guide.
            </p>
          </div>
        </div>

        {/* Privacy note */}
        <div className="mt-20 text-center">
          <p className="text-sm text-gray-500">
            Your financial data is used only for guidance—never sold or shared for advertising.
            <br />
            <Link to="/about" className="text-primary-600 hover:underline">
              Learn more about our privacy practices
            </Link>
          </p>
        </div>
      </main>
    </div>
  )
}
