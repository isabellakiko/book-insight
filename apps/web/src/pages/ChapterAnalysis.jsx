import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Loader2, CheckCircle, BookOpen, Users, Sparkles, Hash, Heart } from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'
import { clsx } from 'clsx'

export default function ChapterAnalysis() {
  const { bookId } = useParams()
  const queryClient = useQueryClient()
  const [selectedChapter, setSelectedChapter] = useState(null)

  const { data: book } = useQuery({
    queryKey: ['book', bookId],
    queryFn: () => booksApi.get(bookId),
    enabled: !!bookId,
  })

  const { data: chapters = [] } = useQuery({
    queryKey: ['chapters', bookId],
    queryFn: () => booksApi.getChapters(bookId),
    enabled: !!bookId,
  })

  const { data: analyses = [] } = useQuery({
    queryKey: ['analyses', bookId],
    queryFn: () => analysisApi.getChapterAnalyses(bookId),
    enabled: !!bookId,
  })

  const { data: chapterContent } = useQuery({
    queryKey: ['chapterContent', bookId, selectedChapter],
    queryFn: () => booksApi.getChapterContent(bookId, selectedChapter),
    enabled: !!bookId && selectedChapter !== null,
  })

  const { data: selectedAnalysis } = useQuery({
    queryKey: ['chapterAnalysis', bookId, selectedChapter],
    queryFn: () => analysisApi.getChapterAnalysis(bookId, selectedChapter),
    enabled: !!bookId && selectedChapter !== null,
  })

  const analyzeMutation = useMutation({
    mutationFn: (chapterIndex) => analysisApi.analyzeChapter(bookId, chapterIndex),
    onSuccess: () => {
      queryClient.invalidateQueries(['analyses', bookId])
      queryClient.invalidateQueries(['chapterAnalysis', bookId, selectedChapter])
    },
  })

  const isAnalyzed = (index) => analyses.some((a) => a.chapter_index === index)

  return (
    <div className="flex h-full">
      {/* Chapter list sidebar */}
      <aside className="w-72 bg-paper-dark flex flex-col border-r border-paper-lighter/50">
        {/* Book info header */}
        <div className="p-6 border-b border-paper-lighter/30">
          <p className="chapter-number mb-1">Chapters</p>
          <h2 className="font-display text-lg font-medium truncate">
            {book?.title || '加载中...'}
          </h2>
          <p className="text-sm text-[var(--text-muted)] mt-1">
            {chapters.length} 章 · {analyses.length} 已分析
          </p>
        </div>

        {/* Chapter list */}
        <div className="flex-1 overflow-auto p-3">
          <div className="space-y-1">
            {chapters.map((chapter) => {
              const analyzed = isAnalyzed(chapter.index)
              const isSelected = selectedChapter === chapter.index

              return (
                <button
                  key={chapter.index}
                  onClick={() => setSelectedChapter(chapter.index)}
                  className={clsx(
                    'w-full text-left px-4 py-3 rounded-lg flex items-center gap-3 transition-all duration-200',
                    isSelected
                      ? 'bg-paper border border-gold/30'
                      : 'hover:bg-paper/50'
                  )}
                >
                  <span className={clsx(
                    'w-6 h-6 rounded flex items-center justify-center flex-shrink-0 text-xs font-medium',
                    analyzed
                      ? 'bg-gold/20 text-gold'
                      : 'bg-paper-lighter text-[var(--text-muted)]'
                  )}>
                    {analyzed ? (
                      <CheckCircle size={14} />
                    ) : (
                      String(chapter.index + 1).padStart(2, '0')
                    )}
                  </span>
                  <span className={clsx(
                    'truncate text-sm',
                    isSelected ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'
                  )}>
                    {chapter.title}
                  </span>
                </button>
              )
            })}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex">
        {selectedChapter === null ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center animate-fade-in">
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-paper flex items-center justify-center">
                <BookOpen size={32} className="text-[var(--text-muted)]" strokeWidth={1.5} />
              </div>
              <h2 className="font-display text-xl mb-2">选择章节</h2>
              <p className="text-[var(--text-muted)]">从左侧列表选择一个章节开始阅读</p>
            </div>
          </div>
        ) : (
          <>
            {/* Chapter content */}
            <div className="flex-1 overflow-auto">
              <div className="max-w-3xl mx-auto px-8 py-8">
                {/* Chapter header */}
                <header className="mb-8">
                  <p className="chapter-number mb-2">
                    Chapter {String(selectedChapter + 1).padStart(2, '0')}
                  </p>
                  <h1 className="font-display text-3xl font-semibold">
                    {chapterContent?.title}
                  </h1>
                </header>

                {/* Chapter text */}
                <article className="prose prose-lg">
                  <div className="whitespace-pre-wrap text-[var(--text-secondary)] leading-[1.8] text-base">
                    {chapterContent?.content}
                  </div>
                </article>
              </div>
            </div>

            {/* Analysis panel */}
            <aside className="w-80 bg-paper border-l border-paper-lighter/50 overflow-auto">
              <div className="p-6">
                {/* Panel header */}
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-display text-lg font-medium">分析</h3>
                  <button
                    onClick={() => analyzeMutation.mutate(selectedChapter)}
                    disabled={analyzeMutation.isPending}
                    className="btn btn-primary text-sm py-2"
                  >
                    {analyzeMutation.isPending ? (
                      <>
                        <Loader2 size={14} className="animate-spin" />
                        <span>分析中</span>
                      </>
                    ) : (
                      <>
                        <Play size={14} />
                        <span>开始分析</span>
                      </>
                    )}
                  </button>
                </div>

                {selectedAnalysis ? (
                  <div className="space-y-6 animate-fade-in">
                    {/* Summary */}
                    <section>
                      <h4 className="text-sm font-medium text-gold mb-2 flex items-center gap-2">
                        <BookOpen size={14} />
                        章节摘要
                      </h4>
                      <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                        {selectedAnalysis.summary}
                      </p>
                    </section>

                    {/* Characters */}
                    {selectedAnalysis.characters?.length > 0 && (
                      <section>
                        <h4 className="text-sm font-medium text-gold mb-2 flex items-center gap-2">
                          <Users size={14} />
                          登场人物
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedAnalysis.characters.map((char) => (
                            <span key={char} className="tag tag-muted text-xs">
                              {char}
                            </span>
                          ))}
                        </div>
                      </section>
                    )}

                    {/* Events */}
                    {selectedAnalysis.events?.length > 0 && (
                      <section>
                        <h4 className="text-sm font-medium text-gold mb-2 flex items-center gap-2">
                          <Sparkles size={14} />
                          关键事件
                        </h4>
                        <ul className="space-y-2">
                          {selectedAnalysis.events.map((event, i) => (
                            <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2">
                              <span className="text-copper mt-1 text-xs">●</span>
                              <span>{event}</span>
                            </li>
                          ))}
                        </ul>
                      </section>
                    )}

                    {/* Sentiment */}
                    {selectedAnalysis.sentiment && (
                      <section>
                        <h4 className="text-sm font-medium text-gold mb-2 flex items-center gap-2">
                          <Heart size={14} />
                          情感基调
                        </h4>
                        <p className="text-sm text-[var(--text-secondary)]">
                          {selectedAnalysis.sentiment}
                        </p>
                      </section>
                    )}

                    {/* Keywords */}
                    {selectedAnalysis.keywords?.length > 0 && (
                      <section>
                        <h4 className="text-sm font-medium text-gold mb-2 flex items-center gap-2">
                          <Hash size={14} />
                          关键词
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {selectedAnalysis.keywords.map((kw) => (
                            <span key={kw} className="tag tag-gold text-xs">
                              {kw}
                            </span>
                          ))}
                        </div>
                      </section>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-paper-dark flex items-center justify-center">
                      <Sparkles size={24} className="text-[var(--text-muted)]" strokeWidth={1.5} />
                    </div>
                    <p className="text-sm text-[var(--text-muted)]">
                      点击「开始分析」<br />AI 将解析章节内容
                    </p>
                  </div>
                )}
              </div>
            </aside>
          </>
        )}
      </div>
    </div>
  )
}
