import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { X, ChevronDown, ChevronUp, Loader2, BookOpen } from 'lucide-react'
import { booksApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'
import { useCharacterAnalysis } from '../hooks/useCharacterAnalysis'

const relationLabels = {
  lover: '恋人',
  family: '亲人',
  friend: '挚友',
  rival: '对手',
  enemy: '敌人',
  mentor: '导师',
  student: '学生',
}

export default function CharacterDetail() {
  const { name: encodedName } = useParams()
  const name = decodeURIComponent(encodedName || '')
  const { currentBookId } = useBookStore()
  const [expandedChapter, setExpandedChapter] = useState(null)

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const {
    status,
    searchResult,
    appearances,
    result,
    error,
    progress,
    analyzeCharacter,
    loadCached,
  } = useCharacterAnalysis(currentBookId)

  useEffect(() => {
    if (name && currentBookId) {
      loadCached(name).then((loaded) => {
        if (!loaded) {
          analyzeCharacter(name)
        }
      })
    }
  }, [name, currentBookId])

  const handleClose = () => {
    window.close()
  }

  // 未选择书籍
  if (!currentBookId) {
    return (
      <div className="min-h-screen bg-[#0d0b09] flex items-center justify-center">
        <div className="text-center">
          <p className="text-[#6b5d4d] text-sm tracking-[0.3em] uppercase mb-4">No Book Selected</p>
          <h2 className="font-display text-2xl text-[#c4b5a0]">请先在主页面选择一本书</h2>
        </div>
      </div>
    )
  }

  const isLoading = status === 'searching' || status === 'analyzing'

  return (
    <div className="min-h-screen bg-[#0d0b09] text-[#e8e0d4]">
      {/* Subtle texture overlay */}
      <div
        className="fixed inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`
        }}
      />

      {/* Close Button */}
      <button
        onClick={handleClose}
        className="fixed top-8 right-8 z-50 w-10 h-10 rounded-full border border-[#3d3529]/60 flex items-center justify-center text-[#6b5d4d] hover:text-[#c4b5a0] hover:border-[#c4b5a0]/40 transition-all duration-300"
        title="关闭"
      >
        <X size={18} strokeWidth={1.5} />
      </button>

      {/* Loading State */}
      {isLoading && (
        <div className="min-h-screen flex items-center justify-center px-8">
          <div className="text-center max-w-md">
            <p className="text-[#6b5d4d] text-xs tracking-[0.4em] uppercase mb-6">
              {status === 'searching' ? 'Searching' : 'Analyzing'}
            </p>

            <h1 className="font-display text-4xl md:text-5xl font-light text-[#e8e0d4] mb-8 tracking-wide">
              {name}
            </h1>

            {status === 'analyzing' && searchResult && (
              <>
                <div className="w-full h-px bg-[#3d3529] mb-6 relative overflow-hidden">
                  <div
                    className="absolute top-0 left-0 h-full bg-gradient-to-r from-[#c9a55c] to-[#e6c158] transition-all duration-700"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-[#6b5d4d] text-sm">
                  已分析 <span className="text-[#c4b5a0]">{appearances.length}</span> / {Math.min(searchResult.found_in_chapters.length, 30)} 章
                </p>
              </>
            )}

            {status === 'searching' && (
              <Loader2 size={20} className="mx-auto text-[#6b5d4d] animate-spin" />
            )}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && status === 'completed' && (
        <div className="min-h-screen flex items-center justify-center px-8">
          <div className="text-center">
            <p className="text-[#c45050] text-xs tracking-[0.4em] uppercase mb-4">Error</p>
            <h2 className="font-display text-2xl text-[#c4b5a0] mb-4">分析失败</h2>
            <p className="text-[#6b5d4d]">{error}</p>
          </div>
        </div>
      )}

      {/* Result - Editorial Magazine Layout */}
      {result && status === 'completed' && (
        <article className="relative">
          {/* Header Section */}
          <header className="pt-20 pb-16 px-8 md:px-16 lg:px-24 border-b border-[#2a2520]">
            <div className="max-w-5xl mx-auto">
              {/* Meta line */}
              <div className="flex items-center gap-6 mb-8 text-[#6b5d4d] text-xs tracking-[0.3em] uppercase">
                <span>Character Profile</span>
                <span className="w-8 h-px bg-[#3d3529]" />
                <span>《{book?.title}》</span>
              </div>

              {/* Name */}
              <h1 className="font-display text-5xl md:text-7xl lg:text-8xl font-light tracking-tight mb-6 leading-[0.9]">
                {result.name}
              </h1>

              {/* Aliases & Stats */}
              <div className="flex flex-wrap items-center gap-x-8 gap-y-3 text-sm">
                {result.aliases && result.aliases.length > 0 && (
                  <span className="text-[#8a7e70] italic font-display text-lg">
                    {result.aliases.join('，')}
                  </span>
                )}
                <span className="text-[#6b5d4d]">
                  第 <span className="text-[#c9a55c]">{result.first_appearance + 1}</span> 章首次登场
                </span>
                <span className="text-[#6b5d4d]">
                  共 <span className="text-[#c9a55c]">{result.total_chapters || result.appearances?.length || 0}</span> 章出场
                </span>
              </div>
            </div>
          </header>

          {/* Summary - Pull Quote Style */}
          {result.summary && (
            <section className="py-20 px-8 md:px-16 lg:px-24 border-b border-[#2a2520]">
              <div className="max-w-4xl mx-auto">
                <blockquote className="font-display text-2xl md:text-3xl lg:text-4xl font-light leading-relaxed text-[#c4b5a0] italic">
                  <span className="text-[#c9a55c] not-italic">"</span>
                  {result.summary}
                  <span className="text-[#c9a55c] not-italic">"</span>
                </blockquote>
              </div>
            </section>
          )}

          {/* Main Content Grid */}
          <div className="px-8 md:px-16 lg:px-24 py-16">
            <div className="max-w-5xl mx-auto">

              {/* Growth Arc */}
              {result.growth_arc && (
                <section className="mb-20">
                  <SectionHeader number="01" title="成长轨迹" subtitle="Growth Arc" />
                  <div className="md:columns-2 gap-12 text-[#b8a898] leading-[1.9] text-[1.0625rem]">
                    <p className="first-letter:text-5xl first-letter:font-display first-letter:text-[#c9a55c] first-letter:float-left first-letter:mr-3 first-letter:leading-[0.8]">
                      {result.growth_arc}
                    </p>
                  </div>
                </section>
              )}

              {/* Core Traits */}
              {result.core_traits && result.core_traits.length > 0 && (
                <section className="mb-20">
                  <SectionHeader number="02" title="性格剖析" subtitle="Character Traits" />
                  <div className="space-y-12">
                    {result.core_traits.map((trait, i) => (
                      <div key={i} className="grid md:grid-cols-[200px_1fr] gap-6 md:gap-12">
                        <div>
                          <h3 className="font-display text-xl text-[#e8e0d4] mb-1">{trait.trait}</h3>
                          <span className="text-[#6b5d4d] text-xs tracking-[0.2em] uppercase">Trait {String(i + 1).padStart(2, '0')}</span>
                        </div>
                        <div>
                          <p className="text-[#b8a898] leading-relaxed mb-4">{trait.description}</p>
                          {trait.evidence && (
                            <div className="pl-4 border-l border-[#3d3529] space-y-2">
                              {(Array.isArray(trait.evidence) ? trait.evidence.slice(0, 2) : [trait.evidence]).map((e, j) => (
                                <p key={j} className="text-sm text-[#7a6e60] leading-relaxed italic">
                                  {e}
                                </p>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Strengths & Weaknesses */}
              {((result.strengths?.length > 0) || (result.weaknesses?.length > 0)) && (
                <section className="mb-20">
                  <SectionHeader number="03" title="优缺点" subtitle="Strengths & Weaknesses" />
                  <div className="grid md:grid-cols-2 gap-12 md:gap-16">
                    {result.strengths?.length > 0 && (
                      <div>
                        <h4 className="text-xs tracking-[0.3em] uppercase text-[#6b8f71] mb-6 flex items-center gap-3">
                          <span className="w-6 h-px bg-[#6b8f71]" />
                          优点
                        </h4>
                        <ul className="space-y-4">
                          {result.strengths.map((s, i) => (
                            <li key={i} className="text-[#b8a898] leading-relaxed pl-4 border-l border-[#6b8f71]/30">
                              {s}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {result.weaknesses?.length > 0 && (
                      <div>
                        <h4 className="text-xs tracking-[0.3em] uppercase text-[#a67c52] mb-6 flex items-center gap-3">
                          <span className="w-6 h-px bg-[#a67c52]" />
                          缺点
                        </h4>
                        <ul className="space-y-4">
                          {result.weaknesses.map((w, i) => (
                            <li key={i} className="text-[#b8a898] leading-relaxed pl-4 border-l border-[#a67c52]/30">
                              {w}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Notable Quotes */}
              {result.notable_quotes?.length > 0 && (
                <section className="mb-20">
                  <SectionHeader number="04" title="经典语录" subtitle="Notable Quotes" />
                  <div className="space-y-8">
                    {result.notable_quotes.map((q, i) => (
                      <blockquote
                        key={i}
                        className="relative pl-6 py-2 border-l-2 border-[#c9a55c]/40"
                      >
                        <p className="font-display text-xl md:text-2xl text-[#c4b5a0] italic leading-relaxed">
                          「{q}」
                        </p>
                        <span className="absolute -left-[0.6rem] top-0 text-[#c9a55c] text-2xl font-display leading-none">"</span>
                      </blockquote>
                    ))}
                  </div>
                </section>
              )}

              {/* Relations */}
              {result.relations?.length > 0 && (
                <section className="mb-20">
                  <SectionHeader number="05" title="人物关系" subtitle="Relationships" />
                  <div className="grid gap-6">
                    {result.relations.map((rel, i) => (
                      <div
                        key={i}
                        className="group grid md:grid-cols-[180px_1fr] gap-4 md:gap-8 py-6 border-b border-[#2a2520] last:border-b-0"
                      >
                        <div className="flex items-baseline gap-3">
                          <span className="font-display text-2xl text-[#e8e0d4] group-hover:text-[#c9a55c] transition-colors">
                            {rel.target_name}
                          </span>
                        </div>
                        <div className="flex flex-col gap-2">
                          <span className="text-xs tracking-[0.2em] uppercase text-[#6b5d4d]">
                            {relationLabels[rel.relation_type] || rel.relation_type}
                          </span>
                          <p className="text-[#8a7e70] leading-relaxed">
                            {rel.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Appearances */}
              {result.appearances?.length > 0 && (
                <section className="mb-20">
                  <SectionHeader
                    number="06"
                    title="章节出现"
                    subtitle={`${result.appearances.length} Chapters`}
                  />
                  <div className="space-y-1">
                    {result.appearances.map((app) => (
                      <div key={app.chapter_index} className="border-b border-[#2a2520] last:border-b-0">
                        <button
                          className="w-full py-5 flex justify-between items-center text-left group"
                          onClick={() =>
                            setExpandedChapter(expandedChapter === app.chapter_index ? null : app.chapter_index)
                          }
                        >
                          <div className="flex items-baseline gap-6">
                            <span className="text-[#6b5d4d] text-sm tabular-nums w-8">
                              {String(app.chapter_index + 1).padStart(2, '0')}
                            </span>
                            <span className="text-[#c4b5a0] group-hover:text-[#e8e0d4] transition-colors">
                              {app.chapter_title}
                            </span>
                          </div>
                          {expandedChapter === app.chapter_index
                            ? <ChevronUp size={16} className="text-[#c9a55c]" />
                            : <ChevronDown size={16} className="text-[#6b5d4d] group-hover:text-[#8a7e70]" />
                          }
                        </button>
                        {expandedChapter === app.chapter_index && (
                          <div className="pb-6 pl-14 pr-4 space-y-6 animate-fade-in">
                            {app.events?.length > 0 && (
                              <div>
                                <p className="text-xs tracking-[0.2em] uppercase text-[#c9a55c] mb-3">事件</p>
                                <ul className="space-y-2 text-[#8a7e70] text-sm leading-relaxed">
                                  {app.events.map((e, i) => (
                                    <li key={i} className="pl-3 border-l border-[#3d3529]">{e}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {app.interactions?.length > 0 && (
                              <div>
                                <p className="text-xs tracking-[0.2em] uppercase text-[#a67c52] mb-3">互动</p>
                                <ul className="space-y-2 text-[#8a7e70] text-sm leading-relaxed">
                                  {app.interactions.map((e, i) => (
                                    <li key={i} className="pl-3 border-l border-[#3d3529]">{e}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {app.quote && (
                              <blockquote className="pl-3 border-l-2 border-[#c9a55c]/40 font-display italic text-[#b8a898]">
                                「{app.quote}」
                              </blockquote>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>
          </div>

          {/* Footer */}
          <footer className="border-t border-[#2a2520] py-16 px-8">
            <div className="max-w-5xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6 text-[#6b5d4d] text-sm">
              <div className="flex items-center gap-4">
                <span className="text-xs tracking-[0.3em] uppercase">Book Insight</span>
                <span className="w-8 h-px bg-[#3d3529]" />
                <span>Literary Analysis</span>
              </div>
              <span>
                《{book?.title}》· {result.name}
              </span>
            </div>
          </footer>
        </article>
      )}
    </div>
  )
}

// Section Header Component
function SectionHeader({ number, title, subtitle }) {
  return (
    <div className="flex items-end gap-6 mb-10 pb-4 border-b border-[#2a2520]">
      <span className="text-[#3d3529] font-display text-6xl leading-none">{number}</span>
      <div className="pb-1">
        <h2 className="font-display text-2xl text-[#e8e0d4] mb-1">{title}</h2>
        <span className="text-[#6b5d4d] text-xs tracking-[0.3em] uppercase">{subtitle}</span>
      </div>
    </div>
  )
}
