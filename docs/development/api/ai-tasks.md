# AI 任务模块文档

> AI 分析任务的实现细节

**位置**: `apps/api/src/ai/`
**最后更新**: 2025-12-09

---

## 模块概览

```
apps/api/src/ai/
├── __init__.py
├── client.py          # AI 客户端（阿里云百炼）
└── tasks/
    ├── __init__.py
    ├── chapter.py     # 章节分析任务
    └── character.py   # 人物提取任务
    └── character_analyzer.py  # 人物按需分析（SSE）
```

---

## AI 客户端（client.py）

### 职责
- 封装阿里云百炼 API 调用（OpenAI SDK 兼容模式）
- 统一处理 API 配置和错误
- 支持标准对话和 JSON 响应两种模式

### 主要功能
```python
from src.ai.client import chat, chat_json

# 标准对话
response = await chat(prompt="问题", system="系统提示")

# JSON 响应（自动解析）
data = await chat_json(prompt="问题", system="系统提示")
```

### 配置
- 环境变量: `DASHSCOPE_API_KEY`
- Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- 模型: `qwen-plus`（可通过 `CHAT_MODEL` 环境变量配置）
- 默认参数:
  - max_tokens: 4096
  - temperature: 0.3（JSON 模式）/ 0.7（普通对话）

---

## 章节分析（chapter.py）

### 功能
分析单个章节，提取：
- 摘要（100-200字）
- 出场人物
- 关键事件
- 情感基调
- 关键词

### 调用示例
```python
from src.ai.tasks.chapter import ChapterAnalyzer

analyzer = ChapterAnalyzer()
result = await analyzer.analyze(
    chapter_index=0,
    chapter_title="第一章",
    chapter_content="章节内容..."
)
```

### 返回格式（ChapterAnalysis）
```python
{
    "chapter_index": 0,
    "title": "第一章",
    "summary": "章节摘要（100-200字）",
    "characters": ["人物1", "人物2"],
    "events": ["事件1描述", "事件2描述"],
    "sentiment": "紧张|轻松|悲伤|热血|平静|...",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}
```

### 特性
- 自动处理超长内容（>30000字符时截断）
- 使用 JSON 模式确保结构化输出
- 采用专业小说分析系统提示

---

## 人物提取（character.py）

### 功能
从书籍内容中提取人物信息：
- 人物名称和别名
- 人物描述（50-100字）
- 角色类型分类
- 首次出场章节

### 调用示例
```python
from src.ai.tasks.character import CharacterExtractor

extractor = CharacterExtractor()
result = await extractor.extract(
    book=book_object,
    sample_chapters=[0, 5, 10, 15, 20]  # 可选，默认自动采样
)
```

### 返回格式（Character 列表）
```python
{
    "characters": [
        {
            "id": "唯一ID",
            "name": "人物姓名",
            "aliases": ["别名1", "别名2"],
            "description": "人物简介（50-100字）",
            "role": "protagonist|antagonist|supporting|minor",
            "first_appearance": 0
        }
    ]
}
```

### 智能采样策略
默认自动采样关键章节：
- 开头章节
- 四分之一处
- 中点章节
- 四分之三处
- 结尾章节

每个章节内容限制在 5000 字符以内。

---

## Prompt 设计原则

1. **结构化输出**: 使用 JSON 模式确保响应可解析
2. **中文优先**: Prompt 使用中文，适配中文小说分析
3. **上下文限制**: 超长内容自动截断或分块处理
4. **专业角色**: 系统提示定义专业小说分析师角色

---

## 人物按需分析（character_analyzer.py）

### 功能
按需分析单个人物，支持三种模式：
- **快速搜索**：纯文本正则搜索，<100ms
- **完整分析**：AI 分析，1-5秒/人物
- **流式分析**：SSE 事件流，支持前端实时进度

### CharacterOnDemandAnalyzer 类

#### 1. 快速搜索
```python
result = analyzer.search(book, character_name)
# 返回 CharacterSearchResult
```
- 使用正则表达式搜索人物出现的所有章节
- 统计提及次数
- 不调用 AI，速度极快

#### 2. 完整同步分析
```python
result = await analyzer.analyze_full(book, character_name, max_chapters=30)
# 返回 DetailedCharacter
```

#### 3. 流式异步分析（推荐）
```python
async for event in analyzer.analyze_stream(book, character_name):
    # event: {"event": "xxx", "data": {...}}
```

### 分析流程
```
搜索人物出现章节
    ↓
限制分析章节数（默认30章）
    ↓
逐章分析人物出现（事件、互动、台词）
    ↓
分析人物关系（最多5个关键关系）
    ↓
分析性格特点（描述、性格词、角色类型）
    ↓
返回完整 DetailedCharacter
```

### SSE 事件类型

| 事件名 | 数据结构 | 说明 |
|--------|----------|------|
| `search_complete` | `CharacterSearchResult` | 搜索完成 |
| `chapter_analyzed` | `{chapter_index, appearance}` | 单章分析完成 |
| `chapter_error` | `{chapter_index, error}` | 单章分析出错 |
| `relations_analyzed` | `{relations}` | 关系分析完成 |
| `completed` | `DetailedCharacter` | 全部完成 |

### 内容限制
- 章节分析：内容 >15,000 字符时截断
- 关系分析：最多处理 30 条互动记录
- 返回关系：最多 5 个关键关系

### Prompt 模板

#### 章节出现分析
```
分析人物 "{name}" 在以下章节中的表现：

章节标题：{title}
章节内容：
{content}

返回 JSON 格式：
{
    "events": ["该人物在本章的主要事件，最多3个"],
    "interactions": ["与其他角色的互动，最多3个"],
    "quote": "代表性台词或描述（可为空）"
}
```

#### 关系分析
```
基于以下人物互动记录，分析 "{name}" 的人物关系：

{interactions_text}

返回 JSON 格式：
{
    "relations": [
        {
            "target_name": "关系对象",
            "relation_type": "friend/enemy/lover/family/mentor/rival",
            "description": "关系描述",
            "evidence_chapters": [章节索引列表]
        }
    ]
}

最多返回5个最重要的关系。
```

#### 性格分析
```
基于以下人物表现，分析 "{name}" 的性格特点：

{appearances_text}

返回 JSON 格式：
{
    "description": "人物简介（100-200字）",
    "personality": ["性格特点列表，3-5个词"],
    "role": "protagonist/antagonist/supporting/minor"
}
```

---

## 相关模块

- **RAG 系统**: `apps/api/src/rag/` - 向量检索与问答
- **知识模型**: `apps/api/src/knowledge/models.py` - 数据结构定义
