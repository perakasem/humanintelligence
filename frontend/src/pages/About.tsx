import { Link } from 'react-router-dom'

export default function About() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="py-6 px-4 border-b border-gray-100">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">HF</span>
            </div>
            <span className="font-semibold text-gray-900">HI FI</span>
          </Link>
          <Link
            to="/"
            className="btn btn-primary"
          >
            Get Started
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-4 py-16">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">About HI FI</h1>

        <div className="prose prose-lg text-gray-600">
          <section className="mb-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Why We Built This</h2>
            <p className="mb-4">
              Managing money as a student is hard. Between tuition, rent, food, and trying to have
              some semblance of a social life, it's easy to feel overwhelmed. Many students don't
              have access to financial education or personalized advice.
            </p>
            <p>
              We built HI FI to change that. Using AI and machine learning, we
              provide the kind of personalized financial guidance that used to be available only
              to those who could afford a financial advisor.
            </p>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">How It Works</h2>
            <ol className="list-decimal list-inside space-y-3">
              <li>
                <strong>Tell us about your finances</strong> through a quick, conversational form
              </li>
              <li>
                <strong>Our ML model analyzes your patterns</strong> to identify risks and
                opportunities
              </li>
              <li>
                <strong>Your AI coach explains everything</strong> in plain language and gives you
                specific actions
              </li>
              <li>
                <strong>Weekly check-ins track your progress</strong> and adapt recommendations
                over time
              </li>
            </ol>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Our Focus: Education</h2>
            <p className="mb-4">
              This isn't just about tracking expenses. We believe in financial literacy. That's why
              your AI coach doesn't just tell you what to do—it teaches you why, with mini lessons
              on topics like:
            </p>
            <ul className="list-disc list-inside space-y-2">
              <li>How student loan interest works</li>
              <li>Building an emergency fund</li>
              <li>The psychology of spending</li>
              <li>Budgeting strategies that actually work</li>
            </ul>
          </section>

          <section className="mb-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Privacy & Data</h2>
            <p className="mb-4">
              We take your privacy seriously. Here's what you should know:
            </p>
            <ul className="list-disc list-inside space-y-2">
              <li>
                <strong>Your data is used only for coaching.</strong> We don't sell it or use it
                for advertising.
              </li>
              <li>
                <strong>We use Google Sign-In</strong> so we never see or store your password.
              </li>
              <li>
                <strong>Your financial data is encrypted</strong> in transit and at rest.
              </li>
              <li>
                <strong>You can delete your account</strong> and all associated data at any time.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Get Started</h2>
            <p className="mb-6">
              Ready to take control of your finances? It's free, takes about 5 minutes to set up,
              and you'll have your first insights right away.
            </p>
            <Link
              to="/"
              className="btn btn-primary inline-block"
            >
              Start Your Financial Journey
            </Link>
          </section>
        </div>
      </main>
    </div>
  )
}
