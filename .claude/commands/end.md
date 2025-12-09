---
description: 每日开发结束，完整更新文档并提交
argument-hint: [--push | --no-push]
allowed-tools: Read, Write, Edit, Bash(date, git)
---

<task>
每日开发结束时，完整总结工作，更新文档，创建 commit 并可选推送。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)

echo "当前时间: $CURRENT_DATE $CURRENT_TIME"
```

## Step 1: 总结本次会话

完整总结今天的工作：

1. **所有完成的工作**：列出今天完成的所有功能/任务
2. **遇到的问题和解决方案**：记录所有问题
3. **未完成的工作**：记录未完成的内容
4. **下次会话建议**：建议下次从哪里开始

## Step 2: 更新文档（完整更新）

### 2.1 更新 CURRENT.md

如果今天已经执行过 `/checkpoint`，补充完善内容。
如果没有执行过，创建完整的 Day X 条目。

更新内容：
- Day X 日志（完整版）
- 本周任务状态（标记完成的任务）
- 技术亮点（如果有新的）
- 问题与解决方案（如果有新的）

### 2.2 检查是否需要更新 CONTEXT.md

如果今天有重大变化（如完成了一个 Phase、技术栈变更等）：
- 更新 CONTEXT.md 的"当前开发状态"
- 更新"下一步任务"

## Step 3: Git 操作

### 3.1 检查变更
```bash
git status --short
git diff --stat
```

### 3.2 创建 commit

```bash
# 添加所有变更
git add .

# 创建 commit
git commit -m "$(cat <<'EOF'
docs: 每日总结 ${CURRENT_DATE}

## 今日完成
- [工作内容 1]
- [工作内容 2]

## 下次继续
- [待续任务]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### 3.3 推送处理

根据参数：
- `--push`：自动推送 `git push`
- `--no-push`：不推送
- 无参数：询问用户是否需要推送

## Step 4: 输出完成报告

```
## ✅ 每日总结完成

**日期**: ${CURRENT_DATE} ${CURRENT_TIME}

### 今日完成
- [工作内容 1]
- [工作内容 2]

### 遇到的问题
- [问题 1]: [解决方案]

### 更新的文档
- [x] CURRENT.md
- [其他更新的文档]

### Git 状态
- [x] Commit 已创建
- [ ] 已推送 / 未推送

### 下次会话建议
1. 执行 `/start` 恢复上下文
2. 继续 [任务名称]

---
辛苦了！明天见 👋
```

</workflow>
