---
description: 每月归档 CURRENT.md，创建新月份模板
argument-hint: [--push | --no-push]
allowed-tools: Read, Write, Edit, Bash(date, git, cp, wc)
---

<task>
每月初执行，归档上月 CURRENT.md，创建新月份模板，全面审查文档。
</task>

<workflow>

## Step 0: 获取当前时间（必须）

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)
CURRENT_MONTH=$(date +%Y-%m)
CURRENT_WEEK_NUM=$(date +%V)

# 获取上月信息（用于归档命名）- macOS
LAST_MONTH=$(date -v-1m +%Y-%m)

echo "当前月份: $CURRENT_MONTH"
echo "归档月份: $LAST_MONTH"
```

## Step 1: 归档 CURRENT.md

### 1.1 复制到归档目录

```bash
# 创建归档目录（如果不存在）
mkdir -p docs/ai-context/archive

# 复制当前 CURRENT.md 到归档
cp docs/ai-context/CURRENT.md "docs/ai-context/archive/${LAST_MONTH}.md"

echo "已归档到: docs/ai-context/archive/${LAST_MONTH}.md"
```

### 1.2 创建新月份 CURRENT.md

创建新的 CURRENT.md 模板，包含：
- 新的周时间范围
- 清空的 Day-by-Day 日志
- 迁移未完成的任务

## Step 2: 更新 CONTEXT.md

### 2.1 更新项目阶段
如果上月完成了某个 Phase，更新阶段信息。

### 2.2 更新下月任务
从"优先级 2"提升到"优先级 1"

## Step 3: 审查所有文档

### 3.1 文档清单检查

检查以下文档是否存在且有效：
- [ ] docs/ai-context/CONTEXT.md
- [ ] docs/ai-context/CURRENT.md
- [ ] docs/development/api/routers.md
- [ ] docs/development/api/ai-tasks.md
- [ ] docs/development/web/pages.md
- [ ] docs/development/web/stores.md

### 3.2 版本检查

对比文档与实际代码：
- package.json 依赖版本
- pyproject.toml 依赖版本

## Step 4: Token 成本总报告

```bash
echo "=== 月度 Token 报告 ==="
echo "CONTEXT.md: $(wc -l < docs/ai-context/CONTEXT.md) 行"
echo "CURRENT.md: $(wc -l < docs/ai-context/CURRENT.md) 行"
echo "归档文件数: $(ls docs/ai-context/archive/*.md 2>/dev/null | wc -l)"
```

## Step 5: Git 操作

```bash
git add docs/
git commit -m "$(cat <<'EOF'
docs: ${CURRENT_MONTH} 月度归档

## 归档内容
- 归档 ${LAST_MONTH} 月 CURRENT.md
- 创建 ${CURRENT_MONTH} 月新模板
- 更新 CONTEXT.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

根据参数决定是否推送（推荐 `--push`）。

## Step 6: 输出月报

```
## 📅 ${CURRENT_MONTH} 月度归档完成

**归档时间**: ${CURRENT_DATE} ${CURRENT_TIME}

---

### 归档操作
- [x] ${LAST_MONTH} 月 CURRENT.md → archive/${LAST_MONTH}.md
- [x] 创建 ${CURRENT_MONTH} 月新 CURRENT.md
- [x] 更新 CONTEXT.md

### 文档健康状态
| 检查项 | 状态 |
|--------|------|
| 核心文档完整性 | ✅ |
| 版本一致性 | ✅ / ⚠️ 需更新 |

### Token 统计
| 文档 | 行数 |
|------|------|
| CONTEXT.md | X 行 |
| CURRENT.md | X 行 |

### archive 状态
- 归档文件数: X 个

### 下月重点
1. [任务 1]
2. [任务 2]

---
新的一月，新的开始！🚀
```

</workflow>
