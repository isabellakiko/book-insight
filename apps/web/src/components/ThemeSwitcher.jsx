import { useThemeStore } from '../stores/themeStore'

// 简洁的图标组件
const Icons = {
  sun: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/>
      <line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/>
      <line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  ),
  moon: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  ),
  eye: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  ),
  stars: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"/>
      <circle cx="12" cy="12" r="4"/>
    </svg>
  ),
}

export function ThemeSwitcher({ variant = 'default' }) {
  const { theme, themes, setTheme } = useThemeStore()
  const themeOrder = ['light', 'dark', 'sepia', 'midnight']

  if (variant === 'compact') {
    // 紧凑版：只显示当前主题图标，点击循环
    const { cycleTheme } = useThemeStore()
    return (
      <button
        onClick={cycleTheme}
        className="btn btn-ghost btn-icon"
        title={`当前: ${themes[theme].name}`}
      >
        {Icons[themes[theme].icon]}
      </button>
    )
  }

  // 完整版：显示所有主题选项
  return (
    <div className="theme-switcher">
      {themeOrder.map((themeId) => (
        <button
          key={themeId}
          onClick={() => setTheme(themeId)}
          className={`theme-option ${theme === themeId ? 'active' : ''}`}
          title={themes[themeId].name}
        >
          {Icons[themes[themeId].icon]}
        </button>
      ))}
    </div>
  )
}

export default ThemeSwitcher
