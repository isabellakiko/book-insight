import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { Book, MessageSquare, Users, Clock, Feather } from 'lucide-react'
import { clsx } from 'clsx'

import Dashboard from './pages/Dashboard'
import RAGChat from './pages/RAGChat'
import Characters from './pages/Characters'
import CharacterDetail from './pages/CharacterDetail'
import Timeline from './pages/Timeline'
import ChapterAnalysis from './pages/ChapterAnalysis'

const navItems = [
  { path: '/', icon: Book, label: '藏书阁', subtitle: 'Library' },
  { path: '/chat', icon: MessageSquare, label: '问答', subtitle: 'Dialogue' },
  { path: '/characters', icon: Users, label: '人物志', subtitle: 'Characters' },
  { path: '/timeline', icon: Clock, label: '编年史', subtitle: 'Chronicle' },
]

function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-72 bg-paper-dark flex flex-col border-r border-paper-lighter/50">
      {/* Logo */}
      <div className="p-8 pb-6">
        <div className="flex items-center gap-3 mb-1">
          <Feather className="w-6 h-6 text-gold" strokeWidth={1.5} />
          <h1 className="font-display text-2xl font-semibold tracking-tight">
            Book Insight
          </h1>
        </div>
        <p className="text-sm text-[var(--text-muted)] ml-9 tracking-wide">
          Literary Analysis
        </p>
      </div>

      {/* Decorative Line */}
      <div className="mx-6 mb-6">
        <div className="h-px bg-gradient-to-r from-gold/60 via-paper-lighter to-transparent" />
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4">
        <div className="space-y-1">
          {navItems.map(({ path, icon: Icon, label, subtitle }) => {
            const isActive = location.pathname === path ||
              (path !== '/' && location.pathname.startsWith(path))

            return (
              <NavLink
                key={path}
                to={path}
                className={clsx(
                  'group flex items-center gap-4 px-4 py-3.5 rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-paper text-[var(--text-primary)]'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-paper/50'
                )}
              >
                <div className={clsx(
                  'relative flex items-center justify-center w-10 h-10 rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-gold/15'
                    : 'bg-paper-light/50 group-hover:bg-paper-light'
                )}>
                  <Icon
                    size={20}
                    strokeWidth={1.5}
                    className={clsx(
                      'transition-colors',
                      isActive ? 'text-gold' : 'text-[var(--text-muted)] group-hover:text-[var(--text-secondary)]'
                    )}
                  />
                  {isActive && (
                    <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-gold rounded-full" />
                  )}
                </div>
                <div className="flex flex-col">
                  <span className={clsx(
                    'font-medium text-[0.9375rem] leading-tight',
                    isActive && 'text-[var(--text-primary)]'
                  )}>
                    {label}
                  </span>
                  <span className={clsx(
                    'text-2xs tracking-wider uppercase',
                    isActive ? 'text-gold/70' : 'text-[var(--text-muted)]'
                  )}>
                    {subtitle}
                  </span>
                </div>
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-6 mt-auto">
        <div className="p-4 rounded-lg bg-paper/50 border border-paper-lighter/50">
          <p className="text-xs text-[var(--text-muted)] leading-relaxed">
            <span className="text-gold font-medium">AI 驱动</span> · 深度解析文学作品中的人物性格、情节发展与叙事结构
          </p>
        </div>
      </div>
    </aside>
  )
}

export default function App() {
  const location = useLocation()

  // 人物详情页使用独立全屏布局
  const isCharacterDetail = location.pathname.startsWith('/characters/') && location.pathname !== '/characters'

  if (isCharacterDetail) {
    return (
      <Routes>
        <Route path="/characters/:name" element={<CharacterDetail />} />
      </Routes>
    )
  }

  return (
    <div className="flex h-screen bg-ink">
      <Sidebar />
      <main className="flex-1 overflow-auto bg-paper-dark/30">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<RAGChat />} />
          <Route path="/characters" element={<Characters />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/chapters/:bookId" element={<ChapterAnalysis />} />
        </Routes>
      </main>
    </div>
  )
}
