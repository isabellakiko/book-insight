# API 路由文档

> 后端 API 接口快速参考

**框架**: FastAPI
**Base URL**: `http://localhost:8000`
**最后更新**: 2025-12-09

---

## 路由概览

| 路由文件 | 前缀 | 描述 |
|----------|------|------|
| `books.py` | `/api/books` | 书籍管理 |
| `analysis.py` | `/api/analysis` | AI 分析任务 |
| `rag.py` | `/api/rag` | RAG 问答系统 |

---

## Books 模块（books.py）

### GET /api/books
**描述**: 获取所有书籍列表

**响应**:
```json
{
  "books": [
    {
      "id": "string",
      "title": "string",
      "author": "string",
      "total_chapters": 0,
      "total_characters": 0
    }
  ]
}
```

### POST /api/books/upload
**描述**: 上传书籍文件

**请求**: `multipart/form-data`
| 参数 | 类型 | 描述 |
|------|------|------|
| file | File | TXT 书籍文件 |

**响应**:
```json
{
  "id": "string",
  "title": "string",
  "total_chapters": 0
}
```

### GET /api/books/{book_id}
**描述**: 获取书籍详情

**响应**:
```json
{
  "id": "string",
  "title": "string",
  "author": "string",
  "total_chapters": 0,
  "total_characters": 0
}
```

### GET /api/books/{book_id}/chapters
**描述**: 获取书籍章节列表

**响应**:
```json
{
  "chapters": [
    {
      "index": 0,
      "title": "string",
      "start": 0,
      "end": 0
    }
  ]
}
```

### GET /api/books/{book_id}/chapters/{chapter_index}/content
**描述**: 获取单章内容

**响应**:
```json
{
  "content": "章节完整文本内容"
}
```

### DELETE /api/books/{book_id}
**描述**: 删除书籍及其相关分析数据

**响应**:
```json
{
  "message": "Book deleted successfully"
}
```

---

## Analysis 模块（analysis.py）

### GET /api/analysis/{book_id}/chapters
**描述**: 获取所有章节的分析结果

**响应**:
```json
{
  "analyses": [
    {
      "chapter_index": 0,
      "title": "string",
      "summary": "string",
      "characters": ["string"],
      "events": ["string"],
      "sentiment": "string",
      "keywords": ["string"]
    }
  ]
}
```

### GET /api/analysis/{book_id}/chapters/{chapter_index}
**描述**: 获取单个章节的分析结果

**响应**:
```json
{
  "chapter_index": 0,
  "title": "string",
  "summary": "string",
  "characters": ["string"],
  "events": ["string"],
  "sentiment": "string",
  "keywords": ["string"]
}
```

### POST /api/analysis/{book_id}/chapters/{chapter_index}
**描述**: 分析单个章节（AI 驱动）

**响应**:
```json
{
  "chapter_index": 0,
  "title": "string",
  "summary": "string",
  "characters": ["string"],
  "events": ["string"],
  "sentiment": "string",
  "keywords": ["string"]
}
```

### POST /api/analysis/{book_id}/batch
**描述**: 批量分析章节（后台任务）

**请求体**:
```json
{
  "start_chapter": 0,
  "end_chapter": 10,
  "parallel": 3
}
```

**响应**:
```json
{
  "message": "Batch analysis started",
  "chapters": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
```

### GET /api/analysis/{book_id}/characters
**描述**: 获取已提取的人物列表

**响应**:
```json
{
  "characters": [
    {
      "id": "string",
      "name": "string",
      "aliases": ["string"],
      "description": "string",
      "role": "protagonist|antagonist|supporting|minor",
      "first_appearance": 0
    }
  ]
}
```

### POST /api/analysis/{book_id}/characters/extract
**描述**: 提取书籍人物（AI 驱动）

**请求体**（可选）:
```json
{
  "sample_chapters": [0, 5, 10]
}
```

**响应**:
```json
{
  "characters": [
    {
      "id": "string",
      "name": "string",
      "aliases": ["string"],
      "description": "string",
      "role": "protagonist|antagonist|supporting|minor",
      "first_appearance": 0
    }
  ]
}
```

---

## RAG 模块（rag.py）

### POST /api/rag/{book_id}/index
**描述**: 为书籍创建向量索引

**请求体**（可选）:
```json
{
  "chunk_size": 500,
  "chunk_overlap": 100
}
```

**响应**:
```json
{
  "status": "success",
  "chunks_indexed": 0
}
```

### GET /api/rag/{book_id}/status
**描述**: 检查书籍的向量索引状态

**响应**:
```json
{
  "indexed": true,
  "chunk_count": 0
}
```

### POST /api/rag/{book_id}/query
**描述**: 向量相似度检索（不含 AI 回答）

**请求体**:
```json
{
  "query": "string",
  "top_k": 5
}
```

**响应**:
```json
{
  "query": "string",
  "results": [
    {
      "chapter_index": 0,
      "chapter_title": "string",
      "content": "string",
      "score": 0.95
    }
  ]
}
```

### POST /api/rag/{book_id}/ask
**描述**: RAG 问答（含 AI 回答）

**请求体**:
```json
{
  "query": "string",
  "top_k": 5
}
```

**响应**:
```json
{
  "query": "string",
  "answer": "string",
  "results": [
    {
      "chapter_index": 0,
      "chapter_title": "string",
      "content": "string",
      "score": 0.95
    }
  ]
}
```

---

## 错误处理

### 通用错误格式
```json
{
  "detail": "错误描述"
}
```

### 常见状态码
| 状态码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 相关文件

- `apps/api/src/routers/books.py`
- `apps/api/src/routers/analysis.py`
- `apps/api/src/routers/rag.py`
