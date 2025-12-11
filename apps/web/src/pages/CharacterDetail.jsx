import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  X, ChevronRight, ChevronDown, Loader2, Sparkles,
  Heart, Swords, Users, GraduationCap, BookOpen
} from 'lucide-react'
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
  partner: { label: '伙伴', icon: Users, color: 'indigo' },
  complex: { label: '复杂', icon: Users, color: 'purple' },
}

export default function CharacterDetail() {
  const { name: encodedName } = useParams()
  const name = decodeURIComponent(encodedName || '')
  const { currentBookId } = useBookStore()
  const [expandedChapter, setExpandedChapter] = useState(null)
  const initTheme = useThemeStore((state) => state.initTheme)

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  const {
    status, searchResult, appearances, result, error, progress,
    analyzeCharacter, loadCached,
  } = useCharacterAnalysis(currentBookId)

  useEffect(() => { initTheme() }, [initTheme])

  useEffect(() => {
    if (name && currentBookId) {
      // 只加载缓存，不自动触发分析（分析通过脚本离线执行）
      loadCached(name)
    }
  }, [name, currentBookId, loadCached])

  if (!currentBookId) {
    return (
      <div className="cd-page">
        <div className="cd-empty">
          <BookOpen size={32} strokeWidth={1} />
          <h2>请先选择一本书</h2>
          <p>在主页面的藏书阁中选择要分析的书籍</p>
        </div>
      </div>
    )
  }

  const isLoading = status === 'searching' || status === 'analyzing'

  return (
    <div className="cd-page">
      {/* Controls */}
      <div className="cd-controls">
        <ThemeSwitcher variant="compact" />
        <button onClick={() => window.close()} className="cd-close" title="关闭">
          <X size={18} strokeWidth={1.5} />
        </button>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="cd-loading">
          <div className="cd-loading-label">{status === 'searching' ? '正在搜索' : '正在分析'}</div>
          <h1 className="cd-loading-name">{name}</h1>
          {status === 'analyzing' && searchResult && (
            <div className="cd-progress">
              <div className="cd-progress-bar">
                <div className="cd-progress-fill" style={{ width: `${progress}%` }} />
              </div>
              <p>已分析 {appearances.length} / {Math.min(searchResult.found_in_chapters.length, 30)} 章</p>
            </div>
          )}
          {status === 'searching' && <Loader2 size={24} className="animate-spin" />}
        </div>
      )}

      {/* Error */}
      {error && status === 'completed' && (
        <div className="cd-empty cd-error">
          <X size={32} strokeWidth={1} />
          <h2>分析失败</h2>
          <p>{error}</p>
        </div>
      )}

      {/* No Data */}
      {!result && !error && status === 'completed' && (
        <div className="cd-empty">
          <BookOpen size={32} strokeWidth={1} />
          <h2>暂无分析数据</h2>
          <p>请先运行脚本分析该人物</p>
          <code className="cd-code">python scripts/analyze.py {decodeURIComponent(name)}</code>
        </div>
      )}

      {/* Result */}
      {result && status === 'completed' && (
        <div className="cd-container">
          {/* Header */}
          <header className="cd-header">
            <div className="cd-header-meta">
              <span>人物志</span>
              <span className="cd-dot">·</span>
              <span>{book?.title}</span>
            </div>
            <h1 className="cd-name">{result.name}</h1>
            {result.aliases?.length > 0 && (
              <p className="cd-aliases">{result.aliases.join(' · ')}</p>
            )}
            {result.summary && <p className="cd-summary">{result.summary}</p>}

            {/* Stats */}
            <div className="cd-stats">
              <div className="cd-stat">
                <span className="cd-stat-num">第{result.first_appearance + 1}章</span>
                <span className="cd-stat-label">首次登场</span>
              </div>
              <div className="cd-stat">
                <span className="cd-stat-num">{result.total_chapters}</span>
                <span className="cd-stat-label">出现章节</span>
              </div>
              <div className="cd-stat">
                <span className="cd-stat-num">{result.appearances?.length || 0}</span>
                <span className="cd-stat-label">已分析</span>
              </div>
              <div className="cd-stat">
                <span className="cd-stat-num">{result.total_chapters ? Math.round((result.appearances?.length || 0) / result.total_chapters * 100) : 0}%</span>
                <span className="cd-stat-label">覆盖率</span>
              </div>
            </div>
          </header>

          {/* Main Content - Two Column Layout */}
          <div className="cd-main">
            {/* Left Column */}
            <div className="cd-col-left">
              {/* Growth Arc */}
              {result.growth_arc && (
                <section className="cd-section">
                  <h2 className="cd-section-title">
                    <span className="cd-section-num">01</span>
                    成长轨迹
                  </h2>
                  <p className="cd-growth-text">{result.growth_arc}</p>
                </section>
              )}

              {/* Core Traits */}
              {result.core_traits?.length > 0 && (
                <section className="cd-section">
                  <h2 className="cd-section-title">
                    <span className="cd-section-num">02</span>
                    性格剖析
                  </h2>
                  <div className="cd-traits">
                    {result.core_traits.map((trait, i) => (
                      <div key={i} className="cd-trait">
                        <h3 className="cd-trait-name">{trait.trait}</h3>
                        <p className="cd-trait-desc">{trait.description}</p>
                        {trait.evidence && (
                          <p className="cd-trait-evidence">
                            <Sparkles size={12} />
                            {Array.isArray(trait.evidence) ? trait.evidence[0] : trait.evidence}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Strengths & Weaknesses */}
              {(result.strengths?.length > 0 || result.weaknesses?.length > 0) && (
                <section className="cd-section">
                  <h2 className="cd-section-title">
                    <span className="cd-section-num">03</span>
                    光与影
                  </h2>
                  <div className="cd-balance">
                    {result.strengths?.length > 0 && (
                      <div className="cd-balance-col">
                        <h4><span>✦</span> 优点</h4>
                        <ul>{result.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                      </div>
                    )}
                    {result.weaknesses?.length > 0 && (
                      <div className="cd-balance-col cd-balance-shadow">
                        <h4><span>✧</span> 缺点</h4>
                        <ul>{result.weaknesses.map((w, i) => <li key={i}>{w}</li>)}</ul>
                      </div>
                    )}
                  </div>
                </section>
              )}

              {/* Quotes */}
              {result.notable_quotes?.length > 0 && (
                <section className="cd-section">
                  <h2 className="cd-section-title">
                    <span className="cd-section-num">04</span>
                    经典语录
                  </h2>
                  <div className="cd-quotes">
                    {result.notable_quotes.map((q, i) => (
                      <blockquote key={i} className="cd-quote">「{q}」</blockquote>
                    ))}
                  </div>
                </section>
              )}

              {/* Relations */}
              {result.relations?.length > 0 && (
                <section className="cd-section">
                  <h2 className="cd-section-title">
                    <span className="cd-section-num">05</span>
                    人物关系
                  </h2>
                  <div className="cd-relations">
                    {result.relations.map((rel, i) => {
                      const cfg = relationConfig[rel.relation_type] || { label: rel.relation_type, icon: Users, color: 'gray' }
                      const Icon = cfg.icon
                      return (
                        <div key={i} className={`cd-relation cd-relation-${cfg.color}`}>
                          <div className="cd-relation-avatar">{(rel.target_name || rel.name || '?')[0]}</div>
                          <div className="cd-relation-info">
                            <div className="cd-relation-top">
                              <span className="cd-relation-name">{rel.target_name || rel.name || '未知'}</span>
                              <span className="cd-relation-type"><Icon size={12} />{cfg.label}</span>
                            </div>
                            <p className="cd-relation-desc">{rel.description}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </section>
              )}

              {/* Discovered Characters */}
              {result.discovered_characters?.length > 0 && (
                <section className="cd-section cd-discovered">
                  <h2 className="cd-section-title">
                    <span className="cd-section-num">✦</span>
                    关联人物
                    <span className="cd-section-count">{result.discovered_characters.length} 人</span>
                  </h2>
                  <div className="cd-discovered-list">
                    {result.discovered_characters.map((char, i) => (
                      <span key={i} className="cd-discovered-tag">{char}</span>
                    ))}
                  </div>
                </section>
              )}
            </div>

            {/* Right Column - Chapter Timeline */}
            <div className="cd-col-right">
              <section className="cd-section cd-timeline-section">
                <h2 className="cd-section-title">
                  <span className="cd-section-num">06</span>
                  章节足迹
                  <span className="cd-section-count">{result.appearances?.length || 0} 章</span>
                </h2>

                <div className="cd-timeline">
                  {result.appearances?.map((app) => (
                    <div key={app.chapter_index} className={`cd-chapter ${app.is_mentioned_only ? 'mentioned-only' : ''}`}>
                      <button
                        className={`cd-chapter-btn ${expandedChapter === app.chapter_index ? 'expanded' : ''}`}
                        onClick={() => setExpandedChapter(expandedChapter === app.chapter_index ? null : app.chapter_index)}
                      >
                        <span className="cd-chapter-num">{app.chapter_index + 1}</span>
                        <span className="cd-chapter-title">
                          {app.chapter_title}
                          {app.is_mentioned_only && <span className="cd-mention-tag">仅提及</span>}
                        </span>
                        <ChevronRight size={16} className="cd-chapter-icon" />
                      </button>

                      {expandedChapter === app.chapter_index && (
                        <div className="cd-chapter-content">
                          {app.events?.length > 0 && (
                            <div className="cd-chapter-block">
                              <h5>关键事件</h5>
                              <ul>{app.events.map((e, j) => <li key={j}>{e}</li>)}</ul>
                            </div>
                          )}
                          {app.interactions?.length > 0 && (
                            <div className="cd-chapter-block">
                              <h5>人物互动</h5>
                              <ul>{app.interactions.map((int, j) => (
                                <li key={j}>
                                  {typeof int === 'string'
                                    ? int
                                    : <><strong>{int.character}</strong>：{int.description}</>
                                  }
                                </li>
                              ))}</ul>
                            </div>
                          )}
                          {app.key_moment && (
                            <div className="cd-chapter-block cd-key-moment">
                              <h5>关键时刻</h5>
                              <p>{app.key_moment}</p>
                            </div>
                          )}
                          {app.quote && (
                            <blockquote className="cd-chapter-quote">「{app.quote}」</blockquote>
                          )}
                          {app.emotional_state && (
                            <div className="cd-chapter-emotional">
                              <span className="cd-emotional-label">情感状态</span>
                              <span className="cd-emotional-value">{app.emotional_state}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            </div>
          </div>

          {/* Footer */}
          <footer className="cd-footer">
            <span>Book Insight</span>
            <span className="cd-dot">·</span>
            <span>{book?.title}</span>
            <span className="cd-dot">·</span>
            <span>{result.name}</span>
          </footer>
        </div>
      )}
    </div>
  )
}
