import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useBookStore = create(
  persist(
    (set) => ({
      // Current selected book
      currentBookId: null,
      setCurrentBook: (bookId) => set({ currentBookId: bookId }),

      // UI state
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    {
      name: 'book-insight-store',
    }
  )
)
