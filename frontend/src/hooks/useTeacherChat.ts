import { useState, useCallback, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { sendTeacherMessage, getChatHistory } from '../api'
import type { ChatHistory, TeacherOutput } from '../types'

interface Message {
  id: string
  type: 'user' | 'teacher'
  content: string
  teacherOutput?: TeacherOutput
  timestamp: Date
}

export function useTeacherChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [lastHistoryLength, setLastHistoryLength] = useState<number | null>(null)
  const queryClient = useQueryClient()

  // Load chat history
  const { data: historyData, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['chatHistory'],
    queryFn: () => getChatHistory(20),
  })

  // Process history data when it loads or changes
  useEffect(() => {
    if (historyData) {
      const currentLength = historyData.history.length

      // Only update if this is initial load or history was cleared
      if (lastHistoryLength === null || currentLength === 0 || (lastHistoryLength > 0 && currentLength === 0)) {
        const loadedMessages: Message[] = historyData.history.flatMap((item: ChatHistory) => [
          {
            id: `${item.interaction_id}-user`,
            type: 'user' as const,
            content: item.user_message,
            timestamp: new Date(item.created_at),
          },
          {
            id: `${item.interaction_id}-teacher`,
            type: 'teacher' as const,
            content: item.teacher_response.explanation,
            teacherOutput: item.teacher_response,
            timestamp: new Date(item.created_at),
          },
        ])
        setMessages(loadedMessages)
      }
      setLastHistoryLength(currentLength)
    }
  }, [historyData, lastHistoryLength])

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: sendTeacherMessage,
    onSuccess: (response) => {
      // Add teacher response
      const teacherMessage: Message = {
        id: `${response.interaction_id}-teacher`,
        type: 'teacher',
        content: response.teacher_output.explanation,
        teacherOutput: response.teacher_output,
        timestamp: new Date(response.created_at),
      }
      setMessages((prev) => [...prev, teacherMessage])

      // Invalidate chat history cache
      queryClient.invalidateQueries({ queryKey: ['chatHistory'] })

      // If field updates were processed, invalidate dashboard to show new data
      if (response.teacher_output.field_updates && response.teacher_output.field_updates.length > 0) {
        queryClient.invalidateQueries({ queryKey: ['dashboard'] })
      }
    },
  })

  const sendMessage = useCallback(
    async (content: string, snapshotId?: string) => {
      // Add user message immediately
      const userMessage: Message = {
        id: `temp-${Date.now()}`,
        type: 'user',
        content,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, userMessage])

      // Send to API
      await sendMutation.mutateAsync({
        user_message: content,
        snapshot_id: snapshotId,
      })
    },
    [sendMutation]
  )

  return {
    messages,
    sendMessage,
    isLoading: isLoadingHistory,
    isSending: sendMutation.isPending,
  }
}
