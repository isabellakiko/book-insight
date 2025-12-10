# 状态管理文档

> Zustand Store 参考

**位置**: `apps/web/src/stores/`
**库**: Zustand 5.0
**最后更新**: 2025-12-11

---

## Store 概览

| Store | 文件 | 描述 |
|-------|------|------|
| bookStore | `bookStore.js` | 书籍选择和 UI 状态管理 |
| themeStore | `themeStore.js` | 主题切换（4 套主题） |

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

## themeStore

### 状态
```javascript
{
  theme: 'light',  // 当前主题 ID
  themes: THEMES,  // 主题配置对象（包含所有主题元数据）
}
```

### 可用主题

| ID | 名称 | 图标 | 说明 |
|----|------|------|------|
| light | 浅色 | Sun | 默认亮色主题 |
| dark | 深色 | Moon | 暗色模式 |
| sepia | 护眼 | Eye | 暖色护眼模式 |
| midnight | 暗夜 | Stars | 深蓝暗夜主题 |

### Actions
```javascript
// 设置指定主题
setTheme(theme)   // 自动更新 DOM data-theme 属性

// 循环切换主题
cycleTheme()      // light → dark → sepia → midnight → light

// 初始化主题（应用启动时调用）
initTheme()       // 从 localStorage 恢复或使用默认主题
```

### 持久化
- **存储 key**: `book-insight-theme`
- **中间件**: Zustand persist
- **特殊处理**: `onRehydrateStorage` 确保持久化恢复后 DOM 同步

```javascript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useThemeStore = create(
  persist(
    (set, get) => ({
      theme: 'light',
      themes: THEMES,
      setTheme: (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        set({ theme });
      },
      // ...
    }),
    {
      name: 'book-insight-theme',
      onRehydrateStorage: () => (state) => {
        // 持久化恢复后，确保 DOM 同步
        if (state?.theme) {
          document.documentElement.setAttribute('data-theme', state.theme);
        }
      },
    }
  )
);
```

### 使用示例
```jsx
import { useThemeStore } from '../stores/themeStore';

function Header() {
  const { theme, setTheme, cycleTheme } = useThemeStore();

  return (
    <button onClick={cycleTheme}>
      当前主题: {theme}
    </button>
  );
}
```

### ThemeSwitcher 组件

**位置**: `apps/web/src/components/ThemeSwitcher.jsx`

主题切换组件，支持两种显示模式：

| variant | 说明 | 适用场景 |
|---------|------|----------|
| `default` | 显示所有 4 个主题按钮 | 设置页面、侧边栏 |
| `compact` | 单图标，点击循环切换 | 导航栏、紧凑空间 |

**使用示例**:
```jsx
<ThemeSwitcher />                    {/* 完整版 - 显示所有主题 */}
<ThemeSwitcher variant="compact" />  {/* 紧凑版 - 单图标循环 */}
```

**集成位置**:
- `App.jsx` 侧边栏底部（default 模式）
- `CharacterDetail.jsx` 浮动控制栏（compact 模式）

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

## 与 Hook 的协作关系

### useCharacterAnalysis Hook

此 Hook 处理人物分析的 SSE 流式状态，与 `bookStore` 协作获取 `currentBookId`。

> 完整 API 参考：[hooks.md](./hooks.md)

| 职责划分 | 负责方 | 说明 |
|----------|--------|------|
| 当前书籍 ID | bookStore | 跨页面共享，持久化 |
| 分析状态 | useCharacterAnalysis | 页面级，SSE 流式 |
| 分析结果缓存 | TanStack Query | 服务器状态，自动失效 |

### 组件依赖图

```
CharacterDetail
├── useBookStore → currentBookId
├── useCharacterAnalysis(bookId)
│   ├── analyzeCharacter(name) → SSE 流
│   └── loadCached(name) → API 缓存
└── UI 渲染（进度条、分析结果）

RAGChat
├── useBookStore → currentBookId
├── useQuery(['rag-status']) → 索引状态
├── useMutation → 发送问题
└── 消息列表渲染

Dashboard
├── useQuery(['books']) → 书籍列表
├── useMutation(upload) → 上传书籍
├── useMutation(delete) → 删除书籍
└── useBookStore.setCurrentBook → 选择书籍
```

### 状态管理原则

1. **全局状态**（Zustand）
   - 用户选择：`currentBookId`
   - UI 偏好：`sidebarOpen`
   - 特点：需要跨页面共享、需要持久化

2. **页面状态**（组件内 useState）
   - 表单输入
   - 临时 UI 状态（展开/折叠）
   - 特点：页面内部使用、无需持久化

3. **服务器状态**（TanStack Query）
   - 书籍列表、章节数据
   - 分析结果缓存
   - 特点：来自服务器、需要缓存和自动刷新

4. **流式状态**（自定义 Hook）
   - SSE 进度（useCharacterAnalysis）
   - 特点：实时更新、需要连接管理

---

## 相关文件

- **API 服务**: `apps/web/src/services/api.js`
- **页面组件**: `apps/web/src/pages/`
- **自定义 Hooks**: [hooks.md](./hooks.md)
