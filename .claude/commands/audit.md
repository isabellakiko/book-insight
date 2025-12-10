---
description: 项目健康检查，代码质量、依赖、文档同步
argument-hint: [--quick | --full | --security | --docs]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

<task>
执行 Book Insight 项目健康检查，检查代码质量、依赖状态、文档同步情况。
</task>

<workflow>

## Step 0: 获取基本信息

```bash
echo "审计时间: $(date +%Y-%m-%d) $(date +%H:%M)"
echo "=== 最近提交 ==="
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
| `--code-sync` | 文档与代码同步检查 | 重构后 |

## Step 2: 项目结构统计

```bash
echo "=== 代码统计 ==="
echo "后端 Python: $(find apps/api/src -name '*.py' | wc -l) 个文件"
echo "前端 JSX: $(find apps/web/src -name '*.jsx' -o -name '*.js' | wc -l) 个文件"
echo "文档: $(find docs -name '*.md' | wc -l) 个文件"
```

## Step 3: 代码质量检查

### 3.1 TODO/FIXME
```bash
echo "=== TODO/FIXME ==="
grep -rn "TODO\|FIXME" apps/ --include="*.py" --include="*.js" --include="*.jsx" 2>/dev/null | head -10
```

### 3.2 console.log 残留
```bash
echo "=== console.log ==="
grep -rn "console.log" apps/web/src --include="*.js" --include="*.jsx" 2>/dev/null | wc -l
```

### 3.3 构建检查（--full 模式）
```bash
cd apps/web && pnpm build
cd apps/api && .venv/bin/python -m py_compile src/main.py
```

## Step 4: 依赖健康检查

### 4.1 前端
```bash
cd apps/web && pnpm outdated 2>/dev/null | head -10 || echo "无过时依赖"
```

### 4.2 后端
```bash
cd apps/api && .venv/bin/pip list --outdated 2>/dev/null | head -5 || echo "无过时依赖"
```

### 4.3 安全漏洞（--security 模式）
```bash
cd apps/web && pnpm audit 2>/dev/null || echo "检查完成"
```

## Step 5: 文档同步审计

### 5.1 文件数量对比
```bash
echo "=== 文件对比 ==="
echo "页面: $(ls apps/web/src/pages/*.jsx 2>/dev/null | wc -l) 个"
echo "路由: $(ls apps/api/src/routers/*.py 2>/dev/null | grep -v __init__ | wc -l) 个"
```

### 5.2 检查内容
- CONTEXT.md 项目阶段 vs 实际进度
- routers.md vs 实际 API 端点
- pages.md vs 实际页面组件

## Step 5.5: 代码同步检查（--code-sync 模式）

### 检查 routers.md vs 实际端点
```bash
echo "=== API 端点同步检查 ==="
echo "文档中的端点："
grep -E "^### (GET|POST|DELETE|PUT)" docs/development/api/routers.md | wc -l
echo "代码中的端点："
grep -E "@router\.(get|post|delete|put)" apps/api/src/routers/*.py | wc -l
```

### 检查 pages.md vs 实际页面
```bash
echo "=== 页面组件同步检查 ==="
echo "实际页面文件："
ls apps/web/src/pages/*.jsx 2>/dev/null | wc -l
```

### 检查 stores.md vs 实际 stores
```bash
echo "=== Store 同步检查 ==="
echo "实际 store 文件："
ls apps/web/src/stores/*.js 2>/dev/null | wc -l
```

### 检查 hooks 同步
```bash
echo "=== Hooks 同步检查 ==="
echo "实际 hook 文件："
ls apps/web/src/hooks/*.js 2>/dev/null | wc -l
```

## Step 6: 生成报告

```
# 📋 Book Insight 审计报告

**时间**: [日期时间]
**模式**: [quick/标准/full/security/docs]

---

## 📊 总览

| 维度 | 状态 | 详情 |
|------|------|------|
| 代码质量 | ✅/⚠️/❌ | TODO: X, console.log: X |
| 依赖健康 | ✅/⚠️/❌ | 过时: X |
| 文档同步 | ✅/⚠️/❌ | 问题: X 处 |

## 🔴 需要立即处理
[列出严重问题]

## 🟡 建议优化
[列出建议]

## 🎯 行动建议
1. [建议 1]
2. [建议 2]
```

## Step 7: 执行优化（需确认）

如果发现问题，询问用户是否执行修复：
- 更新过时文档
- 清理 console.log
- 更新文档日期

</workflow>
