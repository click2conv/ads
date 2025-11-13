import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getChatSessions, sendChatMessage, createChatSession } from '../services/api'
import { Send, MessageSquare, Plus } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Chat() {
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null)
  const [message, setMessage] = useState('')
  const [contextKeywords, setContextKeywords] = useState('')
  const [messages, setMessages] = useState<any[]>([])

  const { data: sessions } = useQuery({
    queryKey: ['chatSessions'],
    queryFn: getChatSessions,
  })

  const createSessionMutation = useMutation({
    mutationFn: createChatSession,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chatSessions'] })
      setCurrentSessionId(data.id)
      setMessages([])
      toast.success('New chat session created')
    },
  })

  const sendMessageMutation = useMutation({
    mutationFn: sendChatMessage,
    onSuccess: (data) => {
      // Add AI message to the list
      setMessages((prev) => [...prev, data])
      setMessage('')
      queryClient.invalidateQueries({ queryKey: ['chatSessions'] })
    },
    onError: () => {
      toast.error('Failed to send message')
    },
  })

  const handleSendMessage = () => {
    if (!message.trim()) {
      toast.error('Please enter a message')
      return
    }

    // Add user message to the list
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
      },
    ])

    const keywords = contextKeywords
      ? contextKeywords.split(',').map((k) => k.trim())
      : undefined

    sendMessageMutation.mutate({
      session_id: currentSessionId || undefined,
      message,
      context_keywords: keywords,
    })
  }

  const handleNewSession = () => {
    createSessionMutation.mutate({
      session_name: `Chat ${new Date().toLocaleString()}`,
    })
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="p-8 h-screen flex flex-col">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              AI Chat
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Ask questions about your ad data
            </p>
          </div>
          <button
            onClick={handleNewSession}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            New Chat
          </button>
        </div>

        {/* Context Keywords */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Context Keywords (optional)
          </label>
          <input
            type="text"
            value={contextKeywords}
            onChange={(e) => setContextKeywords(e.target.value)}
            placeholder="e.g., running shoes, nike"
            className="input max-w-2xl"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Specify keywords to focus the AI's context on relevant ad data
          </p>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 bg-white dark:bg-gray-800 rounded-lg shadow flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <MessageSquare
                  size={64}
                  className="mx-auto text-gray-300 dark:text-gray-600 mb-4"
                />
                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-2">
                  Start a conversation
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Ask me anything about your ad data, competitors, or get suggestions
                  for your campaigns.
                </p>
                <div className="text-sm text-gray-500 dark:text-gray-400 space-y-2">
                  <p className="font-medium">Try asking:</p>
                  <ul className="space-y-1">
                    <li>"What are the most common headlines?"</li>
                    <li>"How have Nike's ads changed over time?"</li>
                    <li>"Suggest 5 headlines for running shoes"</li>
                    <li>"What emotional triggers are competitors using?"</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${
                    msg.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  <div
                    className={`max-w-3xl rounded-lg p-4 ${
                      msg.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                    <p
                      className={`text-xs mt-2 ${
                        msg.role === 'user'
                          ? 'text-primary-100'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}
                    >
                      {new Date(msg.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              {sendMessageMutation.isPending && (
                <div className="flex justify-start">
                  <div className="max-w-3xl rounded-lg p-4 bg-gray-100 dark:bg-gray-700">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: '0.1s' }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: '0.2s' }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your message..."
              className="input flex-1"
              disabled={sendMessageMutation.isPending}
            />
            <button
              onClick={handleSendMessage}
              disabled={sendMessageMutation.isPending || !message.trim()}
              className="btn btn-primary flex items-center gap-2"
            >
              <Send size={20} />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
