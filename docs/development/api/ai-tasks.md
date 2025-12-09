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

## 相关模块

- **RAG 系统**: `apps/api/src/rag/` - 向量检索与问答
- **知识模型**: `apps/api/src/knowledge/models.py` - 数据结构定义
