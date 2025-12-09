# 状态管理文档

> Zustand Store 参考

**位置**: `apps/web/src/stores/`
**库**: Zustand 5.0
**最后更新**: 2025-12-09

---

## Store 概览

| Store | 文件 | 描述 |
|-------|------|------|
| bookStore | `bookStore.js` | 书籍选择和 UI 状态管理 |

---

## bookStore

### 状态
```javascript
{
  // 当前选中的书籍 ID
  currentBookId: null,

  // 侧边栏展开/收起状态
  sidebarOpen: true
}
```

### Actions
```javascript
// 设置当前书籍
setCurrentBook(bookId)

// 切换侧边栏
toggleSidebar()
```

### 使用示例
```jsx
import { useBookStore } from '../stores/bookStore';

function BookList() {
  const { currentBookId, setCurrentBook } = useBookStore();

  return (
    <ul>
      {books.map(book => (
        <li
          key={book.id}
          onClick={() => setCurrentBook(book.id)}
          className={book.id === currentBookId ? 'active' : ''}
        >
          {book.title}
        </li>
      ))}
    </ul>
  );
}
```

### 持久化
Store 使用 `persist` 中间件自动持久化到 localStorage：

```javascript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useBookStore = create(
  persist(
    (set) => ({
      currentBookId: null,
      setCurrentBook: (bookId) => set({ currentBookId: bookId }),
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    }),
    {
      name: 'book-insight-store'
    }
  )
);
```

---

## 设计原则

### 1. 最小化状态
只存储必要的全局状态：
- **currentBookId**: 跨页面共享当前选中的书籍
- **sidebarOpen**: UI 偏好设置

页面级状态使用组件内 state 或 TanStack Query。

### 2. 与 TanStack Query 配合
- **服务器状态**: 使用 TanStack Query（书籍列表、分析结果、章节内容）
- **客户端状态**: 使用 Zustand（UI 状态、用户偏好）

### 3. 持久化策略
使用 localStorage 持久化用户偏好，确保刷新页面后状态保持。

---

## 相关文件

- **API 服务**: `apps/web/src/services/api.js`
- **页面组件**: `apps/web/src/pages/`
