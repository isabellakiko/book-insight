# 前端页面文档

> React 页面组件参考

**位置**: `apps/web/src/pages/`
**框架**: React 18 + Vite
**最后更新**: 2025-12-12

---

## 页面概览

| 页面 | 文件 | 路由 | 描述 |
|------|------|------|------|
| Dashboard | `Dashboard.jsx` | `/` | 首页，书籍管理 |
| RAG Chat | `RAGChat.jsx` | `/chat` | 智能问答 |
| Characters | `Characters.jsx` | `/characters` | 人物列表 |
| Character Detail V4 | `CharacterDetailV4.jsx` | `/characters/:name` | 人物详情（左侧目录+右侧内容） |
| Timeline | `Timeline.jsx` | `/timeline` | 情节时间线 |
| Chapter Analysis | `ChapterAnalysis.jsx` | `/chapters/:bookId` | 章节分析 |

> **注**: `CharacterDetail.jsx` 为旧版本，保留作为参考。当前使用 V4 版本。

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
使用 `useNavigate()` 在当前页面导航到人物详情：
```javascript
const navigate = useNavigate()
navigate(`/characters/${encodeURIComponent(name)}`)
```

---

## CharacterDetail V4（人物详情）

> **文件**: `CharacterDetailV4.jsx`（当前版本），`CharacterDetail.jsx`（旧版，备份参考）

### V4 版本特点

**布局重构**：左侧目录 + 右侧内容 Tab 切换
```
┌──────────────────┬──────────────────────────────────┐
│  左侧边栏 280px  │       右侧内容区 (flex:1)         │
│  ┌────────────┐  │  ┌────────────────────────────┐  │
│  │ 返回按钮   │  │  │ 6 个内容区块（Tab 切换）    │  │
│  │ 人物头像   │  │  │ 概览/成长/性格/关系/足迹    │  │
│  │ 快捷统计   │  │  │ /关联人物                  │  │
│  │ 目录导航   │  │  │                            │  │
│  │ 书籍信息   │  │  │ 点击目录切换内容           │  │
│  └────────────┘  │  └────────────────────────────┘  │
└──────────────────┴──────────────────────────────────┘
```

### 6 大内容区块

| 区块 | 组件 | 数据字段 |
|------|------|---------|
| 概览 | `OverviewSection` | summary, description, personality, notable_quotes |
| 成长轨迹 | `GrowthSection` | growth_arc, growth_phases |
| 性格分析 | `PersonalitySection` | core_traits, strengths, weaknesses |
| 人物关系 | `RelationsSection` | relations（9种类型） |
| 章节足迹 | `ChaptersSection` | appearances（可展开详情） |
| 关联人物 | `ConnectionsSection` | discovered_characters |

### 关系类型

支持 9 种关系类型，每种有专属图标和颜色：

| 类型 | 标签 | 图标 | 颜色 |
|------|------|------|------|
| lover | 恋人 | Heart | rose |
| family | 亲人 | Users | amber |
| friend | 挚友 | Users | emerald |
| rival | 对手 | Swords | orange |
| enemy | 敌人 | Swords | red |
| mentor | 导师 | GraduationCap | blue |
| student | 学生 | GraduationCap | cyan |
| partner | 伙伴 | Handshake | indigo |
| complex | 复杂 | Users | purple |

### 数据来源

**纯展示模式**：只读取已有分析数据，不触发实时 AI 分析

存储路径：
```
data/analysis/{book_id}/characters/{人物名}/profile.json
```

**分析脚本**（统一 CLI）：
```bash
python scripts/analyze.py 赵秦              # 智能采样分析
python scripts/analyze.py 赵秦 --continue   # 增量分析
python scripts/analyze.py 赵秦 --status     # 查看状态
```

### CSS 样式

- 样式前缀：`cv4-*`（约 770 行）
- 位置：`apps/web/src/index.css`
- 响应式：桌面双栏，移动端单栏

### 依赖

- `useBookStore` - 获取 `currentBookId`
- `useThemeStore` - 主题切换
- `@tanstack/react-query` - 数据获取

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
