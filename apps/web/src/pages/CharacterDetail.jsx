import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { X, ChevronRight, Loader2, Quote, Sparkles, Heart, Swords, Users, GraduationCap, BookOpen } from 'lucide-react'
import { booksApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'
import { useCharacterAnalysis } from '../hooks/useCharacterAnalysis'
import { useThemeStore } from '../stores/themeStore'
import ThemeSwitcher from '../components/ThemeSwitcher'

const relationConfig = {
  lover: { label: '恋人', icon: Heart, color: 'rose' },
  family: { label: '亲人', icon: Users, color: 'amber' },
  friend: { label: '挚友', icon: Users, color: 'emerald' },
  rival: { label: '对手', icon: Swords, color: 'orange' },
  enemy: { label: '敌人', icon: Swords, color: 'red' },
  mentor: { label: '导师', icon: GraduationCap, color: 'blue' },
  student: { label: '学生', icon: GraduationCap, color: 'cyan' },
}

export default function CharacterDetail() {
  const { name: encodedName } = useParams()
  const name = decodeURIComponent(encodedName || '')
  const { currentBookId } = useBookStore()
  const [expandedChapter, setExpandedChapter] = useState(null)
  const initTheme = useThemeStore((state) => state.initTheme)

  // 1. 获取数据的 hooks 必须在前面
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

  // 2. 然后是 useEffect
  useEffect(() => {
    initTheme()
  }, [initTheme])

  // 加载缓存或开始分析
  useEffect(() => {
    if (name && currentBookId) {
      loadCached(name).then((loaded) => {
        if (!loaded) {
          analyzeCharacter(name)
        }
      })
    }
  }, [name, currentBookId, loadCached, analyzeCharacter])

  const handleClose = () => {
    window.close()
  }

  if (!currentBookId) {
    return (
      <div className="character-page">
        <div className="character-empty">
          <div className="character-empty-icon">
            <BookOpen size={32} strokeWidth={1} />
          </div>
          <h2>请先选择一本书</h2>
          <p>在主页面的藏书阁中选择要分析的书籍</p>
        </div>
      </div>
    )
  }

  const isLoading = status === 'searching' || status === 'analyzing'

  return (
    <div className="character-page">
      {/* Floating Controls */}
      <div className="character-controls">
        <ThemeSwitcher variant="compact" />
        <button onClick={handleClose} className="character-close" title="关闭">
          <X size={18} strokeWidth={1.5} />
        </button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="character-loading">
          <div className="character-loading-content">
            <div className="character-loading-label">
              {status === 'searching' ? '正在搜索' : '正在分析'}
            </div>
            <h1 className="character-loading-name">{name}</h1>

            {status === 'analyzing' && searchResult && (
              <div className="character-loading-progress">
                <div className="character-progress-bar">
                  <div
                    className="character-progress-fill"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="character-progress-text">
                  已分析 <span>{appearances.length}</span> / {Math.min(searchResult.found_in_chapters.length, 30)} 章
                </p>
              </div>
            )}

            {status === 'searching' && (
              <div className="character-loading-spinner">
                <Loader2 size={24} className="animate-spin" />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && status === 'completed' && (
        <div className="character-empty">
          <div className="character-empty-icon character-empty-error">
            <X size={32} strokeWidth={1} />
          </div>
          <h2>分析失败</h2>
          <p>{error}</p>
        </div>
      )}

      {/* Result */}
      {result && status === 'completed' && (
        <article className="character-article">
          {/* Hero Section */}
          <header className="character-hero">
            <div className="character-hero-bg" />
            <div className="character-hero-content">
              <div className="character-hero-meta">
                <span className="character-hero-label">人物志</span>
                <span className="character-hero-divider" />
                <span className="character-hero-book">{book?.title}</span>
              </div>

              <h1 className="character-hero-name">
                <span className="character-hero-name-text">{result.name}</span>
                {result.aliases && result.aliases.length > 0 && (
                  <span className="character-hero-aliases">
                    {result.aliases.join(' · ')}
                  </span>
                )}
              </h1>

              <div className="character-hero-stats">
                <div className="character-stat">
                  <span className="character-stat-value">第 {result.first_appearance + 1} 章</span>
                  <span className="character-stat-label">首次登场</span>
                </div>
                <div className="character-stat-divider" />
                <div className="character-stat">
                  <span className="character-stat-value">{result.total_chapters || result.appearances?.length || 0} 章</span>
                  <span className="character-stat-label">出场次数</span>
                </div>
              </div>
            </div>
          </header>

          {/* Summary - Large Pull Quote */}
          {result.summary && (
            <section id="summary" className="character-summary visible">
              <div className="character-summary-inner">
                <Quote className="character-summary-quote-icon" size={48} strokeWidth={1} />
                <blockquote className="character-summary-text">
                  {result.summary}
                </blockquote>
              </div>
            </section>
          )}

          {/* Main Content */}
          <div className="character-content">
            {/* Growth Arc */}
            {result.growth_arc && (
              <section id="growth" className="character-section visible">
                <SectionTitle number="01" title="成长轨迹" subtitle="Character Arc" />
                <div className="character-growth">
                  <p className="character-growth-text">
                    <span className="character-growth-dropcap">{result.growth_arc[0]}</span>
                    {result.growth_arc.slice(1)}
                  </p>
                </div>
              </section>
            )}

            {/* Core Traits */}
            {result.core_traits && result.core_traits.length > 0 && (
              <section id="traits" className="character-section visible">
                <SectionTitle number="02" title="性格剖析" subtitle="Personality" />
                <div className="character-traits">
                  {result.core_traits.map((trait, i) => (
                    <div
                      key={i}
                      className="character-trait"
                      style={{ animationDelay: `${i * 0.1}s` }}
                    >
                      <div className="character-trait-header">
                        <span className="character-trait-index">{String(i + 1).padStart(2, '0')}</span>
                        <h3 className="character-trait-name">{trait.trait}</h3>
                      </div>
                      <p className="character-trait-desc">{trait.description}</p>
                      {trait.evidence && (
                        <div className="character-trait-evidence">
                          <Sparkles size={12} />
                          <span>{Array.isArray(trait.evidence) ? trait.evidence[0] : trait.evidence}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Strengths & Weaknesses */}
            {((result.strengths?.length > 0) || (result.weaknesses?.length > 0)) && (
              <section id="balance" className="character-section visible">
                <SectionTitle number="03" title="光与影" subtitle="Light & Shadow" />
                <div className="character-balance">
                  {result.strengths?.length > 0 && (
                    <div className="character-balance-side character-balance-light">
                      <h4 className="character-balance-title">
                        <span className="character-balance-icon">✦</span>
                        优点
                      </h4>
                      <ul className="character-balance-list">
                        {result.strengths.map((s, i) => (
                          <li key={i}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {result.weaknesses?.length > 0 && (
                    <div className="character-balance-side character-balance-shadow">
                      <h4 className="character-balance-title">
                        <span className="character-balance-icon">✧</span>
                        缺点
                      </h4>
                      <ul className="character-balance-list">
                        {result.weaknesses.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* Notable Quotes */}
            {result.notable_quotes?.length > 0 && (
              <section id="quotes" className="character-section visible">
                <SectionTitle number="04" title="经典语录" subtitle="Memorable Quotes" />
                <div className="character-quotes">
                  {result.notable_quotes.map((q, i) => (
                    <blockquote
                      key={i}
                      className="character-quote"
                      style={{ animationDelay: `${i * 0.15}s` }}
                    >
                      <span className="character-quote-mark">"</span>
                      <p className="character-quote-text">{q}</p>
                      <span className="character-quote-mark character-quote-mark-end">"</span>
                    </blockquote>
                  ))}
                </div>
              </section>
            )}

            {/* Relations */}
            {result.relations?.length > 0 && (
              <section id="relations" className="character-section visible">
                <SectionTitle number="05" title="人物关系" subtitle="Relationships" />
                <div className="character-relations">
                  {result.relations.map((rel, i) => {
                    const config = relationConfig[rel.relation_type] || { label: rel.relation_type, icon: Users, color: 'gray' }
                    const Icon = config.icon
                    return (
                      <div
                        key={i}
                        className={`character-relation character-relation-${config.color}`}
                        style={{ animationDelay: `${i * 0.1}s` }}
                      >
                        <div className="character-relation-avatar">
                          {rel.target_name[0]}
                        </div>
                        <div className="character-relation-content">
                          <div className="character-relation-header">
                            <span className="character-relation-name">{rel.target_name}</span>
                            <span className="character-relation-type">
                              <Icon size={12} />
                              {config.label}
                            </span>
                          </div>
                          <p className="character-relation-desc">{rel.description}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </section>
            )}

            {/* Appearances Timeline */}
            {result.appearances?.length > 0 && (
              <section id="appearances" className="character-section visible">
                <SectionTitle
                  number="06"
                  title={`章节足迹`}
                  subtitle={`${result.appearances.length} Chapters`}
                />
                <div className="character-timeline">
                  {result.appearances.map((app, i) => (
                    <div
                      key={app.chapter_index}
                      className="character-timeline-item"
                      style={{ animationDelay: `${i * 0.05}s` }}
                    >
                      <div className="character-timeline-marker">
                        <span className="character-timeline-dot" />
                        <span className="character-timeline-line" />
                      </div>
                      <div className="character-timeline-content">
                        <button
                          className={`character-timeline-header ${expandedChapter === app.chapter_index ? 'expanded' : ''}`}
                          onClick={() => setExpandedChapter(
                            expandedChapter === app.chapter_index ? null : app.chapter_index
                          )}
                        >
                          <span className="character-timeline-chapter">
                            {String(app.chapter_index + 1).padStart(2, '0')}
                          </span>
                          <span className="character-timeline-title">{app.chapter_title}</span>
                          <ChevronRight
                            size={16}
                            className={`character-timeline-arrow ${expandedChapter === app.chapter_index ? 'rotated' : ''}`}
                          />
                        </button>

                        {expandedChapter === app.chapter_index && (
                          <div className="character-timeline-details">
                            {app.events?.length > 0 && (
                              <div className="character-timeline-group">
                                <h5>关键事件</h5>
                                <ul>
                                  {app.events.map((e, j) => (
                                    <li key={j}>{e}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {app.interactions?.length > 0 && (
                              <div className="character-timeline-group">
                                <h5>人物互动</h5>
                                <ul>
                                  {app.interactions.map((e, j) => (
                                    <li key={j}>{e}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                            {app.quote && (
                              <blockquote className="character-timeline-quote">
                                「{app.quote}」
                              </blockquote>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Footer */}
          <footer className="character-footer">
            <div className="character-footer-content">
              <span className="character-footer-logo">Book Insight</span>
              <span className="character-footer-divider">·</span>
              <span>{book?.title}</span>
              <span className="character-footer-divider">·</span>
              <span>{result.name}</span>
            </div>
          </footer>
        </article>
      )}
    </div>
  )
}

// Section Title Component
function SectionTitle({ number, title, subtitle }) {
  return (
    <div className="character-section-title">
      <div className="character-section-number">{number}</div>
      <div className="character-section-text">
        <h2>{title}</h2>
        <span>{subtitle}</span>
      </div>
    </div>
  )
}
