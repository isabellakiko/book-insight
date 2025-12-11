# 前端页面文档

> React 页面组件参考

**位置**: `apps/web/src/pages/`
**框架**: React 18 + Vite
**最后更新**: 2025-12-11

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
- **纯展示模式**：只读取已有分析数据，不触发实时 AI 分析
- 展示人物完整档案：
  - 基础信息（名字、别名、首次出场、出场章数、覆盖率）
  - 人物概述（Summary）
  - 成长轨迹（Growth Arc）
  - 性格剖析（Core Traits - 带证据）
  - 优点 / 缺点
  - 经典语录
  - 人物关系（9种类型：friend/enemy/lover/family/mentor/student/rival/partner/complex）
  - 关联人物（discovered_characters - 分析过程中发现的相关人物）
  - 章节出现（可展开查看：事件、结构化互动、台词、关键时刻、情感状态）
- 无数据时显示"暂无分析数据"提示
- 浮动关闭按钮

### 数据来源
分析数据通过脚本离线生成，存储在：
```
data/analysis/{book_id}/characters/{人物名}/profile.json
```

**分析脚本**（统一 CLI）：
```bash
python scripts/analyze.py 赵秦              # 智能采样分析
python scripts/analyze.py 赵秦 --continue   # 增量分析
python scripts/analyze.py 赵秦 --status     # 查看状态
```

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
- `useCharacterAnalysis` - 人物分析 Hook（只使用 `loadCached`）

### 主要组件
```jsx
function CharacterDetail() {
  // Loading 状态 - 加载缓存数据
  // NoData 状态 - 暂无分析数据（提示运行脚本）
  // Error 状态 - 加载失败提示
  // Result 状态 - 完整人物档案展示
}

function SectionHeader({ number, title, subtitle }) {
  // 编号式标题组件（01 成长轨迹 Growth Arc）
}
```

---

## useCharacterAnalysis Hook

**位置**: `apps/web/src/hooks/useCharacterAnalysis.js`

用于加载人物分析数据的 Hook。

> **重要**: 当前架构下，前端只使用 `loadCached` 方法加载已有数据，不触发实时 AI 分析。

### 状态

| 状态 | 类型 | 描述 |
|------|------|------|
| status | string | 状态：idle/searching/completed/error |
| result | object | 分析结果（完整人物档案） |
| appearances | array | 章节出场详情数组 |
| relations | array | 人物关系数组 |
| error | string | 错误信息 |

### 方法

| 方法 | 参数 | 描述 | 当前使用 |
|------|------|------|----------|
| loadCached | name: string | 加载已缓存的分析结果 | ✅ 主要使用 |
| analyzeCharacter | name: string | 触发 SSE 流式分析 | ❌ 前端不调用 |
| cancel | - | 取消当前分析 | - |
| reset | - | 重置所有状态 | - |

### 使用示例（纯展示模式）

```jsx
import { useCharacterAnalysis } from '../hooks/useCharacterAnalysis'

function CharacterDetail({ bookId, name }) {
  const { status, result, error, loadCached } = useCharacterAnalysis(bookId)

  useEffect(() => {
    if (name && bookId) {
      // 只加载缓存，不触发分析
      loadCached(name)
    }
  }, [name, bookId, loadCached])

  if (status === 'completed' && !result && !error) {
    return <div>暂无分析数据，请运行脚本分析</div>
  }
  // ...
}
```

### SSE 流式分析（脚本使用）

> 以下 SSE 事件由分析脚本通过 API 触发，前端不直接使用。

| 事件 | 数据 | 描述 |
|------|------|------|
| search_complete | { name, found_in_chapters, total_mentions } | 搜索完成 |
| chapter_analyzed | { chapter_index, appearance } | 单章分析完成 |
| relations_analyzed | { relations } | 关系分析完成 |
| completed | { profile, appearances, relations } | 全部完成 |

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
- **自定义 Hooks**: [hooks.md](./hooks.md)
