# 人物分析指南

> 人物按需分析系统使用指南

**位置**: `scripts/analyze.py`
**后端**: `apps/api/src/routers/analysis.py`
**最后更新**: 2025-12-11

---

## 分析模式

| 模式 | 命令 | 场景 |
|------|------|------|
| 初始分析 | `analyze.py 赵秦` | 首次分析，智能采样 30 章 |
| 增量分析 | `--continue` | 交互式询问章节数 |
| 增量分析(指定) | `--continue --chapters 50` | 分析 50 章 |
| 增量+刷新 | `--continue --chapters 50 --refresh-summary` | 分析后刷新总结 |
| 仅刷新总结 | `--refresh-summary-only` | 不分析新章节，只更新总结 |
| 查看状态 | `--status` | 显示分析进度 |

---

## 快速开始

### 1. 查看人物状态

```bash
python scripts/analyze.py 赵秦 --status
```

输出示例：
```
============================================================
  人物状态: 赵秦
============================================================

出现章节: 1112 章
首次出场: 第 169 章
最后出场: 第 8095 章

分析状态: 已分析 30/1112 章 (2.7%)

简介: 赵秦是一位退役特种兵，性格沉稳...
角色: protagonist
性格: 冷静、机智、重情义、果断、坚韧
成长轨迹: 从军队退役后...

可用命令:
  python scripts/analyze.py 赵秦 --continue           # 继续分析（交互式）
  python scripts/analyze.py 赵秦 --refresh-summary-only  # 仅刷新总结
```

### 2. 增量分析（交互式）

```bash
python scripts/analyze.py 赵秦 --continue
```

脚本会询问：
```
当前状态: 已分析 30/1112 章 (2.7%)
剩余未分析: 1082 章

本次分析多少章？ [默认 50]:
```

分析完成后会询问：
```
当前进度: 80/1112 章 (7.2%)

是否刷新总结字段（基于已分析的章节重新生成）？ [y/N]:
```

### 3. 非交互式分析

```bash
# 分析 100 章，不刷新总结
python scripts/analyze.py 赵秦 --continue --chapters 100 --no-interactive

# 分析 50 章并刷新总结
python scripts/analyze.py 赵秦 --continue --chapters 50 --refresh-summary
```

---

## 第一人称视角处理

> 小说以张成第一人称叙述，AI 分析需区分主观描述与客观行为

### FIRST_PERSON_CONTEXT

所有分析 Prompt 都包含以下上下文：

```
本小说以第一人称（我/张成）视角叙述。分析时请注意：
1. 区分客观行为描述与主观推测
2. 标注叙述者偏见（narrator_bias）
3. 优先采信对话内容和明确行为
4. 对"我认为"、"看起来"等主观表述保持谨慎
```

### 相关字段

| 字段 | 模型 | 用途 |
|------|------|------|
| `narrator_bias` | CharacterAppearance | 叙述者态度：positive/neutral/negative/unclear |
| `objective_basis` | CharacterRelation | 关系判断的客观依据 |
| `confidence` | CharacterRelation | 判断可信度：high/medium/low |
| `analysis_limitations` | DetailedCharacter | 分析局限性说明 |

---

## 数据结构

### profile.json 关键字段

```json
{
  "name": "赵秦",
  "total_chapters": 1112,            // 总出场章节数
  "total_analyzed_chapters": 80,     // 已分析数量
  "analyzed_chapters": [168, 288, 374, ...],  // 已分析章节列表
  "analysis_status": "completed",

  // 章节分析数据（增量追加）
  "appearances": [
    {
      "chapter_index": 168,
      "chapter_title": "第168章 初次登场",
      "events": ["..."],
      "interactions": ["..."],
      "quote": "..."
    }
  ],

  // 总结字段（手动刷新）
  "summary": "一句话概括",
  "growth_arc": "成长轨迹描述",
  "core_traits": [...],
  "relations": [...],
  "strengths": [...],
  "weaknesses": [...],
  "notable_quotes": [...]
}
```

### 增量分析流程

```
1. 读取 profile.json
   ↓
2. 获取 analyzed_chapters，排除已分析的
   ↓
3. 分析新章节，追加到 appearances
   ↓
4. 更新 analyzed_chapters、total_analyzed_chapters
   ↓
5. 【可选】用户确认后刷新总结字段
   ↓
6. 保存 profile.json
```

---

## 总结刷新策略

**策略 B（当前实现）**: 手动刷新

- 每次增量只追加 `appearances`，不自动更新总结
- 分析完成后**询问**用户是否刷新
- 用户可以手动执行 `--refresh-summary-only`

**优点**:
- 节省 API 调用成本
- 用户可以累积多次增量后一次性刷新
- 避免小样本产生不准确的总结

---

## 最佳实践

### 1. 分析计划

```bash
# 第一周：智能采样 30 章（初始分析）
python scripts/analyze.py 赵秦

# 之后每周：增量 50 章
python scripts/analyze.py 赵秦 --continue --chapters 50

# 每增量 100+ 章后：刷新总结
python scripts/analyze.py 赵秦 --refresh-summary-only
```

### 2. 成本控制

| 操作 | API 调用次数 | 建议频率 |
|------|-------------|----------|
| 分析 1 章 | 1 次 | - |
| 刷新总结 | 3-4 次 | 每 100 章 1 次 |
| 增量 50 章 + 刷新 | ~54 次 | 每周 1 次 |

### 3. 多人物分析

```bash
# 批量分析（依次执行）
python scripts/analyze.py 张成 赵琳 夏诗

# 查看所有状态
python scripts/analyze.py 张成 赵秦 夏诗 --status
```

---

## API 端点

### 增量分析（SSE）

```
GET /api/analysis/{book_id}/characters/continue
```

参数：
- `name`: 人物名称
- `additional_chapters`: 分析章节数（默认 30）
- `refresh_summary`: 是否刷新总结（默认 false）

SSE 事件：
- `search_complete`: 搜索完成
- `continue_info`: 增量信息
- `chapter_analyzed`: 单章分析完成
- `summary_skipped`: 跳过总结刷新
- `relations_analyzed`: 关系分析完成
- `personality_analyzed`: 性格分析完成
- `deep_profile_analyzed`: 深度分析完成
- `completed`: 全部完成

---

## 常见问题

### Q: 为什么不自动刷新总结？

A: 刷新总结需要调用 AI 3-4 次，如果每次增量都刷新：
- 10 次增量 × 4 次 AI = 40 次额外调用
- 建议累积 100 章后一次性刷新，降低成本

### Q: 如何知道该刷新总结了？

A: 脚本会在分析完成后询问。一般建议：
- 覆盖率超过 10% 时刷新一次
- 每增量 100 章后刷新一次
- 分析完成（100%）后刷新一次

### Q: 交互式询问太烦？

A: 使用 `--no-interactive` 禁用交互：
```bash
python scripts/analyze.py 赵秦 --continue --chapters 50 --no-interactive
```

---

## 相关文件

- **脚本**: `scripts/analyze.py`
- **API 客户端**: `scripts/lib/api_client.py`
- **后端路由**: `apps/api/src/routers/analysis.py`
- **分析器**: `apps/api/src/ai/tasks/character_analyzer.py`
- **数据存储**: `data/analysis/{book_id}/characters/{name}/profile.json`
