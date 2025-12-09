import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Book, Upload, Trash2, MessageSquare, Database, BookOpen, Loader2, CheckCircle } from 'lucide-react'
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
      queryClient.invalidateQueries(['books'])
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
      queryClient.invalidateQueries(['books'])
    },
  })

  const indexMutation = useMutation({
    mutationFn: (bookId) => ragApi.index(bookId),
    onSuccess: () => {
      queryClient.invalidateQueries(['books'])
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
    <div className="min-h-full">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-paper-dark/95 backdrop-blur-sm border-b border-paper-lighter/30">
        <div className="max-w-5xl mx-auto px-8 py-6">
          <div className="flex items-end justify-between">
            <div>
              <p className="chapter-number mb-2">Library</p>
              <h1 className="font-display text-3xl font-semibold">藏书阁</h1>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="btn btn-primary"
            >
              {uploading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  <span>上传中</span>
                </>
              ) : (
                <>
                  <Upload size={18} />
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

      <div className="max-w-5xl mx-auto px-8 py-8">
        {isLoading ? (
          <div className="text-center py-16 animate-fade-in">
            <Loader2 size={32} className="mx-auto text-gold animate-spin mb-4" />
            <p className="text-[var(--text-muted)]">加载藏书中...</p>
          </div>
        ) : books.length === 0 ? (
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
              <BookOpen size={32} className="text-[var(--text-muted)]" strokeWidth={1.5} />
            </div>
            <h2 className="font-display text-xl mb-2">藏书阁尚空</h2>
            <p className="text-[var(--text-muted)] mb-6">
              点击上方「导入书籍」按钮，开始您的文学探索之旅
            </p>
            <p className="text-sm text-[var(--text-muted)]">
              支持 .txt 格式的小说文件
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6 stagger">
            {books.map((book) => {
              const isSelected = currentBookId === book.id

              return (
                <article
                  key={book.id}
                  onClick={() => handleSelectBook(book)}
                  className={clsx(
                    'card card-hover p-6 cursor-pointer relative group',
                    isSelected && 'ring-1 ring-gold/50'
                  )}
                >
                  {/* Selected indicator */}
                  {isSelected && (
                    <div className="absolute -top-px -left-px -right-px h-0.5 bg-gradient-to-r from-gold via-copper to-gold rounded-t-lg" />
                  )}

                  <div className="flex gap-5">
                    {/* Book cover placeholder */}
                    <div className="w-20 h-28 rounded-lg bg-gradient-to-br from-paper-light to-paper-lighter flex items-center justify-center flex-shrink-0 border border-paper-lighter">
                      <Book size={28} className="text-[var(--text-muted)]" strokeWidth={1} />
                    </div>

                    <div className="flex-1 min-w-0">
                      {/* Title & Author */}
                      <h3 className="font-display text-xl font-medium mb-1 truncate pr-8">
                        {book.title}
                      </h3>
                      {book.author && (
                        <p className="text-[var(--text-muted)] text-sm mb-3">
                          {book.author}
                        </p>
                      )}

                      {/* Stats */}
                      <div className="flex items-center gap-4 text-sm text-[var(--text-secondary)]">
                        <span>{book.total_chapters} 章</span>
                        <span className="w-1 h-1 rounded-full bg-paper-lighter" />
                        <span>{(book.total_characters / 10000).toFixed(1)} 万字</span>
                      </div>

                      {/* Status tags */}
                      <div className="flex items-center gap-2 mt-3">
                        {isSelected && (
                          <span className="tag tag-gold text-xs">
                            <CheckCircle size={12} className="mr-1" />
                            当前选中
                          </span>
                        )}
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
                      className="absolute top-4 right-4 p-2 text-[var(--text-muted)] hover:text-[var(--error)] transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3 mt-5 pt-5 border-t border-paper-lighter/50">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleStartChat(book)
                      }}
                      className="btn btn-primary flex-1"
                    >
                      <MessageSquare size={16} />
                      <span>开始问答</span>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        indexMutation.mutate(book.id)
                      }}
                      disabled={indexMutation.isPending}
                      className="btn btn-secondary"
                    >
                      {indexMutation.isPending ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Database size={16} />
                      )}
                      <span>建立索引</span>
                    </button>
                  </div>
                </article>
              )
            })}
          </div>
        )}

        {/* Tips */}
        {books.length > 0 && (
          <div className="mt-12 p-6 rounded-lg bg-paper/30 border border-paper-lighter/30">
            <h4 className="font-display text-sm text-gold mb-2">使用提示</h4>
            <ul className="text-sm text-[var(--text-muted)] space-y-1">
              <li>• 点击书籍卡片选择当前分析的书籍</li>
              <li>• 首次使用问答功能前，建议先建立 RAG 索引</li>
              <li>• 在「人物志」页面可以深度分析书中的人物</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
