import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const THEMES = {
  light: {
    id: 'light',
    name: '浅色',
    icon: 'sun',
  },
  dark: {
    id: 'dark',
    name: '深色',
    icon: 'moon',
  },
  sepia: {
    id: 'sepia',
    name: '护眼',
    icon: 'eye',
  },
  midnight: {
    id: 'midnight',
    name: '暗夜',
    icon: 'stars',
  },
}

export const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'light',
      themes: THEMES,

      setTheme: (theme) => {
        if (THEMES[theme]) {
          // 更新 DOM
          document.documentElement.setAttribute('data-theme', theme)
          set({ theme })
        }
      },

      // 循环切换主题
      cycleTheme: () => {
        const themeOrder = ['light', 'dark', 'sepia', 'midnight']
        const currentIndex = themeOrder.indexOf(get().theme)
        const nextIndex = (currentIndex + 1) % themeOrder.length
        get().setTheme(themeOrder[nextIndex])
      },

      // 初始化主题（在 app 启动时调用）
      initTheme: () => {
        const { theme } = get()
        document.documentElement.setAttribute('data-theme', theme)
      },
    }),
    {
      name: 'book-insight-theme',
      onRehydrateStorage: () => (state) => {
        // 持久化恢复后，确保 DOM 同步
        if (state) {
          document.documentElement.setAttribute('data-theme', state.theme)
        }
      },
    }
  )
)
