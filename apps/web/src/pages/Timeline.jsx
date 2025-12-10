import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Clock, Loader2, BookOpen, Users, Sparkles } from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'

export default function Timeline() {
  const { currentBookId } = useBookStore()

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const { data: analyses = [], isLoading } = useQuery({
    queryKey: ['analyses', currentBookId],
    queryFn: () => analysisApi.getChapterAnalyses(currentBookId),
    enabled: !!currentBookId,
  })

  if (!currentBookId) {
    return (
      <div className="flex items-center justify-center h-full bg-surface">
        <div className="empty-state animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
            <Clock size={28} className="text-text-muted" strokeWidth={1.5} />
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
    <div className="min-h-full bg-surface">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-surface/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-3xl mx-auto px-6 py-5">
          <h1 className="text-xl font-semibold text-text-primary">时间线</h1>
          <p className="text-sm text-text-muted mt-0.5">
            {book ? `《${book.title}》` : '加载中...'}
          </p>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-6 py-6">
        {isLoading ? (
          <div className="empty-state animate-fade-in">
            <Loader2 size={32} className="text-accent animate-spin mb-4" />
            <p className="text-text-muted">加载时间线...</p>
          </div>
        ) : analyses.length === 0 ? (
          <div className="empty-state py-16 animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
              <BookOpen size={28} className="text-text-muted" strokeWidth={1.5} />
            </div>
            <h2 className="empty-state-title">尚无章节分析</h2>
            <p className="empty-state-description">
              请先在章节分析页面分析一些章节
            </p>
          </div>
        ) : (
          <div className="timeline stagger">
            {analyses.map((analysis) => (
              <article key={analysis.chapter_index} className="timeline-item">
                <div className="card p-5">
                  {/* Chapter title */}
                  <div className="flex items-start gap-3 mb-3">
                    <span className="tag tag-accent text-xs">
                      {String(analysis.chapter_index + 1).padStart(2, '0')}
                    </span>
                    <h3 className="font-medium text-text-primary">
                      {analysis.title}
                    </h3>
                  </div>

                  {/* Summary */}
                  <p className="text-sm text-text-secondary leading-relaxed mb-4">
                    {analysis.summary}
                  </p>

                  {/* Events */}
                  {analysis.events?.length > 0 && (
                    <div className="mb-4">
                      <h4 className="text-xs font-medium text-accent mb-2 flex items-center gap-1.5">
                        <Sparkles size={12} />
                        关键事件
                      </h4>
                      <ul className="space-y-1.5">
                        {analysis.events.map((event, i) => (
                          <li
                            key={i}
                            className="text-sm text-text-secondary flex items-start gap-2"
                          >
                            <span className="text-accent mt-1.5 text-xs">●</span>
                            <span>{event}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Characters */}
                  {analysis.characters?.length > 0 && (
                    <div className="pt-3 border-t border-border">
                      <h4 className="text-xs font-medium text-text-muted mb-2 flex items-center gap-1.5">
                        <Users size={12} />
                        登场人物
                      </h4>
                      <div className="flex flex-wrap gap-1.5">
                        {analysis.characters.map((char) => (
                          <span
                            key={char}
                            className="tag tag-default text-xs"
                          >
                            {char}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </article>
            ))}

            {/* End marker */}
            <div className="relative pl-8 pt-2">
              <p className="text-xs text-text-muted">
                已分析 {analyses.length} 章
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
