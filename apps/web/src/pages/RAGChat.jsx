import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, BookOpen, Loader2, Feather, Quote, BookMarked } from 'lucide-react'
import { booksApi, ragApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function RAGChat() {
  const { currentBookId } = useBookStore()
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const messagesEndRef = useRef(null)

  const { data: books = [] } = useQuery({
    queryKey: ['books'],
    queryFn: booksApi.list,
  })

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
      <div className="flex items-center justify-center h-full">
        <div className="text-center animate-fade-in">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
            <BookOpen size={40} className="text-[var(--text-muted)]" strokeWidth={1} />
          </div>
          <h2 className="font-display text-2xl mb-2">尚未选择书籍</h2>
          <p className="text-[var(--text-muted)]">请先在藏书阁选择一本书</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-paper-dark/95 backdrop-blur-sm border-b border-paper-lighter/30">
        <div className="px-8 py-5">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-paper flex items-center justify-center">
              <Feather size={20} className="text-gold" strokeWidth={1.5} />
            </div>
            <div>
              <p className="chapter-number mb-0.5">Dialogue</p>
              <h1 className="font-display text-xl font-medium">
                {book?.title || '加载中...'}
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-auto px-8 py-6">
        {messages.length === 0 ? (
          <div className="text-center py-16 animate-fade-in">
            <Quote size={32} className="mx-auto text-gold/50 mb-6" strokeWidth={1} />
            <h3 className="font-display text-xl mb-4 text-[var(--text-secondary)]">
              与文本对话
            </h3>
            <p className="text-[var(--text-muted)] mb-6">
              基于原文内容的智能问答
            </p>
            <div className="max-w-md mx-auto space-y-2">
              <p className="text-sm text-[var(--text-muted)]">试着问：</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {['主角是谁？', '故事的背景是什么？', '第一章发生了什么？'].map((q) => (
                  <button
                    key={q}
                    onClick={() => setQuery(q)}
                    className="px-3 py-1.5 text-sm bg-paper hover:bg-paper-light border border-paper-lighter rounded-full transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`animate-slide-up ${msg.type === 'question' ? 'flex justify-end' : ''}`}
                style={{ animationDelay: `${i * 0.05}s` }}
              >
                {msg.type === 'question' ? (
                  <div className="max-w-[80%] bg-gold text-ink rounded-2xl rounded-tr-sm px-5 py-3">
                    <p className="font-medium">{msg.content}</p>
                  </div>
                ) : msg.type === 'error' ? (
                  <div className="bg-burgundy/20 border border-burgundy/30 rounded-lg px-5 py-3">
                    <p className="text-[var(--error)]">{msg.content}</p>
                  </div>
                ) : (
                  <div className="bg-paper rounded-2xl rounded-tl-sm px-5 py-4 border border-paper-lighter">
                    <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                    {msg.results?.length > 0 && (
                      <details className="mt-4 pt-4 border-t border-paper-lighter/50">
                        <summary className="text-sm text-gold cursor-pointer hover:text-copper transition-colors flex items-center gap-2">
                          <BookMarked size={14} />
                          参考原文 ({msg.results.length} 处)
                        </summary>
                        <div className="mt-3 space-y-3">
                          {msg.results.map((r, j) => (
                            <div
                              key={j}
                              className="text-sm bg-paper-dark/50 rounded-lg p-3 border-l-2 border-gold/30"
                            >
                              <span className="text-gold text-xs font-medium">
                                第 {r.chapter_index + 1} 章
                              </span>
                              <p className="mt-1 text-[var(--text-secondary)] leading-relaxed">
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
              <div className="flex items-center gap-3 text-[var(--text-muted)] animate-fade-in">
                <Loader2 size={18} className="animate-spin text-gold" />
                <span className="font-display italic">思考中...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-paper-lighter/30 bg-paper-dark/80 backdrop-blur-sm">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-8 py-4">
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
              className="btn btn-primary px-5"
            >
              {askMutation.isPending ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
