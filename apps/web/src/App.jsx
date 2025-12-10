import { useEffect } from 'react'
import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { Book, MessageSquare, Users, Clock, BookOpen } from 'lucide-react'
import { clsx } from 'clsx'

import Dashboard from './pages/Dashboard'
import RAGChat from './pages/RAGChat'
import Characters from './pages/Characters'
import CharacterDetail from './pages/CharacterDetail'
import Timeline from './pages/Timeline'
import ChapterAnalysis from './pages/ChapterAnalysis'
import ThemeSwitcher from './components/ThemeSwitcher'
import { useThemeStore } from './stores/themeStore'

const navItems = [
  { path: '/', icon: Book, label: '藏书阁' },
  { path: '/chat', icon: MessageSquare, label: '问答' },
  { path: '/characters', icon: Users, label: '人物志' },
  { path: '/timeline', icon: Clock, label: '时间线' },
]

function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-surface-secondary flex flex-col border-r border-border">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-accent-surface flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-accent" strokeWidth={1.5} />
          </div>
          <div>
            <h1 className="font-semibold text-text-primary text-[0.9375rem] leading-tight">
              Book Insight
            </h1>
            <p className="text-xs text-text-muted">
              AI 书籍分析
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3">
        <div className="space-y-1">
          {navItems.map(({ path, icon: Icon, label }) => {
            const isActive = location.pathname === path ||
              (path !== '/' && location.pathname.startsWith(path))

            return (
              <NavLink
                key={path}
                to={path}
                className={clsx(
                  'nav-bookmark',
                  isActive && 'active'
                )}
              >
                <Icon size={18} strokeWidth={1.5} />
                <span className="font-medium text-[0.875rem]">{label}</span>
              </NavLink>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted">主题</span>
          <ThemeSwitcher />
        </div>
      </div>
    </aside>
  )
}

export default function App() {
  const location = useLocation()
  const initTheme = useThemeStore((state) => state.initTheme)

  // 初始化主题
  useEffect(() => {
    initTheme()
  }, [initTheme])

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
    <div className="flex h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 overflow-auto">
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
