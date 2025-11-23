import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getDashboard, clearUserData } from '../api'
import SpendingDonut from '../components/charts/SpendingDonut'
import RiskTrendLine from '../components/charts/RiskTrendLine'
import SummaryWalkthrough from '../components/SummaryWalkthrough'

type ViewMode = 'overview' | 'breakdown'

export default function Dashboard() {
  const queryClient = useQueryClient()
  const [isClearing, setIsClearing] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('overview')
  const [showWalkthrough, setShowWalkthrough] = useState(false)

  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  const handleClearData = async () => {
    if (!confirm('Are you sure you want to clear all your data? This cannot be undone.')) {
      return
    }

    setIsClearing(true)
    try {
      await clearUserData()
      // Invalidate both dashboard and chat history
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] })
    } catch (error) {
      console.error('Failed to clear data:', error)
      alert('Failed to clear data. Please try again.')
    } finally {
      setIsClearing(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-primary-700">Failed to load dashboard data.</p>
      </div>
    )
  }

  if (!data?.has_data) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-serif font-semibold text-stone-800 mb-4">Welcome!</h2>
        <p className="text-stone-600 mb-6">
          Complete your onboarding to get personalized financial insights.
        </p>
        <Link to="/onboarding" className="btn btn-primary">
          Start Onboarding
        </Link>
      </div>
    )
  }

  const { spending_breakdown, analytics, risk_scores, summary, history } = data

  // Show walkthrough if requested
  if (showWalkthrough && analytics && risk_scores && summary) {
    const walkthroughData = {
      snapshot_id: data.latest_snapshot_id || '',
      overspending_prob: risk_scores.overspending_prob,
      financial_stress_prob: risk_scores.financial_stress_prob,
      summary,
      analytics,
      created_at: new Date().toISOString(),
    }
    return (
      <SummaryWalkthrough
        data={walkthroughData}
        onComplete={() => setShowWalkthrough(false)}
      />
    )
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Pill Toggle */}
      <div className="flex items-center justify-center gap-4">
        <div className="inline-flex bg-stone-100 rounded-full p-1">
          <button
            onClick={() => setViewMode('overview')}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
              viewMode === 'overview'
                ? 'bg-white text-stone-800 shadow-sm'
                : 'text-stone-500 hover:text-stone-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setViewMode('breakdown')}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${
              viewMode === 'breakdown'
                ? 'bg-white text-stone-800 shadow-sm'
                : 'text-stone-500 hover:text-stone-700'
            }`}
          >
            Breakdown
          </button>
        </div>
        <button
          onClick={() => setShowWalkthrough(true)}
          className="text-stone-400 hover:text-stone-600 transition-colors"
          title="View summary slideshow"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 3v11.25A2.25 2.25 0 006 16.5h2.25M3.75 3h-1.5m1.5 0h16.5m0 0h1.5m-1.5 0v11.25A2.25 2.25 0 0118 16.5h-2.25m-7.5 0h7.5m-7.5 0l-1 3m8.5-3l1 3m0 0l.5 1.5m-.5-1.5h-9.5m0 0l-.5 1.5" />
          </svg>
        </button>
      </div>

      {viewMode === 'overview' ? (
        <>
          {/* Hero Section - Main Financial Status */}
          {analytics && (
            <div className="text-center py-8">
              <p className="text-stone-500 text-sm uppercase tracking-wide mb-3">Monthly Balance</p>
              <p className={`text-5xl md:text-6xl font-serif font-bold mb-2 ${
                analytics.is_overspending ? 'text-primary-600' : 'text-accent-600'
              }`}>
                {analytics.is_overspending ? '-' : '+'}${Math.abs(analytics.net_balance)}
              </p>
              <p className="text-stone-500">
                ${analytics.total_resources} in — ${analytics.total_spending} out
              </p>
            </div>
          )}

          {/* Summary Section */}
          {summary && (
            <div className="card">
              <h2 className="text-lg font-serif font-semibold text-stone-800 mb-4">Your Financial Summary</h2>
              <p className="text-stone-600 leading-relaxed mb-6">{summary.summary_paragraph}</p>
              <div className="space-y-3">
                {summary.key_points.map((point, index) => (
                  <div key={index} className="flex items-start gap-3 bg-cream-50 rounded-xl p-4">
                    <span className="text-accent-600 text-lg mt-0.5">→</span>
                    <p className="text-stone-700">{point}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Risk Indicator */}
          {risk_scores && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-serif font-semibold text-stone-800">Risk Overview</h3>
              </div>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-sm text-stone-600">Overspending</span>
                    <span className={`text-2xl font-serif font-bold ${
                      risk_scores.overspending_prob > 0.6 ? 'text-primary-600' :
                      risk_scores.overspending_prob > 0.3 ? 'text-primary-500' : 'text-accent-600'
                    }`}>
                      {Math.round(risk_scores.overspending_prob * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-stone-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        risk_scores.overspending_prob > 0.6 ? 'bg-primary-600' :
                        risk_scores.overspending_prob > 0.3 ? 'bg-primary-400' : 'bg-accent-500'
                      }`}
                      style={{ width: `${risk_scores.overspending_prob * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-baseline justify-between mb-2">
                    <span className="text-sm text-stone-600">Financial Stress</span>
                    <span className={`text-2xl font-serif font-bold ${
                      risk_scores.financial_stress_prob > 0.6 ? 'text-primary-600' :
                      risk_scores.financial_stress_prob > 0.3 ? 'text-primary-500' : 'text-accent-600'
                    }`}>
                      {Math.round(risk_scores.financial_stress_prob * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-stone-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-500 ${
                        risk_scores.financial_stress_prob > 0.6 ? 'bg-primary-600' :
                        risk_scores.financial_stress_prob > 0.3 ? 'bg-primary-400' : 'bg-accent-500'
                      }`}
                      style={{ width: `${risk_scores.financial_stress_prob * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Breakdown View - Charts */}
          <div className={`grid gap-6 ${history && history.length > 1 ? 'md:grid-cols-2' : 'md:grid-cols-1'}`}>
            {spending_breakdown && (
              <div className="card">
                <h3 className="text-lg font-serif font-semibold text-stone-800 mb-4">Spending Breakdown</h3>
                <SpendingDonut data={spending_breakdown} />
              </div>
            )}

            {history && history.length > 1 && (
              <div className="card">
                <h3 className="text-lg font-serif font-semibold text-stone-800 mb-4">Risk Trends</h3>
                <RiskTrendLine data={history} />
              </div>
            )}
          </div>

          {/* Show single chart message if no trends */}
          {(!history || history.length <= 1) && spending_breakdown && (
            <p className="text-center text-sm text-stone-500">
              Complete more check-ins to see your risk trends over time
            </p>
          )}
        </>
      )}

      {/* Monthly Check-in CTA */}
      <div className="card bg-accent-50/50 border-accent-100">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-serif font-semibold text-stone-800">Time for a check-in?</h3>
            <p className="text-sm text-stone-600">Update your numbers and see how you're progressing.</p>
          </div>
          <Link to="/onboarding" className="btn btn-primary whitespace-nowrap">
            Start Check-in
          </Link>
        </div>
      </div>

      {/* Debug Section - Minimal */}
      <div className="pt-8 border-t border-stone-100">
        <button
          onClick={handleClearData}
          disabled={isClearing}
          className="text-sm text-stone-400 hover:text-stone-600 transition-colors"
        >
          {isClearing ? 'Clearing...' : 'Reset all data'}
        </button>
      </div>
    </div>
  )
}
