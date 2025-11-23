import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { submitIntake } from '../api'
import { getNextQuestion } from '../api/survey'
import SummaryWalkthrough from '../components/SummaryWalkthrough'
import type { RawAnswer, IntakeResponse } from '../types'

export default function Onboarding() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [collectedFields, setCollectedFields] = useState<string[]>([])
  const [collectedAnswers, setCollectedAnswers] = useState<Record<string, string>>({})
  const [currentField, setCurrentField] = useState<string | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState<{
    question: string
    context?: string
    suggested_type?: string
    options?: string[]
  } | null>(null)
  const [input, setInput] = useState('')
  const [progress, setProgress] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [showWalkthrough, setShowWalkthrough] = useState(false)
  const [intakeResult, setIntakeResult] = useState<IntakeResponse | null>(null)

  // Submit intake mutation
  const intakeMutation = useMutation({
    mutationFn: submitIntake,
    onSuccess: (data) => {
      // Store the result and show walkthrough
      setIntakeResult(data)
      setShowWalkthrough(true)
      // Invalidate dashboard cache so it fetches fresh data
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
    onError: (error: any) => {
      console.error('Failed to submit intake:', error)
      const message = error.response?.data?.detail || error.message || 'Failed to submit. Please try again.'
      setSubmitError(message)
    }
  })

  const handleWalkthroughComplete = () => {
    setShowWalkthrough(false)
    navigate('/dashboard')
  }

  // Load first question on mount
  useEffect(() => {
    loadNextQuestion([], {})
  }, [])

  const loadNextQuestion = async (fields: string[], answers: Record<string, string>) => {
    setIsLoading(true)
    try {
      const response = await getNextQuestion({
        conversation: [],
        collected_fields: fields
      })

      if (response.is_complete) {
        setIsComplete(true)
        setCurrentQuestion(null)
        setCurrentField(null)
      } else if (response.question) {
        setCurrentField(response.field)
        setCurrentQuestion({
          question: response.question,
          context: response.context || undefined,
          suggested_type: response.suggested_type || undefined,
          options: response.options || undefined
        })
        setProgress(response.progress)
      }
    } catch (error) {
      console.error('Failed to load question:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const isInputValid = () => {
    if (!input.trim()) return false

    // Validate age range
    if (currentField === 'age') {
      const age = parseInt(input)
      if (isNaN(age) || age < 16 || age > 100) return false
    }

    return true
  }

  const handleNext = () => {
    if (!currentField || !isInputValid()) return

    const newAnswers = {
      ...collectedAnswers,
      [currentField]: input.trim()
    }
    const newFields = [...collectedFields, currentField]

    setCollectedAnswers(newAnswers)
    setCollectedFields(newFields)
    setInput('')

    // Load next question with updated state
    loadNextQuestion(newFields, newAnswers)
  }

  const handleOptionSelect = (option: string) => {
    if (!currentField) return

    const newAnswers = {
      ...collectedAnswers,
      [currentField]: option
    }
    const newFields = [...collectedFields, currentField]

    setCollectedAnswers(newAnswers)
    setCollectedFields(newFields)
    setInput('')

    // Load next question with updated state
    loadNextQuestion(newFields, newAnswers)
  }

  const handleComplete = () => {
    setSubmitError(null)

    // Convert collected answers to raw answers format
    const rawAnswers: RawAnswer[] = Object.entries(collectedAnswers).map(([questionId, answer]) => ({
      question_id: questionId,
      answer
    }))

    intakeMutation.mutate({ raw_answers: rawAnswers })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && isInputValid()) {
      e.preventDefault()
      handleNext()
    }
  }

  if (isLoading && !currentQuestion) {
    return (
      <div className="min-h-screen bg-cream-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Show walkthrough after successful submission
  if (showWalkthrough && intakeResult) {
    return (
      <SummaryWalkthrough
        data={intakeResult}
        onComplete={handleWalkthroughComplete}
      />
    )
  }

  return (
    <div className="min-h-screen bg-cream-50 flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-stone-100 py-4 px-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex justify-between text-sm text-stone-500 mb-2">
            <span>Step {isComplete ? 17 : Math.min(collectedFields.length + 1, 17)} of 17</span>
            <span>{isComplete ? 100 : Math.round(progress * 100)}% complete</span>
          </div>
          <div className="w-full bg-stone-100 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${isComplete ? 100 : progress * 100}%` }}
            />
          </div>
        </div>
      </header>

      {/* Question */}
      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md animate-fade-in">
          {isComplete ? (
            <div className="bg-white rounded-2xl shadow-soft border border-stone-100 p-8 text-center">
              <h2 className="text-xl font-serif font-semibold text-stone-800 mb-4">
                All done!
              </h2>
              <p className="text-stone-600 mb-6">
                I've got everything I need. Let me analyze your finances and create your personalized dashboard.
              </p>
              {submitError && (
                <div className="bg-primary-50 border border-primary-200 text-primary-700 px-4 py-3 rounded-xl mb-4 text-sm">
                  {submitError}
                </div>
              )}
              <button
                onClick={handleComplete}
                disabled={intakeMutation.isPending}
                className="btn btn-primary w-full py-3 disabled:opacity-50"
              >
                {intakeMutation.isPending ? 'Analyzing...' : 'See My Dashboard'}
              </button>
            </div>
          ) : currentQuestion ? (
            <div className="bg-white rounded-2xl shadow-soft border border-stone-100 p-8">
              <h2 className="text-xl font-serif font-semibold text-stone-800 mb-2">
                {currentQuestion.question}
              </h2>
              {currentQuestion.context && (
                <p className="text-sm text-stone-500 mb-6">{currentQuestion.context}</p>
              )}

              {/* Input based on type */}
              {currentQuestion.options ? (
                <div className="space-y-3">
                  {currentQuestion.options.map((option) => (
                    <button
                      key={option}
                      onClick={() => handleOptionSelect(option)}
                      className="w-full p-4 text-left rounded-xl border border-stone-200 hover:border-primary-400 hover:bg-primary-50 transition-all text-stone-700"
                    >
                      {option}
                    </button>
                  ))}
                </div>
              ) : (
                <>
                  <input
                    type={currentQuestion.suggested_type === 'number' ? 'number' : 'text'}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your answer..."
                    className="input"
                    autoFocus
                    min={currentField === 'age' ? 16 : 0}
                    max={currentField === 'age' ? 100 : undefined}
                  />
                  {currentField === 'age' && (
                    <p className="text-xs text-stone-500 mt-1">Please enter an age between 16 and 100</p>
                  )}
                  <div className="flex justify-end mt-6">
                    <button
                      onClick={handleNext}
                      disabled={!isInputValid() || isLoading}
                      className="btn btn-primary disabled:opacity-50"
                    >
                      {isLoading ? 'Loading...' : 'Continue'}
                    </button>
                  </div>
                </>
              )}
            </div>
          ) : null}
        </div>
      </main>
    </div>
  )
}
