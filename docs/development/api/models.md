# 数据模型文档

> Pydantic 模型定义参考

**位置**: `apps/api/src/knowledge/models.py`
**最后更新**: 2025-12-09

---

## 模型概览

| 模型 | 用途 | 存储位置 |
|------|------|----------|
| Chapter | 章节结构 | 内存（解析时使用） |
| ChapterAnalysis | 章节分析结果 | `analysis/{book_id}/chapters/` |
| Character | 人物简要信息 | `analysis/{book_id}/characters.json` |
| DetailedCharacter | 人物详细分析 | `analysis/{book_id}/characters/{name}/` |
| CharacterAppearance | 人物章节出现 | 嵌套在 DetailedCharacter |
| CharacterRelation | 人物关系 | 嵌套在 DetailedCharacter |
| CharacterSearchResult | 人物搜索结果 | API 响应（不存储） |
| Event | 事件/情节点 | 未实现 |
| Relation | 人物关系（旧版） | 未实现 |

---

## 章节相关模型

### Chapter

章节基本结构，用于在内存中表示章节位置。

```python
class Chapter(BaseModel):
    index: int    # 章节索引（从 0 开始）
    title: str    # 章节标题
    start: int    # 起始字符位置
    end: int      # 结束字符位置
```

### ChapterAnalysis

AI 章节分析结果。

```python
class ChapterAnalysis(BaseModel):
    chapter_index: int           # 章节索引
    title: str                   # 章节标题
    summary: str                 # 章节摘要（100-200字）
    characters: list[str] = []   # 出场人物
    events: list[str] = []       # 关键事件
    sentiment: str = ""          # 情感基调
    keywords: list[str] = []     # 关键词
```

**情感类型**:
- 热血、紧张、轻松、悲伤、温馨、恐怖、平静、激动、搞笑

---

## 人物相关模型

### Character（简要信息）

用于人物列表展示的简要信息。

```python
class Character(BaseModel):
    id: str                      # 唯一标识
    name: str                    # 人物名称
    aliases: list[str] = []      # 别名列表
    description: str = ""        # 人物描述（50-100字）
    first_appearance: int = 0    # 首次出场章节
    role: str = "minor"          # 角色类型
    attributes: dict = {}        # 扩展属性
```

**角色类型（role）**:
| 值 | 含义 |
|---|------|
| `protagonist` | 主角 |
| `antagonist` | 反派 |
| `supporting` | 配角 |
| `minor` | 次要角色 |

### DetailedCharacter（详细分析）

人物按需分析的完整结果。

```python
class DetailedCharacter(BaseModel):
    name: str                               # 人物名称
    aliases: list[str] = []                 # 别名列表

    # 基本信息
    description: str = ""                   # 人物简介
    role: str = "unknown"                   # 角色类型
    personality: list[str] = []             # 性格特点

    # 出现章节
    appearances: list[CharacterAppearance] = []
    first_appearance: int = -1              # 首次出场章节
    total_chapters: int = 0                 # 出现章节总数

    # 人物关系
    relations: list[CharacterRelation] = []

    # 分析状态
    analysis_status: str = "pending"        # 分析状态
    analyzed_chapters: list[int] = []       # 已分析的章节
    error_message: str = ""                 # 错误信息
```

**分析状态（analysis_status）**:
| 值 | 含义 |
|---|------|
| `pending` | 待分析 |
| `searching` | 搜索中 |
| `analyzing` | 分析中 |
| `completed` | 完成 |
| `error` | 错误 |

### CharacterAppearance（章节出现）

人物在某章节的出现详情。

```python
class CharacterAppearance(BaseModel):
    chapter_index: int           # 章节索引
    chapter_title: str           # 章节标题
    events: list[str] = []       # 涉及此人物的事件
    interactions: list[str] = [] # 与其他角色的互动
    quote: str = ""              # 代表性台词或描述
```

### CharacterRelation（人物关系）

人物之间的关系。

```python
class CharacterRelation(BaseModel):
    target_name: str                   # 关系对象
    relation_type: str                 # 关系类型
    description: str                   # 关系描述
    evidence_chapters: list[int] = []  # 证据章节
```

**关系类型（relation_type）**:
| 值 | 含义 |
|---|------|
| `friend` | 朋友 |
| `enemy` | 敌人 |
| `lover` | 恋人 |
| `family` | 家人 |
| `mentor` | 师徒 |
| `rival` | 对手 |

### CharacterSearchResult（搜索结果）

人物快速搜索的返回结果（不存储，仅 API 响应）。

```python
class CharacterSearchResult(BaseModel):
    name: str                        # 人物名称
    found_in_chapters: list[int]     # 出现的章节索引
    chapter_titles: list[str]        # 章节标题
    total_mentions: int              # 总提及次数
```

---

## 事件相关模型（未实现）

### Event

事件/情节点模型，用于时间线功能。

```python
class Event(BaseModel):
    id: str                     # 唯一标识
    chapter: int                # 所在章节
    title: str                  # 事件标题
    summary: str                # 事件摘要
    characters: list[str] = []  # 涉及人物
    location: str = ""          # 地点
    importance: int = 1         # 重要性（1-5）
    tags: list[str] = []        # 标签
```

### Relation（旧版）

人物关系模型（旧版，被 CharacterRelation 替代）。

```python
class Relation(BaseModel):
    source: str              # 源人物
    target: str              # 目标人物
    type: str                # 关系类型
    description: str = ""    # 关系描述
    evidence: list[str] = [] # 证据文本
    chapters: list[int] = [] # 相关章节
```

---

## 模型关系图

```
Book (内存)
 ├── chapters: list[Chapter]
 └── metadata: dict

ChapterAnalysis (章节分析)
 ├── chapter_index
 ├── summary
 ├── characters: list[str]
 └── events: list[str]

Character (人物简要)
 └── 用于列表展示

DetailedCharacter (人物详细)
 ├── appearances: list[CharacterAppearance]
 │    ├── events
 │    └── interactions
 └── relations: list[CharacterRelation]
      └── evidence_chapters
```

---

## 相关文件

- **模型定义**: `apps/api/src/knowledge/models.py`
- **存储管理**: `apps/api/src/core/book.py`
- **存储格式**: [data-storage.md](./data-storage.md)
