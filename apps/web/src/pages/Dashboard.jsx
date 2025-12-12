import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Book, Upload, Trash2, MessageSquare, Database, BookOpen, Loader2, Check } from 'lucide-react'
import { useState, useRef } from 'react'
import { booksApi, ragApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'
import { clsx } from 'clsx'

export default function Dashboard() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const { currentBookId, setCurrentBook } = useBookStore()

  const { data: books = [], isLoading } = useQuery({
    queryKey: ['books'],
    queryFn: booksApi.list,
  })

  const uploadMutation = useMutation({
    mutationFn: booksApi.upload,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
      setUploading(false)
    },
    onError: (err) => {
      alert('上传失败: ' + err.message)
      setUploading(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: booksApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
    },
  })

  const indexMutation = useMutation({
    mutationFn: (bookId) => ragApi.index(bookId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
    },
    onError: (err) => {
      alert('索引创建失败: ' + err.message)
    },
  })

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    uploadMutation.mutate(file)
  }

  const handleSelectBook = (book) => {
    setCurrentBook(book.id)
  }

  const handleStartChat = (book) => {
    setCurrentBook(book.id)
    navigate('/chat')
  }

  return (
    <div className="min-h-full bg-surface">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-surface/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-text-primary">藏书阁</h1>
              <p className="text-sm text-text-muted mt-0.5">
                {books.length > 0 ? `${books.length} 本书籍` : '开始您的阅读之旅'}
              </p>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="btn btn-primary"
            >
              {uploading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>上传中</span>
                </>
              ) : (
                <>
                  <Upload size={16} />
                  <span>导入书籍</span>
                </>
              )}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-6">
        {isLoading ? (
          <div className="empty-state animate-fade-in">
            <Loader2 size={32} className="empty-state-icon animate-spin" />
            <p className="text-text-muted">加载中...</p>
          </div>
        ) : books.length === 0 ? (
          <div className="empty-state animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
              <BookOpen size={28} className="text-text-muted" strokeWidth={1.5} />
            </div>
            <h2 className="empty-state-title">还没有书籍</h2>
            <p className="empty-state-description">
              点击上方「导入书籍」按钮，开始您的文学探索之旅
            </p>
            <p className="text-xs text-text-muted mt-4">
              支持 .txt 格式
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4 stagger">
            {books.map((book) => {
              const isSelected = currentBookId === book.id

              return (
                <article
                  key={book.id}
                  onClick={() => handleSelectBook(book)}
                  className={clsx(
                    'card book-card p-5 cursor-pointer relative group',
                    isSelected && 'selected'
                  )}
                >
                  <div className="flex gap-4">
                    {/* Book cover placeholder */}
                    <div className="w-16 h-22 rounded-lg bg-surface-tertiary flex items-center justify-center flex-shrink-0">
                      <Book size={24} className="text-text-muted" strokeWidth={1.5} />
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Title & Author */}
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-medium text-text-primary truncate">
                          {book.title}
                        </h3>
                        {isSelected && (
                          <span className="tag tag-accent flex-shrink-0">
                            <Check size={12} />
                            选中
                          </span>
                        )}
                      </div>

                      {book.author && (
                        <p className="text-text-muted text-sm mt-0.5">
                          {book.author}
                        </p>
                      )}

                      {/* Stats */}
                      <div className="flex items-center gap-3 text-xs text-text-secondary mt-2">
                        <span>{book.total_chapters} 章</span>
                        <span className="w-1 h-1 rounded-full bg-border" />
                        <span>{(book.total_characters / 10000).toFixed(1)} 万字</span>
                      </div>
                    </div>

                    {/* Delete button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (confirm('确定要删除这本书吗？')) {
                          deleteMutation.mutate(book.id)
                        }
                      }}
                      className="absolute top-3 right-3 p-1.5 rounded text-text-muted hover:text-error hover:bg-surface-tertiary transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 mt-4 pt-4 border-t border-border">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleStartChat(book)
                      }}
                      className="btn btn-primary btn-sm flex-1"
                    >
                      <MessageSquare size={14} />
                      <span>问答</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        indexMutation.mutate(book.id)
                      }}
                      disabled={indexMutation.isPending}
                      className="btn btn-secondary btn-sm"
                    >
                      {indexMutation.isPending ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Database size={14} />
                      )}
                      <span>索引</span>
                    </button>
                  </div>
                </article>
              )
            })}
          </div>
        )}

        {/* Tips */}
        {books.length > 0 && (
          <div className="mt-8 p-4 rounded-lg bg-accent-surface border border-accent/20">
            <h4 className="text-sm font-medium text-accent mb-2">使用提示</h4>
            <ul className="text-sm text-text-secondary space-y-1">
              <li>• 点击书籍卡片选择当前分析的书籍</li>
              <li>• 首次使用问答功能前，建议先建立索引</li>
              <li>• 在「人物志」页面可以深度分析书中人物</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
