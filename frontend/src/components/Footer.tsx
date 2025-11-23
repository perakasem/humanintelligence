import { Link } from 'react-router-dom'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-stone-50 border-t border-stone-100 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="text-sm text-stone-500">
            © {currentYear} HI FI
          </div>

          <div className="flex items-center gap-6">
            <Link to="/about" className="text-sm text-stone-500 hover:text-primary-600 transition-colors">
              About
            </Link>
            <a
              href="mailto:support@studentfinancecoach.com"
              className="text-sm text-stone-500 hover:text-primary-600 transition-colors"
            >
              Contact
            </a>
          </div>
        </div>

        <div className="mt-6 pt-6 border-t border-stone-100 text-center">
          <p className="text-xs text-stone-400 max-w-xl mx-auto">
            This app provides educational financial guidance only. It is not a substitute for professional financial advice.
          </p>
        </div>
      </div>
    </footer>
  )
}
