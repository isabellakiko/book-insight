---
description: 每周文档优化，删除冗余，统计周报
argument-hint: [--push | --no-push]
allowed-tools: Read, Write, Edit, Bash(date, git, wc)
---

<task>
每周（建议周日）执行，优化文档，删除冗余内容，生成周报。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_WEEK_NUM=$(date +%V)

# 获取本周起止日期（macOS）
WEEK_START=$(date -v-$(( $(date +%u) - 1 ))d +%Y-%m-%d)
WEEK_END=$(date -v+$(( 7 - $(date +%u) ))d +%Y-%m-%d)

echo "第 $CURRENT_WEEK_NUM 周: $WEEK_START - $WEEK_END"
```

## Step 1: 审查 CURRENT.md

### 1.1 读取并分析

```bash
# 统计行数
wc -l docs/ai-context/CURRENT.md
```

### 1.2 识别冗余内容

检查以下冗余类型：
- **重复日志**：相同内容出现多次
- **过度详细**：包含完整代码片段、过长的描述
- **已完成任务**：仍在"本周任务"中但已标记 ✅ 的过期任务
- **过时信息**：不再相关的技术亮点或问题

### 1.3 优化 CURRENT.md

执行优化：
1. 删除重复内容
2. 压缩过度详细的日志（保留关键信息）
3. 清理已完成的任务
4. 更新"本周时间"为下周

## Step 2: 审查其他文档

### 2.1 检查 CONTEXT.md
- 检查"当前状态"是否准确
- 检查"下一步任务"是否需要更新

### 2.2 检查开发文档
- `docs/development/api/routers.md` - 是否与实际 API 同步
- `docs/development/web/pages.md` - 是否与实际页面同步

## Step 3: Token 优化报告

```bash
echo "=== Token 优化报告 ==="
echo "CURRENT.md: $(wc -l < docs/ai-context/CURRENT.md) 行"
echo "CONTEXT.md: $(wc -l < docs/ai-context/CONTEXT.md) 行"
```

## Step 4: 统计本周工作

```bash
# 统计本周 commits
git log --since="$WEEK_START" --until="$WEEK_END 23:59:59" --oneline | wc -l
```

汇总：
- 本周 commits 数
- 完成的功能/任务数
- 修复的 Bug 数

## Step 5: Git 操作

```bash
git add docs/
git commit -m "$(cat <<'EOF'
docs: 第 ${CURRENT_WEEK_NUM} 周优化

## 优化内容
- 清理 CURRENT.md 冗余内容
- 更新文档同步状态

## 本周统计
- Commits: [X] 次
- 完成功能: [X] 个

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

根据参数决定是否推送。

## Step 6: 输出周报

```
## 📊 第 ${CURRENT_WEEK_NUM} 周周报

**周期**: ${WEEK_START} - ${WEEK_END}

---

### 本周完成
- [功能 1]
- [功能 2]

### 本周统计
| 指标 | 数值 |
|------|------|
| Commits | X 次 |
| 新增功能 | X 个 |

### Token 优化
| 文档 | 行数 |
|------|------|
| CURRENT.md | X 行 |
| CONTEXT.md | X 行 |

### 下周计划
1. [任务 1]
2. [任务 2]

---
周报已生成，继续加油！💪
```

</workflow>
