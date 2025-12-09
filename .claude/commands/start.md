---
description: 恢复项目记忆，快速进入开发状态
argument-hint: [--full | --web | --api | --core]
allowed-tools: Read, Bash(date)
---

<task>
恢复 Book Insight 项目上下文，快速开始开发。
</task>

<workflow>

## Step 0: 获取当前时间

```bash
echo "当前时间: $(date +%Y-%m-%d) $(date +%H:%M) (第 $(date +%V) 周)"
```

## Step 1: 解析参数

| 参数 | 读取文档 | 场景 |
|------|----------|------|
| 无参数 | CONTEXT.md + CURRENT.md | 日常快速启动 |
| `--full` | + 全部开发文档 | 首次或长时间未开发 |
| `--web` | + pages.md + stores.md | 前端开发 |
| `--api` | + routers.md + ai-tasks.md | 后端开发 |
| `--core` | + ai-tasks.md | AI/RAG 核心开发 |

## Step 2: 读取核心文档（必读）

1. `docs/ai-context/CONTEXT.md`
2. `docs/ai-context/CURRENT.md`

## Step 3: 根据参数读取额外文档

### --full 模式
- `docs/development/api/routers.md`
- `docs/development/api/ai-tasks.md`
- `docs/development/web/pages.md`
- `docs/development/web/stores.md`

### --web 模式
- `docs/development/web/pages.md`
- `docs/development/web/stores.md`

### --api 模式
- `docs/development/api/routers.md`
- `docs/development/api/ai-tasks.md`

### --core 模式
- `docs/development/api/ai-tasks.md`

## Step 4: 输出验证

```
✅ 已恢复上下文

## 验证理解

1. **项目**: Book Insight - AI 书籍深度分析工具
2. **阶段**: [从 CONTEXT.md 获取]
3. **技术栈**: React 18 + FastAPI + 阿里云百炼(qwen-plus)
4. **下一步**: [从 CURRENT.md 获取 P0 任务]

## 读取的文档
- [x] CONTEXT.md
- [x] CURRENT.md
- [根据参数列出]

---
**当前阶段：[Phase X]，下一步：[任务]。**
**我们从哪里开始？**
```

</workflow>
