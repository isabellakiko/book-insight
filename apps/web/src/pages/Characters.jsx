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
      <div className="flex items-center justify-center h-full">
        <div className="text-center animate-fade-in">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
            <BookOpen size={40} className="text-[var(--text-muted)]" strokeWidth={1} />
          </div>
          <h2 className="font-display text-2xl mb-2">尚未选择书籍</h2>
          <p className="text-[var(--text-muted)] mb-6">请先在藏书阁中选择一本书</p>
          <Link to="/" className="btn btn-primary">
            前往藏书阁
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-paper-dark/95 backdrop-blur-sm border-b border-paper-lighter/30">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <div className="flex items-end justify-between mb-6">
            <div>
              <p className="chapter-number mb-2">Character Analysis</p>
              <h1 className="font-display text-3xl font-semibold">人物志</h1>
            </div>
            {book && (
              <p className="text-[var(--text-secondary)] text-sm">
                《{book.title}》
              </p>
            )}
          </div>

          {/* Search Form */}
          <form onSubmit={handleSearch}>
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
                  strokeWidth={1.5}
                />
                <input
                  type="text"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  placeholder="输入人物姓名，探索其故事..."
                  className="input pl-11"
                />
              </div>
              <button
                type="submit"
                disabled={!searchName.trim()}
                className="btn btn-primary min-w-[120px]"
              >
                <Sparkles size={18} />
                <span>开始分析</span>
              </button>
            </div>
          </form>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-8 py-8">
        {/* Cached Characters Grid */}
        {analyzedCharacters.length > 0 && (
          <section className="animate-fade-in">
            <h2 className="font-display text-2xl mb-6 flex items-center gap-3">
              <span className="w-8 h-0.5 bg-gradient-to-r from-gold to-transparent" />
              已分析人物
              <span className="text-[var(--text-muted)] font-body text-base">
                ({analyzedCharacters.length})
              </span>
            </h2>
            <div className="grid md:grid-cols-2 gap-5 stagger">
              {analyzedCharacters.map((char) => (
                <button
                  key={char.name}
                  onClick={() => handleSelectCharacter(char.name)}
                  className="card card-hover p-6 text-left group"
                >
                  <div className="flex items-center gap-5">
                    <div className="w-[4.5rem] h-[4.5rem] rounded-xl bg-gradient-to-br from-gold/25 via-copper/15 to-gold/10 border border-gold/40 flex items-center justify-center group-hover:border-gold/70 group-hover:shadow-[0_0_25px_rgba(230,193,88,0.25)] transition-all">
                      <span className="font-display text-3xl text-gold group-hover:scale-110 transition-transform">
                        {char.name[0]}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-display text-xl mb-1 group-hover:text-gold transition-colors">
                        {char.name}
                      </h3>
                      <p className="text-sm text-[var(--text-muted)]">
                        {char.total_chapters} 章出场
                      </p>
                    </div>
                    <ExternalLink
                      size={18}
                      className="text-[var(--text-muted)] group-hover:text-gold transition-colors"
                    />
                  </div>
                  {char.summary && (
                    <p className="mt-4 text-sm text-[var(--text-secondary)] line-clamp-2 leading-relaxed">
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
          <div className="text-center py-20 animate-fade-in">
            <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
              <Users size={40} className="text-[var(--text-muted)]" strokeWidth={1} />
            </div>
            <h2 className="font-display text-2xl mb-3">开始探索人物</h2>
            <p className="text-[var(--text-muted)] max-w-md mx-auto leading-relaxed">
              输入人物名字，AI 将深度分析其性格特征、成长轨迹、人物关系与经典语录
            </p>
          </div>
        )}

        {/* Tips */}
        {analyzedCharacters.length > 0 && (
          <div className="mt-12 p-6 rounded-xl bg-paper/30 border border-paper-lighter/30">
            <h4 className="font-display text-gold mb-3">分析说明</h4>
            <ul className="text-sm text-[var(--text-muted)] space-y-2">
              <li>• 点击已分析的人物卡片，查看完整的人物档案</li>
              <li>• 在搜索框输入新人物名字，AI 将自动开始深度分析</li>
              <li>• 分析结果会自动缓存，下次访问可直接查看</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
