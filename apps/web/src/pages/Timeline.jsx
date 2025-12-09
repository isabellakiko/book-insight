import { useQuery } from '@tanstack/react-query'
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
      <div className="flex items-center justify-center h-full">
        <div className="text-center animate-fade-in">
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
            <Clock size={40} className="text-[var(--text-muted)]" strokeWidth={1} />
          </div>
          <h2 className="font-display text-2xl mb-2">尚未选择书籍</h2>
          <p className="text-[var(--text-muted)]">请先在藏书阁选择一本书</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-full">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-paper-dark/95 backdrop-blur-sm border-b border-paper-lighter/30">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <p className="chapter-number mb-2">Chronicle</p>
          <h1 className="font-display text-3xl font-semibold mb-1">编年史</h1>
          <p className="text-[var(--text-secondary)]">{book?.title}</p>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-8 py-8">
        {isLoading ? (
          <div className="text-center py-16 animate-fade-in">
            <Loader2 size={32} className="mx-auto text-gold animate-spin mb-4" />
            <p className="text-[var(--text-muted)]">加载时间线...</p>
          </div>
        ) : analyses.length === 0 ? (
          <div className="text-center py-16 animate-fade-in">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
              <BookOpen size={32} className="text-[var(--text-muted)]" strokeWidth={1.5} />
            </div>
            <h2 className="font-display text-xl mb-2">尚无章节分析</h2>
            <p className="text-[var(--text-muted)]">
              请先在章节分析页面分析一些章节
            </p>
          </div>
        ) : (
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-gold via-paper-lighter to-paper-lighter" />

            {/* Events */}
            <div className="space-y-8 stagger">
              {analyses.map((analysis, index) => (
                <article key={analysis.chapter_index} className="relative pl-16">
                  {/* Timeline dot */}
                  <div className="absolute left-4 top-6 w-5 h-5 rounded-full bg-paper-dark border-2 border-gold flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-gold" />
                  </div>

                  {/* Chapter number badge */}
                  <div className="absolute left-0 top-0 w-12 text-center">
                    <span className="text-2xs text-gold font-semibold tracking-wider">
                      {String(analysis.chapter_index + 1).padStart(2, '0')}
                    </span>
                  </div>

                  <div className="card p-6">
                    {/* Chapter title */}
                    <h3 className="font-display text-xl font-medium mb-3">
                      {analysis.title}
                    </h3>

                    {/* Summary */}
                    <p className="text-[var(--text-secondary)] leading-relaxed mb-4">
                      {analysis.summary}
                    </p>

                    {/* Events */}
                    {analysis.events?.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gold mb-2 flex items-center gap-2">
                          <Sparkles size={14} />
                          关键事件
                        </h4>
                        <ul className="space-y-1.5">
                          {analysis.events.map((event, i) => (
                            <li
                              key={i}
                              className="text-sm text-[var(--text-secondary)] flex items-start gap-2"
                            >
                              <span className="text-copper mt-1.5 text-xs">●</span>
                              <span>{event}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Characters */}
                    {analysis.characters?.length > 0 && (
                      <div className="pt-4 border-t border-paper-lighter/50">
                        <h4 className="text-sm font-medium text-[var(--text-muted)] mb-2 flex items-center gap-2">
                          <Users size={14} />
                          登场人物
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {analysis.characters.map((char) => (
                            <span
                              key={char}
                              className="tag tag-muted text-xs"
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
            </div>

            {/* End marker */}
            <div className="relative pl-16 pt-4">
              <div className="absolute left-4 w-5 h-5 rounded-full bg-paper border-2 border-paper-lighter flex items-center justify-center">
                <div className="w-2 h-2 rounded-full bg-paper-lighter" />
              </div>
              <p className="text-sm text-[var(--text-muted)] italic">
                已分析 {analyses.length} 章
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
