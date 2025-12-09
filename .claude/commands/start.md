---
description: 恢复项目记忆，快速进入开发状态
argument-hint: [--full | --web | --api | --core]
allowed-tools: Read, Bash(date)
---

<task>
恢复项目上下文，让 AI 快速理解 Book Insight 项目状态，准备开始开发。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

运行以下命令获取时间信息：

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_WEEK_NUM=$(date +%V)
echo "当前时间: $CURRENT_DATE $CURRENT_TIME (第 $CURRENT_WEEK_NUM 周)"
```

## Step 1: 解析参数

根据用户输入的参数确定读取范围：

| 参数 | 读取文档 | 场景 |
|------|----------|------|
| 无参数 | CONTEXT.md + CURRENT.md | 日常快速启动 |
| `--full` | 全部核心文档 | 首次使用或长时间未开发 |
| `--web` | + pages.md + stores.md | 前端开发场景 |
| `--api` | + routers.md + ai-tasks.md | 后端开发场景 |
| `--core` | + ai-tasks.md | AI/RAG 核心开发 |

## Step 2: 读取核心文档（必读）

**必读文档**（所有模式）：
1. `docs/ai-context/CONTEXT.md` - 项目快照
2. `docs/ai-context/CURRENT.md` - 当前进度

## Step 3: 根据参数读取额外文档

### --full 模式（完整启动）
额外读取：
- `docs/development/api/routers.md` - API 路由
- `docs/development/api/ai-tasks.md` - AI 任务
- `docs/development/web/pages.md` - 页面组件
- `docs/development/web/stores.md` - 状态管理

### --web 模式（前端开发）
额外读取：
- `docs/development/web/pages.md`
- `docs/development/web/stores.md`

### --api 模式（后端开发）
额外读取：
- `docs/development/api/routers.md`
- `docs/development/api/ai-tasks.md`

### --core 模式（AI 核心开发）
额外读取：
- `docs/development/api/ai-tasks.md`

## Step 4: 验证理解并输出

输出格式：

```
✅ 已恢复上下文

## 验证理解

1. **项目类型**: AI 驱动的书籍深度分析工具
2. **当前阶段**: [从 CONTEXT.md 获取]
3. **技术栈**: React 18 + FastAPI + ChromaDB + Claude API
4. **下一步任务**: [从 CURRENT.md 获取 P0 任务]

## 本次读取的文档
- [x] CONTEXT.md
- [x] CURRENT.md
- [根据参数列出其他文档]

---

**已恢复上下文。当前阶段：[Phase X]，下一步：[任务]。**
**我们从哪里开始？**
```

</workflow>
