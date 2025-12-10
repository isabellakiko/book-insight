import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, BookOpen, Loader2, MessageCircle, BookMarked } from 'lucide-react'
import { booksApi, ragApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'
import { Link } from 'react-router-dom'

export default function RAGChat() {
  const { currentBookId } = useBookStore()
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const messagesEndRef = useRef(null)

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const askMutation = useMutation({
    mutationFn: ({ bookId, query }) => ragApi.ask(bookId, query),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          type: 'answer',
          content: data.answer,
          results: data.results,
        },
      ])
    },
    onError: (err) => {
      setMessages((prev) => [
        ...prev,
        {
          type: 'error',
          content: '查询失败: ' + err.message,
        },
      ])
    },
  })

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!query.trim() || !currentBookId) return

    setMessages((prev) => [...prev, { type: 'question', content: query }])
    askMutation.mutate({ bookId: currentBookId, query })
    setQuery('')
  }

  if (!currentBookId) {
    return (
      <div className="flex items-center justify-center h-full bg-surface">
        <div className="empty-state animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
            <BookOpen size={28} className="text-text-muted" strokeWidth={1.5} />
          </div>
          <h2 className="empty-state-title">尚未选择书籍</h2>
          <p className="empty-state-description">请先在藏书阁选择一本书</p>
          <Link to="/" className="btn btn-primary mt-4">
            前往藏书阁
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-surface">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-surface/95 backdrop-blur-sm border-b border-border">
        <div className="px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-accent-surface flex items-center justify-center">
              <MessageCircle size={18} className="text-accent" strokeWidth={1.5} />
            </div>
            <div>
              <h1 className="font-semibold text-text-primary">
                智能问答
              </h1>
              <p className="text-xs text-text-muted">
                {book?.title || '加载中...'}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-auto px-6 py-6">
        {messages.length === 0 ? (
          <div className="empty-state animate-fade-in py-12">
            <MessageCircle size={32} className="text-text-muted mb-4" strokeWidth={1.5} />
            <h3 className="text-lg font-medium text-text-primary mb-2">
              与书籍对话
            </h3>
            <p className="text-text-secondary text-sm mb-6">
              基于原文内容的智能问答
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-md">
              {['主角是谁？', '故事的背景是什么？', '第一章发生了什么？'].map((q) => (
                <button
                  key={q}
                  onClick={() => setQuery(q)}
                  className="btn btn-secondary btn-sm"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-2xl mx-auto space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`animate-slide-up ${msg.type === 'question' ? 'flex justify-end' : ''}`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                {msg.type === 'question' ? (
                  <div className="message-user">
                    <p>{msg.content}</p>
                  </div>
                ) : msg.type === 'error' ? (
                  <div className="bg-error/10 border border-error/20 rounded-lg px-4 py-3">
                    <p className="text-error text-sm">{msg.content}</p>
                  </div>
                ) : (
                  <div className="message-assistant">
                    <p className="whitespace-pre-wrap leading-relaxed text-text-primary">
                      {msg.content}
                    </p>

                    {msg.results?.length > 0 && (
                      <details className="mt-3 pt-3 border-t border-border">
                        <summary className="text-sm text-accent cursor-pointer hover:underline flex items-center gap-2">
                          <BookMarked size={14} />
                          参考原文 ({msg.results.length} 处)
                        </summary>
                        <div className="mt-3 space-y-2">
                          {msg.results.map((r, j) => (
                            <div
                              key={j}
                              className="text-sm bg-surface-tertiary rounded-lg p-3 border-accent-left"
                            >
                              <span className="tag tag-accent text-xs mb-2">
                                第 {r.chapter_index + 1} 章
                              </span>
                              <p className="text-text-secondary leading-relaxed mt-2">
                                {r.content.slice(0, 200)}...
                              </p>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                )}
              </div>
            ))}

            {askMutation.isPending && (
              <div className="flex items-center gap-2 text-text-muted animate-fade-in">
                <Loader2 size={16} className="animate-spin text-accent" />
                <span className="text-sm">思考中...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-border bg-surface-secondary">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto px-6 py-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="输入你的问题..."
              className="input flex-1"
            />
            <button
              type="submit"
              disabled={!query.trim() || askMutation.isPending}
              className="btn btn-primary"
            >
              {askMutation.isPending ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Send size={16} />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
