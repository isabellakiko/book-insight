# 前端 Hooks 文档

> 自定义 React Hooks 参考

**位置**: `apps/web/src/hooks/`
**最后更新**: 2025-12-12

---

## Hooks 概览

| Hook | 文件 | 描述 |
|------|------|------|
| useCharacterAnalysis | `useCharacterAnalysis.js` | 人物分析数据获取（SSE 流式 + 缓存加载） |

---

## useCharacterAnalysis

### 功能

用于加载人物分析数据的 Hook，支持两种模式：
- **缓存加载模式**（主要）：加载已分析的人物数据
- **SSE 流式模式**（脚本使用）：实时分析进度

> **重要**: 当前架构下，前端只使用 `loadCached` 方法加载已有数据，不触发实时 AI 分析。

### 参数

| 参数 | 类型 | 描述 |
|------|------|------|
| bookId | string | 书籍 ID |

### 返回值

```javascript
{
  // 状态
  status,        // 'idle' | 'searching' | 'analyzing' | 'completed' | 'error'
  searchResult,  // 搜索结果（章节列表、提及次数）
  appearances,   // 已分析的出场记录数组
  relations,     // 人物关系数组
  result,        // 完整分析结果（DetailedCharacter）
  error,         // 错误信息
  progress,      // 分析进度 (0-100)

  // 方法
  analyzeCharacter,  // (name: string) => void - 启动 SSE 流式分析
  loadCached,        // (name: string) => Promise<boolean> - 加载已分析的缓存
  cancel,            // () => void - 取消当前分析
  reset,             // () => void - 重置所有状态
}
```

### 状态说明

| 状态 | 含义 | 触发场景 |
|------|------|----------|
| `idle` | 空闲 | 初始状态、重置后 |
| `searching` | 搜索中 | 调用 `loadCached` 或 `analyzeCharacter` 后 |
| `analyzing` | 分析中 | SSE 流式分析进行中 |
| `completed` | 完成 | 数据加载/分析完成 |
| `error` | 错误 | 分析失败或中断 |

### 使用示例

#### 纯展示模式（推荐）

```jsx
import { useCharacterAnalysis } from '../hooks/useCharacterAnalysis'

function CharacterDetail({ bookId, characterName }) {
  const { status, result, error, loadCached } = useCharacterAnalysis(bookId)

  useEffect(() => {
    if (characterName && bookId) {
      // 只加载缓存，不触发分析
      loadCached(characterName)
    }
  }, [characterName, bookId, loadCached])

  if (status === 'searching') {
    return <div>加载中...</div>
  }

  if (status === 'completed' && !result) {
    return <div>暂无分析数据，请运行脚本分析</div>
  }

  if (error) {
    return <div>错误: {error}</div>
  }

  return (
    <div>
      <h1>{result.name}</h1>
      <p>{result.description}</p>
      {/* 渲染其他内容 */}
    </div>
  )
}
```

#### SSE 流式分析（脚本使用）

> 以下代码仅供参考，当前架构下前端不直接调用。

```jsx
function CharacterAnalyzer({ bookId }) {
  const {
    status,
    progress,
    appearances,
    relations,
    result,
    analyzeCharacter,
    cancel
  } = useCharacterAnalysis(bookId)

  const handleAnalyze = (name) => {
    analyzeCharacter(name)
  }

  return (
    <div>
      {status === 'analyzing' && (
        <div>
          <progress value={progress} max="100" />
          <span>{progress}%</span>
          <button onClick={cancel}>取消</button>
        </div>
      )}

      {status === 'completed' && result && (
        <div>分析完成: {result.name}</div>
      )}
    </div>
  )
}
```

### SSE 事件流（参考）

| 事件 | 数据 | 描述 |
|------|------|------|
| `search_complete` | `{ name, found_in_chapters, total_mentions }` | 搜索完成 |
| `chapter_analyzed` | `{ chapter_index, appearance }` | 单章分析完成 |
| `chapter_error` | `{ chapter_index, error }` | 单章分析失败 |
| `personality_analyzed` | `{ personality, role, description }` | 性格分析完成 |
| `relations_analyzed` | `{ relations }` | 关系分析完成 |
| `deep_profile_analyzed` | `{ summary, growth_arc, ... }` | 深度分析完成 |
| `completed` | `DetailedCharacter` | 全部完成 |

### 内部实现

```
loadCached(name)
    ↓
调用 analysisApi.getDetailedCharacter(bookId, name)
    ↓
检查 appearances 是否有数据
    ├── 有数据 → 设置 result, status='completed'
    └── 无数据 → 返回 false（需要分析）
```

### 与其他模块的协作

```
CharacterDetail 页面
├── useBookStore → currentBookId
└── useCharacterAnalysis(bookId)
    ├── loadCached(name) → 读取缓存 JSON
    └── result → 渲染人物档案
```

### 注意事项

1. **缓存优先**: 始终先尝试 `loadCached`，避免重复分析
2. **状态检查**: 使用 `status === 'completed' && !result` 判断无数据状态
3. **清理**: 组件卸载时 Hook 会自动清理 EventSource 连接
4. **进度计算**: `progress` 基于 `min(总章节数, 30)` 计算百分比

---

## 相关文件

- **Hook 实现**: `apps/web/src/hooks/useCharacterAnalysis.js`
- **API 服务**: `apps/web/src/services/api.js`
- **页面组件**: `apps/web/src/pages/CharacterDetail.jsx`
- **后端 SSE**: `apps/api/src/routers/analysis.py`
