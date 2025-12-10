import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Users, Search, BookOpen, Sparkles, ExternalLink } from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function Characters() {
  const { currentBookId } = useBookStore()
  const [searchName, setSearchName] = useState('')

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const { data: analyzedCharacters = [] } = useQuery({
    queryKey: ['detailed-characters', currentBookId],
    queryFn: () => analysisApi.getDetailedCharacters(currentBookId),
    enabled: !!currentBookId,
  })

  const handleSearch = (e) => {
    e.preventDefault()
    if (searchName.trim()) {
      window.open(`/characters/${encodeURIComponent(searchName.trim())}`, '_blank')
    }
  }

  const handleSelectCharacter = (name) => {
    window.open(`/characters/${encodeURIComponent(name)}`, '_blank')
  }

  if (!currentBookId) {
    return (
      <div className="flex items-center justify-center h-full bg-surface">
        <div className="empty-state animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
            <BookOpen size={28} className="text-text-muted" strokeWidth={1.5} />
          </div>
          <h2 className="empty-state-title">尚未选择书籍</h2>
          <p className="empty-state-description">请先在藏书阁中选择一本书</p>
          <Link to="/" className="btn btn-primary mt-4">
            前往藏书阁
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-full bg-surface">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-surface/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-6 py-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-xl font-semibold text-text-primary">人物志</h1>
              <p className="text-sm text-text-muted mt-0.5">
                {book ? `《${book.title}》` : '加载中...'}
              </p>
            </div>
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearch}>
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search
                  size={16}
                  className="search-icon"
                  strokeWidth={1.5}
                />
                <input
                  type="text"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  placeholder="输入人物姓名，开始分析..."
                  className="input search-input"
                />
              </div>
              <button
                type="submit"
                disabled={!searchName.trim()}
                className="btn btn-primary"
              >
                <Sparkles size={16} />
                <span>分析</span>
              </button>
            </div>
          </form>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-6">
        {/* Cached Characters Grid */}
        {analyzedCharacters.length > 0 && (
          <section className="animate-fade-in">
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-sm font-medium text-text-secondary">已分析人物</h2>
              <span className="tag tag-default">
                {analyzedCharacters.length}
              </span>
            </div>
            <div className="grid md:grid-cols-2 gap-4 stagger">
              {analyzedCharacters.map((char) => (
                <button
                  key={char.name}
                  onClick={() => handleSelectCharacter(char.name)}
                  className="card card-hover p-4 text-left group"
                >
                  <div className="flex items-center gap-4">
                    <div className="avatar avatar-lg bg-accent-surface text-accent group-hover:scale-105 transition-transform">
                      {char.name[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-text-primary group-hover:text-accent transition-colors">
                        {char.name}
                      </h3>
                      <p className="text-xs text-text-muted mt-0.5">
                        {char.total_chapters} 章出场
                      </p>
                    </div>
                    <ExternalLink
                      size={16}
                      className="text-text-muted group-hover:text-accent transition-colors"
                    />
                  </div>
                  {char.summary && (
                    <p className="mt-3 text-sm text-text-secondary line-clamp-2 leading-relaxed">
                      {char.summary}
                    </p>
                  )}
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Empty State */}
        {analyzedCharacters.length === 0 && (
          <div className="empty-state py-16 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
              <Users size={28} className="text-text-muted" strokeWidth={1.5} />
            </div>
            <h2 className="empty-state-title">开始探索人物</h2>
            <p className="empty-state-description">
              输入人物名字，AI 将深度分析其性格特征、成长轨迹、人物关系与经典语录
            </p>
          </div>
        )}

        {/* Tips */}
        {analyzedCharacters.length > 0 && (
          <div className="mt-8 p-4 rounded-lg bg-accent-surface border border-accent/20">
            <h4 className="text-sm font-medium text-accent mb-2">使用提示</h4>
            <ul className="text-sm text-text-secondary space-y-1">
              <li>• 点击人物卡片，查看完整的人物档案</li>
              <li>• 输入新人物名字，AI 将自动开始深度分析</li>
              <li>• 分析结果会自动缓存，下次访问可直接查看</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
