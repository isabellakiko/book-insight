# 前端页面文档

> React 页面组件参考

**位置**: `apps/web/src/pages/`
**框架**: React 18 + Vite
**最后更新**: 2025-12-09

---

## 页面概览

| 页面 | 文件 | 路由 | 描述 |
|------|------|------|------|
| Dashboard | `Dashboard.jsx` | `/` | 首页，书籍管理 |
| RAG Chat | `RAGChat.jsx` | `/chat` | 智能问答 |
| Characters | `Characters.jsx` | `/characters` | 人物列表 |
| Character Detail | `CharacterDetail.jsx` | `/characters/:name` | 人物详情（全屏） |
| Timeline | `Timeline.jsx` | `/timeline` | 情节时间线 |
| Chapter Analysis | `ChapterAnalysis.jsx` | `/chapters/:bookId` | 章节分析 |

---

## Dashboard（首页）

### 功能
- 显示已上传的书籍列表
- 上传新书籍
- 进入各功能模块入口

### 主要组件
```jsx
function Dashboard() {
  // 书籍列表
  // 上传按钮
  // 书籍卡片（点击进入详情）
}
```

### 状态
- `books`: 书籍列表
- `isUploading`: 上传状态

---

## RAGChat（智能问答）

### 功能
- 基于书籍内容的问答
- 显示答案来源章节
- 对话历史
- 示例问题提示

### 依赖
使用 `useBookStore` 获取当前选中的书籍 ID（`currentBookId`）

### 主要组件
```jsx
function RAGChat() {
  // 消息列表
  // 输入框
  // 来源引用展示
}
```

---

## Characters（人物列表）

### 功能
- 显示已分析的人物卡片列表
- 搜索框输入人物名字触发分析
- 点击人物卡片在新标签页打开详情

### 依赖
使用 `useBookStore` 获取当前选中的书籍 ID（`currentBookId`）

### 主要组件
```jsx
function Characters() {
  // 搜索框 - 输入人物名触发分析
  // 已分析人物网格 - 点击跳转详情页
}
```

### 跳转方式
使用 `window.open()` 在新标签页打开人物详情：
```javascript
window.open(`/characters/${encodeURIComponent(name)}`, '_blank')
```

---

## CharacterDetail（人物详情）

### 功能
- 全屏独立布局（无侧边栏）
- 展示人物完整档案：
  - 基础信息（名字、别名、首次出场、出场章数）
  - 人物概述（Summary）
  - 成长轨迹（Growth Arc）
  - 性格剖析（Core Traits）
  - 优点 / 缺点
  - 经典语录
  - 人物关系
  - 章节出现（可展开查看事件、互动、台词）
- 流式分析进度显示（SSE）
- 浮动关闭按钮

### URL 参数
| 参数 | 类型 | 描述 |
|------|------|------|
| name | string | 人物名称（URL 编码） |

### 布局特点
- 独立全屏布局，不使用主布局的侧边栏
- Editorial 杂志风格设计
- 编号式 Section Header（01、02、03...）

### 依赖
- `useBookStore` - 获取 `currentBookId`
- `useCharacterAnalysis` - 人物分析 Hook（SSE 流式）

### 主要组件
```jsx
function CharacterDetail() {
  // Loading 状态 - 流式分析进度
  // Error 状态 - 分析失败提示
  // Result 状态 - 完整人物档案展示
}

function SectionHeader({ number, title, subtitle }) {
  // 编号式标题组件（01 成长轨迹 Growth Arc）
}
```

---

## Timeline（情节时间线）

### 功能
- 竖直时间线视图
- 每个事件显示：章节号、标题、摘要、关键事件、涉及人物
- 时间线样式：竖线 + 圆点 + 卡片

### 依赖
使用 `useBookStore` 获取当前选中的书籍 ID（`currentBookId`）

---

## ChapterAnalysis（章节分析）

### 功能
- 三栏布局：章节列表 | 章节内容 | 分析面板
- 章节列表：支持快速导航，显示分析状态（绿色对号）
- 章节内容：完整文本展示
- 分析面板：摘要、人物、事件、情感、关键词
- 手动触发分析按钮

### URL 参数
| 参数 | 类型 | 描述 |
|------|------|------|
| bookId | string | 书籍 ID |

### 主要组件
```jsx
function ChapterAnalysis() {
  // 章节列表（左侧）- 点击切换章节
  // 章节内容（中间）- 显示章节文本
  // 分析面板（右侧）- 显示 AI 分析结果
}
```

---

## 通用模式

### 数据获取
使用 TanStack Query：
```jsx
const { data, isLoading, error } = useQuery({
  queryKey: ['books', bookId],
  queryFn: () => api.getBook(bookId)
});
```

### 状态管理
使用 Zustand：
```jsx
import { useBookStore } from '../stores/bookStore';

const { currentBook, setCurrentBook } = useBookStore();
```

---

## 相关文件

- **路由配置**: `apps/web/src/App.jsx`
- **API 服务**: `apps/web/src/services/api.js`
- **状态管理**: `apps/web/src/stores/bookStore.js`
