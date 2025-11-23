import { useState } from 'react'
import type { IntakeResponse } from '../types'

interface SummaryWalkthroughProps {
  data: IntakeResponse
  onComplete: () => void
}

export default function SummaryWalkthrough({ data, onComplete }: SummaryWalkthroughProps) {
  const [currentSlide, setCurrentSlide] = useState(0)

  const { analytics, risk_scores, summary } = {
    analytics: data.analytics,
    risk_scores: {
      overspending_prob: data.overspending_prob,
      financial_stress_prob: data.financial_stress_prob,
    },
    summary: data.summary,
  }

  const isHealthy = !analytics.is_overspending && risk_scores.financial_stress_prob < 0.4

  // Define slides
  const slides = [
    // Slide 1: The big picture
    {
      content: (
        <div className="text-center">
          <p className="text-stone-500 text-sm uppercase tracking-wide mb-6">Your Monthly Balance</p>
          <p className={`text-6xl md:text-7xl font-serif font-bold mb-4 ${
            analytics.is_overspending ? 'text-primary-600' : 'text-accent-600'
          }`}>
            {analytics.is_overspending ? '-' : '+'}${Math.abs(analytics.net_balance)}
          </p>
          <p className="text-stone-600 text-lg">
            {analytics.is_overspending
              ? 'You\'re spending more than you bring in each month'
              : 'You have room to save or invest'}
          </p>
        </div>
      ),
    },
    // Slide 2: Financial stress insight (primary focus)
    {
      content: (
        <div className="text-center">
          <p className="text-stone-500 text-sm uppercase tracking-wide mb-6">Financial Wellbeing</p>
          <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full mb-6 ${
            isHealthy ? 'bg-accent-100' : 'bg-primary-100'
          }`}>
            <span className="text-5xl">
              {isHealthy ? '✓' : '💭'}
            </span>
          </div>
          <p className={`text-2xl font-serif font-semibold mb-3 ${
            isHealthy ? 'text-accent-700' : 'text-primary-700'
          }`}>
            {isHealthy
              ? 'Looking Good'
              : `${Math.round(risk_scores.financial_stress_prob * 100)}% Stress Risk`}
          </p>
          <p className="text-stone-600 max-w-sm mx-auto">
            {isHealthy
              ? 'Your financial situation appears stable. Small optimizations can help you build savings.'
              : 'Financial uncertainty may be affecting your wellbeing. Let\'s work on building stability.'}
          </p>
        </div>
      ),
    },
    // Slide 3: Key action
    {
      content: (
        <div className="text-center">
          <p className="text-stone-500 text-sm uppercase tracking-wide mb-6">Your First Focus</p>
          <div className="bg-cream-100 rounded-2xl p-6 mb-6 max-w-md mx-auto">
            <p className="text-xl font-serif font-medium text-stone-800">
              {summary.key_points[0] || 'Track your daily spending to identify patterns'}
            </p>
          </div>
          <p className="text-stone-500 text-sm">
            Your coach will help you work on this and more
          </p>
        </div>
      ),
    },
  ]

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1)
    } else {
      onComplete()
    }
  }

  const handlePrev = () => {
    if (currentSlide > 0) {
      setCurrentSlide(currentSlide - 1)
    }
  }

  return (
    <div className="fixed inset-0 bg-cream-50 z-50 flex flex-col">
      {/* Progress dots */}
      <div className="pt-8 pb-4 flex justify-center gap-2">
        {slides.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentSlide(index)}
            className={`w-2 h-2 rounded-full transition-all ${
              index === currentSlide
                ? 'bg-primary-600 w-6'
                : index < currentSlide
                  ? 'bg-primary-300'
                  : 'bg-stone-200'
            }`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>

      {/* Slide content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-lg animate-fade-in" key={currentSlide}>
          {slides[currentSlide].content}
        </div>
      </div>

      {/* Navigation */}
      <div className="p-8 flex justify-between items-center max-w-lg mx-auto w-full">
        <button
          onClick={handlePrev}
          className={`px-6 py-3 rounded-xl font-medium transition-all ${
            currentSlide === 0
              ? 'opacity-0 pointer-events-none'
              : 'text-stone-600 hover:bg-stone-100'
          }`}
        >
          Back
        </button>

        <button
          onClick={handleNext}
          className="btn btn-primary px-8 py-3"
        >
          {currentSlide === slides.length - 1 ? 'View Dashboard' : 'Continue'}
        </button>
      </div>
    </div>
  )
}
