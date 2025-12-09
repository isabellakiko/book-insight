import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, BookOpen, Loader2 } from 'lucide-react'
import { booksApi, ragApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function RAGChat() {
  const { currentBookId } = useBookStore()
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])

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
        <div className="text-center">
          <BookOpen size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">请先在书籍页面选择一本书</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 bg-slate-800">
        <h2 className="font-semibold">{book?.title || '加载中...'}</h2>
        <p className="text-sm text-slate-400">输入问题，AI 将基于原文回答</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12 text-slate-500">
            <p>试着问一些问题，例如：</p>
            <p className="mt-2 text-slate-400">"主角是谁？"</p>
            <p className="text-slate-400">"第一章发生了什么？"</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-3xl ${msg.type === 'question' ? 'ml-auto' : ''}`}
            >
              {msg.type === 'question' ? (
                <div className="bg-blue-600 rounded-lg px-4 py-3">
                  {msg.content}
                </div>
              ) : msg.type === 'error' ? (
                <div className="bg-red-900/50 rounded-lg px-4 py-3 text-red-300">
                  {msg.content}
                </div>
              ) : (
                <div className="bg-slate-800 rounded-lg px-4 py-3">
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  {msg.results?.length > 0 && (
                    <details className="mt-4">
                      <summary className="text-sm text-slate-400 cursor-pointer">
                        查看参考原文 ({msg.results.length} 处)
                      </summary>
                      <div className="mt-2 space-y-2">
                        {msg.results.map((r, j) => (
                          <div
                            key={j}
                            className="text-sm bg-slate-700/50 rounded p-2"
                          >
                            <span className="text-blue-400">
                              [第{r.chapter_index + 1}章]
                            </span>{' '}
                            {r.content.slice(0, 200)}...
                          </div>
                        ))}
                      </div>
                    </details>
                  )}
                </div>
              )}
            </div>
          ))
        )}

        {askMutation.isPending && (
          <div className="flex items-center gap-2 text-slate-400">
            <Loader2 size={16} className="animate-spin" />
            思考中...
          </div>
        )}
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="p-4 border-t border-slate-700 bg-slate-800"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="输入你的问题..."
            className="flex-1 px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={!query.trim() || askMutation.isPending}
            className="px-4 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  )
}
