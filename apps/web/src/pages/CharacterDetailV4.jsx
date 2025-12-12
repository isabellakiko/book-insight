import { useState, useEffect, useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ChevronRight, ChevronDown, Sparkles, Quote,
  Heart, Swords, Users, GraduationCap, BookOpen,
  Handshake, ArrowRight, Pin, FileText, Minus,
  Network, Loader2, ArrowLeft, User, TrendingUp,
  Shield, AlertCircle
} from 'lucide-react'
import { booksApi, analysisApi } from '../services/api'
import { useBookStore } from '../stores/bookStore'
import { useThemeStore } from '../stores/themeStore'
import ThemeSwitcher from '../components/ThemeSwitcher'

// ============================================
// Constants
// ============================================

const SECTIONS = [
  { id: 'overview', label: '概览', icon: User },
  { id: 'growth', label: '成长轨迹', icon: TrendingUp },
  { id: 'personality', label: '性格分析', icon: Shield },
  { id: 'relations', label: '人物关系', icon: Users },
  { id: 'chapters', label: '章节足迹', icon: BookOpen },
  { id: 'connections', label: '关联人物', icon: Network },
]

const RELATION_CONFIG = {
  lover: { label: '恋人', icon: Heart, color: 'rose' },
  family: { label: '亲人', icon: Users, color: 'amber' },
  friend: { label: '挚友', icon: Users, color: 'emerald' },
  rival: { label: '对手', icon: Swords, color: 'orange' },
  enemy: { label: '敌人', icon: Swords, color: 'red' },
  mentor: { label: '导师', icon: GraduationCap, color: 'blue' },
  student: { label: '学生', icon: GraduationCap, color: 'cyan' },
  partner: { label: '伙伴', icon: Handshake, color: 'indigo' },
  complex: { label: '复杂', icon: Users, color: 'purple' },
}

const ROLE_LABELS = {
  protagonist: '主角',
  antagonist: '反派',
  supporting: '配角',
  minor: '次要',
}

// ============================================
// Sidebar Component
// ============================================

function Sidebar({ result, book, activeSection, onSectionClick }) {
  const navigate = useNavigate()
  const coverage = result?.total_chapters
    ? Math.round((result?.appearances?.length || 0) / result.total_chapters * 100)
    : 0

  return (
    <aside className="cv4-sidebar">
      {/* Back */}
      <button className="cv4-back" onClick={() => navigate('/characters')}>
        <ArrowLeft size={16} />
        返回人物志
      </button>

      {/* Profile Card */}
      <div className="cv4-profile">
        <div className="cv4-avatar">{result?.name?.[0] || '?'}</div>
        <h1 className="cv4-name">{result?.name}</h1>
        {result?.aliases?.length > 0 && (
          <p className="cv4-aliases">{result.aliases.join(' · ')}</p>
        )}
        {result?.role && (
          <span className="cv4-role">{ROLE_LABELS[result.role] || result.role}</span>
        )}
      </div>

      {/* Quick Stats */}
      <div className="cv4-stats">
        <div className="cv4-stat">
          <span className="cv4-stat-val">第{(result?.first_appearance || 0) + 1}章</span>
          <span className="cv4-stat-lbl">首次登场</span>
        </div>
        <div className="cv4-stat">
          <span className="cv4-stat-val">{result?.total_chapters || 0}</span>
          <span className="cv4-stat-lbl">出现章节</span>
        </div>
        <div className="cv4-stat">
          <span className="cv4-stat-val">{result?.appearances?.length || 0}</span>
          <span className="cv4-stat-lbl">已分析</span>
        </div>
        <div className="cv4-stat">
          <span className="cv4-stat-val">{coverage}%</span>
          <span className="cv4-stat-lbl">覆盖率</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="cv4-nav">
        <div className="cv4-nav-title">目录</div>
        {SECTIONS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`cv4-nav-item ${activeSection === id ? 'active' : ''}`}
            onClick={() => onSectionClick(id)}
          >
            <Icon size={16} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* Book Info */}
      <div className="cv4-book-info">
        <BookOpen size={14} />
        <span>{book?.title || '未知书籍'}</span>
      </div>
    </aside>
  )
}

// ============================================
// Content Sections
// ============================================

function OverviewSection({ result }) {
  return (
    <div className="cv4-content">
      <h2 className="cv4-title">概览</h2>

      {/* Summary */}
      {result?.summary && (
        <div className="cv4-block cv4-block--highlight">
          <p className="cv4-text cv4-text--lg">{result.summary}</p>
        </div>
      )}

      {/* Description & Personality */}
      <div className="cv4-grid cv4-grid--2">
        {result?.description && result.description !== result.summary && (
          <div className="cv4-block">
            <h3 className="cv4-subtitle">详细描述</h3>
            <p className="cv4-text">{result.description}</p>
          </div>
        )}

        {result?.personality?.length > 0 && (
          <div className="cv4-block">
            <h3 className="cv4-subtitle">性格特点</h3>
            <div className="cv4-tags">
              {result.personality.map((p, i) => (
                <span key={i} className="cv4-tag">{p}</span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Quick Stats Cards */}
      {(result?.relations?.length > 0 || result?.notable_quotes?.length > 0) && (
        <div className="cv4-grid cv4-grid--3">
          {result?.relations?.length > 0 && (
            <div className="cv4-mini-card">
              <Users size={20} />
              <span className="cv4-mini-val">{result.relations.length}</span>
              <span className="cv4-mini-lbl">人物关系</span>
            </div>
          )}
          {result?.core_traits?.length > 0 && (
            <div className="cv4-mini-card">
              <Shield size={20} />
              <span className="cv4-mini-val">{result.core_traits.length}</span>
              <span className="cv4-mini-lbl">核心特质</span>
            </div>
          )}
          {result?.notable_quotes?.length > 0 && (
            <div className="cv4-mini-card">
              <Quote size={20} />
              <span className="cv4-mini-val">{result.notable_quotes.length}</span>
              <span className="cv4-mini-lbl">经典语录</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function GrowthSection({ result }) {
  const [expandedTrait, setExpandedTrait] = useState(null)

  return (
    <div className="cv4-content">
      <h2 className="cv4-title">成长轨迹</h2>

      {/* Growth Arc */}
      {result?.growth_arc && (
        <div className="cv4-block cv4-block--highlight">
          <p className="cv4-text">{result.growth_arc}</p>
        </div>
      )}

      {/* Core Traits */}
      {result?.core_traits?.length > 0 && (
        <>
          <h3 className="cv4-subtitle">核心特质</h3>
          <div className="cv4-traits-grid">
            {result.core_traits.map((trait, i) => (
              <div
                key={i}
                className={`cv4-trait ${expandedTrait === i ? 'expanded' : ''}`}
                onClick={() => setExpandedTrait(expandedTrait === i ? null : i)}
              >
                <div className="cv4-trait-header">
                  <h4>{trait.trait}</h4>
                  <ChevronRight size={16} className="cv4-trait-arrow" />
                </div>
                <p className="cv4-trait-desc">{trait.description}</p>
                {expandedTrait === i && trait.evidence && (
                  <div className="cv4-trait-evidence">
                    <Sparkles size={12} />
                    <span>{Array.isArray(trait.evidence) ? trait.evidence[0] : trait.evidence}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function PersonalitySection({ result }) {
  return (
    <div className="cv4-content">
      <h2 className="cv4-title">性格分析</h2>

      {/* Strengths & Weaknesses */}
      <div className="cv4-grid cv4-grid--2">
        {result?.strengths?.length > 0 && (
          <div className="cv4-block cv4-block--light">
            <h3 className="cv4-subtitle"><span>✦</span> 优点</h3>
            <ul className="cv4-list">
              {result.strengths.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          </div>
        )}
        {result?.weaknesses?.length > 0 && (
          <div className="cv4-block cv4-block--shadow">
            <h3 className="cv4-subtitle"><span>✧</span> 缺点</h3>
            <ul className="cv4-list">
              {result.weaknesses.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>
        )}
      </div>

      {/* Notable Quotes */}
      {result?.notable_quotes?.length > 0 && (
        <>
          <h3 className="cv4-subtitle">经典语录</h3>
          <div className="cv4-quotes-grid">
            {result.notable_quotes.map((q, i) => (
              <blockquote key={i} className="cv4-quote">
                <Quote size={16} className="cv4-quote-icon" />
                「{q}」
              </blockquote>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function RelationsSection({ result }) {
  const navigate = useNavigate()
  const [expandedRel, setExpandedRel] = useState(null)

  if (!result?.relations?.length) {
    return (
      <div className="cv4-content">
        <h2 className="cv4-title">人物关系</h2>
        <div className="cv4-empty">
          <Users size={48} strokeWidth={1} />
          <p>暂无关系数据</p>
        </div>
      </div>
    )
  }

  return (
    <div className="cv4-content">
      <h2 className="cv4-title">人物关系 <span className="cv4-count">{result.relations.length}人</span></h2>

      <div className="cv4-relations-grid">
        {result.relations.map((rel, i) => {
          const config = RELATION_CONFIG[rel.relation_type] || RELATION_CONFIG.complex
          const Icon = config.icon
          const name = rel.target_name || rel.name || '未知'
          const isExpanded = expandedRel === i

          return (
            <div
              key={i}
              className={`cv4-relation cv4-relation--${config.color} ${isExpanded ? 'expanded' : ''}`}
            >
              <div className="cv4-relation-header" onClick={() => setExpandedRel(isExpanded ? null : i)}>
                <div className="cv4-relation-avatar">{name[0]}</div>
                <div className="cv4-relation-info">
                  <span className="cv4-relation-name">{name}</span>
                  <span className="cv4-relation-type">
                    <Icon size={12} /> {config.label}
                  </span>
                </div>
                <ChevronDown size={16} className="cv4-relation-arrow" />
              </div>

              {isExpanded && (
                <div className="cv4-relation-details">
                  <p>{rel.description}</p>
                  {rel.objective_basis && (
                    <div className="cv4-relation-row">
                      <span>依据：</span>{rel.objective_basis}
                    </div>
                  )}
                  <button
                    className="cv4-relation-link"
                    onClick={() => navigate(`/characters/${encodeURIComponent(name)}`)}
                  >
                    查看人物 <ArrowRight size={14} />
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function ChaptersSection({ result }) {
  const [expandedGroup, setExpandedGroup] = useState('high')
  const [expandedChapter, setExpandedChapter] = useState(null)

  const groups = useMemo(() => {
    const g = {
      high: { name: '关键章节', icon: Pin, items: [] },
      medium: { name: '一般章节', icon: FileText, items: [] },
      low: { name: '次要章节', icon: Minus, items: [] },
      mentioned: { name: '仅提及', icon: Quote, items: [] },
    }
    result?.appearances?.forEach((app) => {
      if (app.is_mentioned_only) g.mentioned.items.push(app)
      else {
        const sig = app.chapter_significance || 'medium'
        if (g[sig]) g[sig].items.push(app)
        else g.medium.items.push(app)
      }
    })
    return g
  }, [result?.appearances])

  if (!result?.appearances?.length) {
    return (
      <div className="cv4-content">
        <h2 className="cv4-title">章节足迹</h2>
        <div className="cv4-empty">
          <BookOpen size={48} strokeWidth={1} />
          <p>暂无章节数据</p>
        </div>
      </div>
    )
  }

  return (
    <div className="cv4-content">
      <h2 className="cv4-title">章节足迹 <span className="cv4-count">{result.appearances.length}章</span></h2>

      {/* Stats Bar */}
      <div className="cv4-chapter-stats">
        {Object.entries(groups).map(([key, g]) => (
          <div key={key} className={`cv4-chapter-stat ${expandedGroup === key ? 'active' : ''}`} onClick={() => setExpandedGroup(key)}>
            <g.icon size={14} />
            <span>{g.name}</span>
            <span className="cv4-chapter-stat-num">{g.items.length}</span>
          </div>
        ))}
      </div>

      {/* Chapter List */}
      <div className="cv4-chapters-list">
        {groups[expandedGroup]?.items.map((app) => (
          <div key={app.chapter_index} className="cv4-chapter">
            <button
              className={`cv4-chapter-header ${expandedChapter === app.chapter_index ? 'expanded' : ''}`}
              onClick={() => setExpandedChapter(expandedChapter === app.chapter_index ? null : app.chapter_index)}
            >
              <span className="cv4-chapter-num">{app.chapter_index + 1}</span>
              <span className="cv4-chapter-title">{app.chapter_title}</span>
              {app.emotional_state && <span className="cv4-chapter-emotion">{app.emotional_state}</span>}
              <ChevronRight size={14} className="cv4-chapter-arrow" />
            </button>

            {expandedChapter === app.chapter_index && (
              <div className="cv4-chapter-content">
                {app.key_moment && (
                  <div className="cv4-chapter-block cv4-chapter-block--highlight">
                    <h5>关键时刻</h5>
                    <p>{app.key_moment}</p>
                  </div>
                )}
                {app.events?.length > 0 && (
                  <div className="cv4-chapter-block">
                    <h5>关键事件</h5>
                    <ul>{app.events.map((e, j) => <li key={j}>{e}</li>)}</ul>
                  </div>
                )}
                {app.interactions?.length > 0 && (
                  <div className="cv4-chapter-block">
                    <h5>人物互动</h5>
                    <ul>
                      {app.interactions.map((int, j) => (
                        <li key={j}>
                          {typeof int === 'string' ? int : <><strong>{int.character}</strong>：{int.description}</>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {app.quote && <blockquote className="cv4-chapter-quote">「{app.quote}」</blockquote>}
              </div>
            )}
          </div>
        ))}

        {groups[expandedGroup]?.items.length === 0 && (
          <div className="cv4-empty cv4-empty--sm">
            <p>该分类下暂无章节</p>
          </div>
        )}
      </div>
    </div>
  )
}

function ConnectionsSection({ result }) {
  const navigate = useNavigate()

  if (!result?.discovered_characters?.length) {
    return (
      <div className="cv4-content">
        <h2 className="cv4-title">关联人物</h2>
        <div className="cv4-empty">
          <Network size={48} strokeWidth={1} />
          <p>暂无关联人物数据</p>
        </div>
      </div>
    )
  }

  return (
    <div className="cv4-content">
      <h2 className="cv4-title">关联人物 <span className="cv4-count">{result.discovered_characters.length}人</span></h2>

      <div className="cv4-connections">
        {result.discovered_characters.map((char, i) => (
          <button
            key={i}
            className="cv4-connection"
            onClick={() => navigate(`/characters/${encodeURIComponent(char)}`)}
          >
            <span className="cv4-connection-avatar">{char[0]}</span>
            <span>{char}</span>
            <ArrowRight size={12} />
          </button>
        ))}
      </div>
    </div>
  )
}

// ============================================
// Main Component
// ============================================

export default function CharacterDetailV4() {
  const navigate = useNavigate()
  const { name: encodedName } = useParams()
  const name = decodeURIComponent(encodedName || '')
  const { currentBookId } = useBookStore()
  const initTheme = useThemeStore((state) => state.initTheme)
  const [activeSection, setActiveSection] = useState('overview')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const { data: book } = useQuery({
    queryKey: ['book', currentBookId],
    queryFn: () => booksApi.get(currentBookId),
    enabled: !!currentBookId,
  })

  useEffect(() => { initTheme() }, [initTheme])

  useEffect(() => {
    if (name && currentBookId) {
      setIsLoading(true)
      setError(null)
      analysisApi.getDetailedCharacter(currentBookId, name)
        .then((data) => {
          if (data && data.appearances && data.appearances.length > 0) {
            setResult(data)
          } else {
            setError('暂无分析数据')
          }
        })
        .catch((err) => {
          console.error('Failed to load character:', err)
          setError('加载失败')
        })
        .finally(() => setIsLoading(false))
    }
  }, [name, currentBookId])

  // Loading
  if (isLoading) {
    return (
      <div className="cv4-page cv4-page--center">
        <Loader2 size={32} className="cv4-spinner" />
        <p>加载中...</p>
      </div>
    )
  }

  // No book
  if (!currentBookId) {
    return (
      <div className="cv4-page cv4-page--center">
        <BookOpen size={48} strokeWidth={1} />
        <h2>请先选择一本书</h2>
        <p>在主页面的藏书阁中选择要分析的书籍</p>
      </div>
    )
  }

  // Error
  if (error || !result) {
    return (
      <div className="cv4-page cv4-page--center">
        <AlertCircle size={48} strokeWidth={1} />
        <h2>{error || '暂无分析数据'}</h2>
        <p>请先运行脚本分析该人物</p>
        <code className="cv4-code">python scripts/analyze.py {name}</code>
      </div>
    )
  }

  return (
    <div className="cv4-page">
      <Sidebar
        result={result}
        book={book}
        activeSection={activeSection}
        onSectionClick={setActiveSection}
      />

      <main className="cv4-main">
        <div className="cv4-theme-btn">
          <ThemeSwitcher variant="compact" />
        </div>

        {activeSection === 'overview' && <OverviewSection result={result} />}
        {activeSection === 'growth' && <GrowthSection result={result} />}
        {activeSection === 'personality' && <PersonalitySection result={result} />}
        {activeSection === 'relations' && <RelationsSection result={result} />}
        {activeSection === 'chapters' && <ChaptersSection result={result} />}
        {activeSection === 'connections' && <ConnectionsSection result={result} />}
      </main>
    </div>
  )
}
