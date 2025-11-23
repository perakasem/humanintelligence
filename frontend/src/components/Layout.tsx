import { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { getDashboard } from '../api'
import Navbar from './Navbar'
import TeacherChat from './TeacherChat'
import Footer from './Footer'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const { data: dashboardData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  // Hide teacher panel on certain pages or when user hasn't completed onboarding
  const hideTeacherPanel = ['/', '/about', '/onboarding'].includes(location.pathname) || !dashboardData?.has_data

  return (
    <div className="min-h-screen bg-cream-50 flex flex-col">
      <Navbar />

      <div className="flex-1 flex">
        {/* Main content */}
        <main className={`flex-1 px-4 sm:px-6 lg:px-8 py-8 ${hideTeacherPanel ? 'max-w-3xl mx-auto' : ''}`}>
          <div className={hideTeacherPanel ? '' : 'max-w-4xl mx-auto'}>
            {children}
          </div>
        </main>

        {/* Teacher chat panel - part of the flex layout, fills viewport */}
        {!hideTeacherPanel && (
          <aside className="hidden lg:block w-96 flex-shrink-0 border-l border-stone-200">
            <div className="sticky top-16 h-[calc(100vh-4rem)]">
              <TeacherChat />
            </div>
          </aside>
        )}
      </div>

      {/* Mobile: floating button to show chat (hidden on certain pages) */}
      {!hideTeacherPanel && (
        <div className="lg:hidden">
          <MobileChatButton />
        </div>
      )}

      {/* Footer */}
      <Footer />
    </div>
  )
}

function MobileChatButton() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-primary-600 text-white p-4 rounded-full shadow-lg hover:bg-primary-700 transition-all z-40"
        aria-label="Open teacher chat"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
          className="w-6 h-6"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z"
          />
        </svg>
      </button>

      {/* Mobile chat overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50">
          <div className="absolute inset-0 bg-black/50" onClick={() => setIsOpen(false)} />
          <div className="absolute inset-y-0 right-0 w-full sm:w-96">
            <TeacherChat onClose={() => setIsOpen(false)} />
          </div>
        </div>
      )}
    </>
  )
}
