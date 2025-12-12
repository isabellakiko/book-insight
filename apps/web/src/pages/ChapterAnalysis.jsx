import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Play, Loader2, Check, BookOpen, Users, Sparkles, Hash, Heart } from 'lucide-react'
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
      queryClient.invalidateQueries({ queryKey: ['analyses', bookId] })
      queryClient.invalidateQueries({ queryKey: ['chapterAnalysis', bookId, selectedChapter] })
    },
  })

  const isAnalyzed = (index) => analyses.some((a) => a.chapter_index === index)

  return (
    <div className="flex h-full bg-surface">
      {/* Chapter list sidebar */}
      <aside className="w-64 bg-surface-secondary flex flex-col border-r border-border">
        {/* Book info header */}
        <div className="p-4 border-b border-border">
          <h2 className="font-medium text-text-primary truncate text-sm">
            {book?.title || '加载中...'}
          </h2>
          <p className="text-xs text-text-muted mt-1">
            {chapters.length} 章 · {analyses.length} 已分析
          </p>
        </div>

        {/* Chapter list */}
        <div className="flex-1 overflow-auto p-2">
          <div className="space-y-0.5">
            {chapters.map((chapter) => {
              const analyzed = isAnalyzed(chapter.index)
              const isSelected = selectedChapter === chapter.index

              return (
                <button
                  key={chapter.index}
                  onClick={() => setSelectedChapter(chapter.index)}
                  className={clsx(
                    'w-full text-left px-3 py-2.5 rounded-lg flex items-center gap-2.5 transition-all',
                    isSelected
                      ? 'bg-accent-surface text-accent'
                      : 'hover:bg-surface-tertiary text-text-secondary hover:text-text-primary'
                  )}
                >
                  <span className={clsx(
                    'w-5 h-5 rounded flex items-center justify-center flex-shrink-0 text-xs',
                    analyzed
                      ? 'bg-success/20 text-success'
                      : 'bg-surface-tertiary text-text-muted'
                  )}>
                    {analyzed ? (
                      <Check size={12} />
                    ) : (
                      <span className="text-2xs">{chapter.index + 1}</span>
                    )}
                  </span>
                  <span className="truncate text-sm">
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
            <div className="empty-state animate-fade-in">
              <div className="w-16 h-16 rounded-2xl bg-surface-tertiary flex items-center justify-center mb-4">
                <BookOpen size={28} className="text-text-muted" strokeWidth={1.5} />
              </div>
              <h2 className="empty-state-title">选择章节</h2>
              <p className="empty-state-description">从左侧列表选择一个章节开始阅读</p>
            </div>
          </div>
        ) : (
          <>
            {/* Chapter content */}
            <div className="flex-1 overflow-auto">
              <div className="reading-container">
                {/* Chapter header */}
                <header className="mb-8 text-center">
                  <span className="chapter-number">
                    Chapter {String(selectedChapter + 1).padStart(2, '0')}
                  </span>
                  <h1 className="chapter-title mt-2">
                    {chapterContent?.title}
                  </h1>
                </header>

                {/* Chapter text */}
                <article className="reading">
                  <div className="whitespace-pre-wrap leading-[1.9]">
                    {chapterContent?.content}
                  </div>
                </article>
              </div>
            </div>

            {/* Analysis panel */}
            <aside className="w-72 bg-surface-secondary border-l border-border overflow-auto">
              <div className="p-5">
                {/* Panel header */}
                <div className="flex items-center justify-between mb-5">
                  <h3 className="font-medium text-text-primary">分析</h3>
                  <button
                    onClick={() => analyzeMutation.mutate(selectedChapter)}
                    disabled={analyzeMutation.isPending}
                    className="btn btn-primary btn-sm"
                  >
                    {analyzeMutation.isPending ? (
                      <>
                        <Loader2 size={14} className="animate-spin" />
                        <span>分析中</span>
                      </>
                    ) : (
                      <>
                        <Play size={14} />
                        <span>分析</span>
                      </>
                    )}
                  </button>
                </div>

                {selectedAnalysis ? (
                  <div className="space-y-5 animate-fade-in">
                    {/* Summary */}
                    <section>
                      <h4 className="text-xs font-medium text-accent mb-2 flex items-center gap-1.5">
                        <BookOpen size={12} />
                        章节摘要
                      </h4>
                      <p className="text-sm text-text-secondary leading-relaxed">
                        {selectedAnalysis.summary}
                      </p>
                    </section>

                    {/* Characters */}
                    {selectedAnalysis.characters?.length > 0 && (
                      <section>
                        <h4 className="text-xs font-medium text-accent mb-2 flex items-center gap-1.5">
                          <Users size={12} />
                          登场人物
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {selectedAnalysis.characters.map((char) => (
                            <span key={char} className="tag tag-default text-xs">
                              {char}
                            </span>
                          ))}
                        </div>
                      </section>
                    )}

                    {/* Events */}
                    {selectedAnalysis.events?.length > 0 && (
                      <section>
                        <h4 className="text-xs font-medium text-accent mb-2 flex items-center gap-1.5">
                          <Sparkles size={12} />
                          关键事件
                        </h4>
                        <ul className="space-y-1.5">
                          {selectedAnalysis.events.map((event, i) => (
                            <li key={i} className="text-sm text-text-secondary flex items-start gap-2">
                              <span className="text-accent mt-1.5 text-xs">●</span>
                              <span>{event}</span>
                            </li>
                          ))}
                        </ul>
                      </section>
                    )}

                    {/* Sentiment */}
                    {selectedAnalysis.sentiment && (
                      <section>
                        <h4 className="text-xs font-medium text-accent mb-2 flex items-center gap-1.5">
                          <Heart size={12} />
                          情感基调
                        </h4>
                        <p className="text-sm text-text-secondary">
                          {selectedAnalysis.sentiment}
                        </p>
                      </section>
                    )}

                    {/* Keywords */}
                    {selectedAnalysis.keywords?.length > 0 && (
                      <section>
                        <h4 className="text-xs font-medium text-accent mb-2 flex items-center gap-1.5">
                          <Hash size={12} />
                          关键词
                        </h4>
                        <div className="flex flex-wrap gap-1.5">
                          {selectedAnalysis.keywords.map((kw) => (
                            <span key={kw} className="tag tag-accent text-xs">
                              {kw}
                            </span>
                          ))}
                        </div>
                      </section>
                    )}
                  </div>
                ) : (
                  <div className="empty-state py-8">
                    <Sparkles size={24} className="text-text-muted mb-3" strokeWidth={1.5} />
                    <p className="text-sm text-text-muted text-center">
                      点击「分析」按钮<br />AI 将解析章节内容
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
