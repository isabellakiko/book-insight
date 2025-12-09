import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Book, Upload, Trash2, Search, BarChart3 } from 'lucide-react'
import { useState, useRef } from 'react'
import { booksApi, ragApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function Dashboard() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef(null)
  const [uploading, setUploading] = useState(false)
  const { setCurrentBook } = useBookStore()

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
      alert('索引创建成功！')
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
    navigate('/chat')
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">书籍管理</h1>
          <p className="text-slate-400 mt-1">导入书籍并开始分析</p>
        </div>

        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50"
        >
          <Upload size={20} />
          {uploading ? '上传中...' : '导入书籍'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".txt"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {isLoading ? (
        <div className="text-center py-12 text-slate-400">加载中...</div>
      ) : books.length === 0 ? (
        <div className="text-center py-12">
          <Book size={48} className="mx-auto text-slate-600 mb-4" />
          <p className="text-slate-400">还没有书籍，点击上方按钮导入</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {books.map((book) => (
            <div
              key={book.id}
              className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-slate-600 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg truncate">{book.title}</h3>
                  {book.author && (
                    <p className="text-slate-400 text-sm mt-1">{book.author}</p>
                  )}
                </div>
                <button
                  onClick={() => deleteMutation.mutate(book.id)}
                  className="p-2 text-slate-400 hover:text-red-400 transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </div>

              <div className="text-sm text-slate-400 space-y-1 mb-4">
                <p>{book.total_chapters} 章</p>
                <p>{(book.total_characters / 10000).toFixed(1)} 万字</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleSelectBook(book)}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-sm"
                >
                  <Search size={16} />
                  问答
                </button>
                <button
                  onClick={() => indexMutation.mutate(book.id)}
                  disabled={indexMutation.isPending}
                  className="flex items-center justify-center gap-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors text-sm"
                >
                  <BarChart3 size={16} />
                  索引
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
