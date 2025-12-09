import { Routes, Route, NavLink } from 'react-router-dom'
import { Book, MessageSquare, Users, Clock, Settings } from 'lucide-react'
import { clsx } from 'clsx'

import Dashboard from './pages/Dashboard'
import RAGChat from './pages/RAGChat'
import Characters from './pages/Characters'
import Timeline from './pages/Timeline'
import ChapterAnalysis from './pages/ChapterAnalysis'

const navItems = [
  { path: '/', icon: Book, label: '书籍' },
  { path: '/chat', icon: MessageSquare, label: 'RAG 问答' },
  { path: '/characters', icon: Users, label: '人物' },
  { path: '/timeline', icon: Clock, label: '时间线' },
]

function Sidebar() {
  return (
    <aside className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-xl font-bold text-white">Book Insight</h1>
        <p className="text-sm text-slate-400 mt-1">AI 书籍分析</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-700'
              )
            }
          >
            <Icon size={20} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-slate-700">
        <NavLink
          to="/settings"
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors"
        >
          <Settings size={20} />
          <span>设置</span>
        </NavLink>
      </div>
    </aside>
  )
}

export default function App() {
  return (
    <div className="flex h-screen">
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
