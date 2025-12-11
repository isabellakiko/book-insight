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
| `--web` | + pages.md + stores.md + hooks.md | 前端开发 |
| `--api` | + routers.md + ai-tasks.md | 后端开发 |
| `--core` | + ai-tasks.md + character-analysis.md | AI/RAG 核心开发 |

## Step 2: 读取核心文档（必读）

按顺序读取以下文档：

1. `docs/ai-context/CONTEXT.md` - 项目全局上下文
2. `docs/ai-context/CURRENT.md` - 当前开发进度和待办

## Step 3: 根据参数读取额外文档

### --full 模式（完整上下文）
- `docs/development/ARCHITECTURE.md` - 系统架构
- `docs/development/api/routers.md` - API 端点
- `docs/development/api/ai-tasks.md` - AI 任务模块
- `docs/development/api/models.md` - 数据模型
- `docs/development/web/pages.md` - 页面组件
- `docs/development/web/stores.md` - 状态管理
- `docs/development/web/hooks.md` - 自定义 Hooks

### --web 模式（前端开发）
- `docs/development/web/pages.md` - 页面组件
- `docs/development/web/stores.md` - 状态管理
- `docs/development/web/hooks.md` - 自定义 Hooks

### --api 模式（后端开发）
- `docs/development/api/routers.md` - API 端点
- `docs/development/api/ai-tasks.md` - AI 任务模块
- `docs/development/api/models.md` - 数据模型

### --core 模式（AI 核心开发）
- `docs/development/api/ai-tasks.md` - AI 任务模块
- `docs/development/api/character-analysis.md` - 人物分析详细文档

## Step 4: 验证理解并输出

读取文档后，输出以下格式确认理解：

```
✅ 已恢复上下文

## 项目概览

1. **项目**: Book Insight - AI 书籍深度分析工具
2. **阶段**: [从 CURRENT.md 提取当前阶段]
3. **技术栈**: React 18 + FastAPI + 阿里云百炼(qwen-plus)

## 架构概览

- **前端**: Zustand(UI状态) + TanStack Query(服务器状态)
- **后端**: Books/Analysis/RAG 三模块
- **数据**: JSON 文件 + ChromaDB 向量库
- **分析模式**: 脚本分析 → JSON 存储 → 前端展示

## 待办优先级

- **P0**: [从 CURRENT.md 提取]
- **P1**: [从 CURRENT.md 提取]

## 读取的文档

- [x] CONTEXT.md (~2500 tokens)
- [x] CURRENT.md (~2400 tokens)
- [根据参数列出额外读取的文档]

## 开发建议

根据任务类型选择合适的模式：

| 任务类型 | 推荐操作 |
|----------|----------|
| 探索代码库 | 直接提问，我会使用 Glob/Grep/Read |
| 规划新功能 | 描述需求后说"请先规划方案" |
| 修复 Bug | 描述现象，我会逐步定位 |
| 代码重构 | 说明目标，我会分步执行 |

---
**当前阶段：[Phase X]，下一步：[任务]。**
**准备好了！从哪里开始？**
```

## Step 5: Claude Code 高级模式指南

根据任务复杂度选择合适的模式：

### 探索模式 (Explore Mode)
适用于理解代码库时，直接提问：
- "帮我理解 RAG 模块的实现"
- "查找所有使用 SSE 的地方"
- "这个 Hook 是怎么工作的"

### 规划模式 (Plan Mode)
适用于实现新功能前：
- 按 `Shift+Tab` 两次进入 Plan Mode
- 适合场景：新功能、重构、架构变更
- 产出详细实施计划后再执行

### 思考深度选择

| 任务类型 | 推荐指令 | 示例 |
|----------|----------|------|
| 简单问题 | think | 变量重命名、简单 bug |
| 中等复杂 | megathink | 单文件重构、功能增强 |
| 复杂任务 | ultrathink | 跨模块设计、架构决策 |

### 任务追踪
对于复杂任务（3 步以上），Claude 会自动使用 TodoWrite 追踪进度。

## Step 6: 常用命令提醒

| 命令 | 用途 | 使用时机 |
|------|------|----------|
| `/checkpoint` | 保存进度 | 完成一个功能后 |
| `/end` | 结束开发 | 每天结束时 |
| `/audit` | 健康检查 | 每周或重大改动后 |

</workflow>
