---
description: 项目健康检查，代码质量、依赖、文档同步
argument-hint: [--quick | --full | --security | --docs]
allowed-tools: Read, Write, Edit, Bash(date, git, find, wc, pnpm, pip), Glob, Grep
---

<task>
执行项目健康检查，检查代码质量、依赖状态、文档同步情况。
</task>

<workflow>

## Step 0: 获取基本信息

```bash
CURRENT_DATE=$(date +%Y-%m-%d)
CURRENT_TIME=$(date +%H:%M)

echo "审计时间: $CURRENT_DATE $CURRENT_TIME"

# 最近提交
git log -3 --oneline
```

## Step 1: 解析参数

| 参数 | 审计范围 | 场景 |
|------|----------|------|
| `--quick` | Git 状态 + 文档日期 | 每天/提交前 |
| 无参数 | 标准检查 | 每周常规 |
| `--full` | 完整检查（含构建） | 大版本后 |
| `--security` | 安全扫描 | 上线前 |
| `--docs` | 深度文档审计 | Phase 完成后 |

## Step 2: 项目结构探索

### 2.1 代码统计

```bash
echo "=== 后端代码 ==="
find apps/api/src -name "*.py" -not -path "*/.venv/*" | wc -l
echo "Python 文件数"

echo "=== 前端代码 ==="
find apps/web/src -name "*.jsx" -o -name "*.js" | wc -l
echo "JS/JSX 文件数"
```

### 2.2 文档统计

```bash
find docs -name "*.md" | wc -l
echo "文档文件数"
```

## Step 3: 代码质量检查

### 3.1 TODO/FIXME 统计

```bash
echo "=== TODO/FIXME ==="
grep -rn "TODO\|FIXME" apps/ --include="*.py" --include="*.js" --include="*.jsx" 2>/dev/null | head -20
```

### 3.2 console.log 残留（前端）

```bash
echo "=== console.log 残留 ==="
grep -rn "console.log" apps/web/src --include="*.js" --include="*.jsx" 2>/dev/null | head -10
```

### 3.3 构建检查（--full 模式）

```bash
# 前端构建
cd apps/web && pnpm build

# 后端语法检查（Python）
cd apps/api && .venv/bin/python -m py_compile src/main.py
```

## Step 4: 依赖健康检查

### 4.1 前端依赖

```bash
cd apps/web && pnpm outdated 2>/dev/null || echo "检查完成"
```

### 4.2 后端依赖

```bash
cd apps/api && .venv/bin/pip list --outdated 2>/dev/null | head -10
```

### 4.3 安全漏洞（--security 模式）

```bash
# 前端
cd apps/web && pnpm audit 2>/dev/null || echo "检查完成"
```

## Step 5: 文档同步审计

### 5.1 过时内容检测

对比以下内容：
- CONTEXT.md 项目阶段 vs 实际进度
- API 文档 vs 实际路由
- 页面文档 vs 实际页面

### 5.2 文件数量对比

```bash
echo "=== 实际 vs 文档 ==="
echo "实际页面数: $(ls apps/web/src/pages/*.jsx | wc -l)"
echo "实际路由数: $(ls apps/api/src/routers/*.py | grep -v __init__ | wc -l)"
```

### 5.3 日期检查

检查文档最后更新日期是否过旧（>7天警告）

## Step 6: 生成审计报告

```
# 📋 项目审计报告

**审计时间**: ${CURRENT_DATE} ${CURRENT_TIME}
**审计模式**: [quick/标准/full/security/docs]

---

## 📊 总览

| 维度 | 状态 | 详情 |
|------|------|------|
| 代码质量 | ✅/⚠️/❌ | TODO: X, console.log: X |
| 依赖健康 | ✅/⚠️/❌ | 过时: X, 漏洞: X |
| 文档同步 | ✅/⚠️/❌ | 过时: X 处 |

---

## 🔴 需要立即处理

| 问题 | 位置 | 建议 |
|------|------|------|
| ... | ... | ... |

## 🟡 建议优化

| 问题 | 位置 | 优先级 |
|------|------|--------|
| ... | ... | ... |

## 🎯 行动建议

1. [建议 1]
2. [建议 2]
```

## Step 7: 执行优化（需确认）

如果发现问题，询问用户是否执行修复：
- 更新过时的文档
- 清理无用的 console.log
- 更新文档日期

</workflow>
