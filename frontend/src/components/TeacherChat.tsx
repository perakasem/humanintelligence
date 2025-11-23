import { useState, useRef, useEffect } from 'react'
import { useTeacherChat } from '../hooks/useTeacherChat'
import type { TeacherOutput } from '../types'

interface TeacherChatProps {
  onClose?: () => void  // Optional - only needed for mobile
}

export default function TeacherChat({ onClose }: TeacherChatProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { messages, sendMessage, isLoading, isSending } = useTeacherChat()

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`
    }
  }, [input])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isSending) return

    const message = input.trim()
    setInput('')
    await sendMessage(message)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter, allow Shift+Enter for new line
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="h-full bg-cream-50 flex flex-col border-l border-stone-100">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-stone-100 bg-white/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-accent-100 rounded-xl flex items-center justify-center">
            <span className="text-accent-600 text-lg">🌱</span>
          </div>
          <div>
            <h3 className="font-serif font-semibold text-stone-800">Finance Coach</h3>
            <p className="text-xs text-stone-500">Here to help</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 hover:bg-stone-100 rounded-lg transition-colors"
            aria-label="Close chat"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="w-5 h-5 text-stone-500"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="space-y-4">
            {/* Welcome message */}
            <div className="bg-accent-50 rounded-2xl p-4 border border-accent-100">
              <p className="text-sm text-stone-700 mb-3">
                Hey! I'm your finance coach. I'm here to help you understand your spending and build better money habits—no judgment, just support.
              </p>
              <p className="text-xs text-stone-600 font-medium">
                How I can help:
              </p>
              <ul className="text-xs text-stone-500 mt-1 space-y-1">
                <li>• Ask questions about your spending</li>
                <li>• Get bite-sized financial tips</li>
                <li>• Update me on changes (e.g., "I spent $300 on food")</li>
              </ul>
            </div>

            {/* Quick actions */}
            <div>
              <p className="text-xs text-stone-400 mb-2 uppercase tracking-wide font-medium">Try asking:</p>
              <div className="space-y-2">
                <button
                  onClick={() => sendMessage("What should I focus on this week?")}
                  className="w-full p-3 text-left text-sm bg-white rounded-xl hover:bg-stone-50 transition-colors border border-stone-100 text-stone-700"
                >
                  What should I focus on this week?
                </button>
                <button
                  onClick={() => sendMessage("How can I save more money?")}
                  className="w-full p-3 text-left text-sm bg-white rounded-xl hover:bg-stone-50 transition-colors border border-stone-100 text-stone-700"
                >
                  How can I save more money?
                </button>
                <button
                  onClick={() => sendMessage("Why is my overspending risk high?")}
                  className="w-full p-3 text-left text-sm bg-white rounded-xl hover:bg-stone-50 transition-colors border border-stone-100 text-stone-700"
                >
                  Why is my overspending risk high?
                </button>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white rounded-2xl rounded-br-md px-4 py-3 shadow-warm'
                    : 'bg-white rounded-2xl rounded-bl-md px-4 py-3 border border-stone-100'
                }`}
              >
                {message.type === 'user' ? (
                  <p className="text-sm">{message.content}</p>
                ) : (
                  <TeacherResponse output={message.teacherOutput} />
                )}
              </div>
            </div>
          ))
        )}

        {isSending && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl rounded-bl-md px-4 py-3 border border-stone-100">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-stone-300 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                <span className="w-2 h-2 bg-stone-300 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                <span className="w-2 h-2 bg-stone-300 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-stone-100 bg-white/50">
        <div className="flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask your finance coach..."
            className="flex-1 px-4 py-3 bg-white border border-stone-200 rounded-xl focus:ring-2 focus:ring-primary-300 focus:border-primary-400 resize-none min-h-[48px] max-h-[120px] text-stone-700 placeholder:text-stone-400"
            disabled={isSending}
            rows={1}
          />
          <button
            type="submit"
            disabled={!input.trim() || isSending}
            className="px-4 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex-shrink-0 shadow-warm"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-5 h-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
              />
            </svg>
          </button>
        </div>
      </form>
    </div>
  )
}

function TeacherResponse({ output }: { output?: TeacherOutput }) {
  if (!output) return null

  return (
    <div className="space-y-3 text-sm text-stone-800">
      {/* Explanation */}
      <p>{output.explanation}</p>

      {/* Actions */}
      {output.actions_for_week.length > 0 && (
        <div className="pt-2 border-t border-stone-100">
          <p className="font-medium text-stone-700 mb-2">This week's actions:</p>
          <ul className="space-y-1">
            {output.actions_for_week.map((action, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-accent-600 mt-0.5">✓</span>
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Lesson */}
      {output.lesson_outline && (
        <div className="pt-2 border-t border-stone-100">
          <p className="font-medium text-stone-700 mb-2">
            📚 {output.lesson_outline.title}
          </p>
          <ul className="space-y-1 text-stone-600">
            {output.lesson_outline.bullet_points.map((point, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-stone-400">•</span>
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
