# API 路由文档

> 后端 API 接口快速参考

**框架**: FastAPI
**Base URL**: `http://localhost:8000`
**最后更新**: 2025-12-11

---

## 路由概览

| 路由文件 | 前缀 | 描述 |
|----------|------|------|
| `books.py` | `/api/books` | 书籍管理 |
| `analysis.py` | `/api/analysis` | AI 分析任务 |
| `rag.py` | `/api/rag` | RAG 问答系统 |

---

## 健康检查端点

### GET /api/health

**描述**: 服务健康检查端点

**位置**: `apps/api/src/main.py`（非独立路由文件）

**响应**:
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

**使用场景**:
- Docker 容器健康检查 (`healthcheck`)
- 负载均衡器探活
- 监控系统集成（如 Prometheus）
- CI/CD 部署验证

**示例调用**:
```bash
curl http://localhost:8000/api/health
```

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

### POST /api/analysis/{book_id}/characters/search
**描述**: 快速搜索人物出现的章节（纯文本搜索，不调用 AI）

**请求体**:
```json
{
  "name": "张成"
}
```

**响应**:
```json
{
  "name": "张成",
  "found_in_chapters": [0, 1, 5, 10],
  "chapter_titles": ["第一章", "第二章", "第六章", "第十一章"],
  "total_mentions": 156
}
```

### POST /api/analysis/{book_id}/characters/analyze
**描述**: 完整分析单个人物（同步，可能耗时较长）

**请求体**:
```json
{
  "name": "张成",
  "max_chapters": 30
}
```

**响应**: `DetailedCharacter` 对象（见下方）

### GET /api/analysis/{book_id}/characters/stream
**描述**: 流式分析人物（SSE，推荐用于前端）

**查询参数**:
| 参数 | 类型 | 描述 |
|------|------|------|
| name | string | 人物名称 |

**响应**: Server-Sent Events (SSE) 流

**事件类型**:

| 事件名 | 数据结构 | 说明 |
|--------|----------|------|
| `search_complete` | `CharacterSearchResult` | 搜索完成 |
| `chapter_analyzed` | `{chapter_index, appearance}` | 单章分析完成 |
| `chapter_error` | `{chapter_index, error}` | 单章分析出错 |
| `relations_analyzed` | `{relations}` | 关系分析完成 |
| `completed` | `DetailedCharacter` | 全部完成 |

**前端使用示例**:
```javascript
const eventSource = new EventSource(
  `/api/analysis/${bookId}/characters/stream?name=${encodeURIComponent(name)}`
);

eventSource.addEventListener('search_complete', (e) => {
  const data = JSON.parse(e.data);
  console.log('搜索完成:', data.total_mentions, '次提及');
});

eventSource.addEventListener('chapter_analyzed', (e) => {
  const data = JSON.parse(e.data);
  console.log('分析章节:', data.chapter_index);
});

eventSource.addEventListener('completed', (e) => {
  const character = JSON.parse(e.data);
  console.log('分析完成:', character);
  eventSource.close();
});
```

### GET /api/analysis/{book_id}/characters/detailed
**描述**: 列出所有已分析的人物

**响应**: `list[DetailedCharacter]`

### GET /api/analysis/{book_id}/characters/detailed/{character_name}
**描述**: 获取已分析的人物详情

**响应**:
```json
{
  "name": "张成",
  "aliases": ["小成", "成哥"],
  "description": "主角，重生者...",
  "role": "protagonist",
  "personality": ["坚毅", "果断", "重情义"],
  "appearances": [
    {
      "chapter_index": 0,
      "chapter_title": "第一章",
      "events": ["重生回到高中"],
      "interactions": ["与李明相遇"],
      "quote": "这一世，我绝不会再让悲剧重演。"
    }
  ],
  "first_appearance": 0,
  "total_chapters": 1112,
  "relations": [
    {
      "target_name": "李明",
      "relation_type": "friend",
      "description": "高中同学，生死之交",
      "evidence_chapters": [0, 5, 10]
    }
  ],
  "analysis_status": "completed",
  "analyzed_chapters": [0, 100, 500],
  "error_message": ""
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

## 详细错误码

### Books 模块

| 端点 | 状态码 | 错误场景 | detail 消息 |
|------|--------|----------|-------------|
| GET /api/books/{id} | 404 | 书籍不存在 | `"Book not found"` |
| GET /api/books/{id}/chapters | 404 | 书籍不存在 | `"Book not found"` |
| GET /api/books/{id}/chapters/{index}/content | 404 | 书籍不存在 | `"Book not found"` |
| GET /api/books/{id}/chapters/{index}/content | 404 | 章节索引越界 | `"Chapter not found"` |
| POST /api/books/upload | 400 | 非 TXT 文件 | `"Only .txt files are supported"` |
| DELETE /api/books/{id} | 404 | 书籍不存在 | `"Book not found"` |

### Analysis 模块

| 端点 | 状态码 | 错误场景 | detail 消息 |
|------|--------|----------|-------------|
| GET /{book_id}/chapters | 404 | 书籍不存在 | `"Book not found"` |
| GET /{book_id}/chapters/{index} | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/chapters/{index} | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/chapters/{index} | 404 | 章节索引越界 | `"Chapter not found"` |
| POST /{book_id}/batch | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/characters/search | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/characters/analyze | 404 | 书籍不存在 | `"Book not found"` |
| GET /{book_id}/characters/stream | 404 | 书籍不存在 | `"Book not found"` |
| GET /{book_id}/characters/detailed/{name} | 404 | 书籍不存在 | `"Book not found"` |
| GET /{book_id}/characters/detailed | 404 | 书籍不存在 | `"Book not found"` |

> **注意**: `GET /{book_id}/characters/detailed/{name}` 人物不存在时返回 `null`，不抛出 404。

### RAG 模块

| 端点 | 状态码 | 错误场景 | detail 消息 |
|------|--------|----------|-------------|
| POST /{book_id}/index | 404 | 书籍不存在 | `"Book not found"` |
| GET /{book_id}/status | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/query | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/query | 400 | 未创建索引 | `"Book not indexed. Call /index first."` |
| POST /{book_id}/ask | 404 | 书籍不存在 | `"Book not found"` |
| POST /{book_id}/ask | 400 | 未创建索引 | `"Book not indexed. Call /index first."` |

### 前端错误处理示例

```javascript
import { toast } from 'your-toast-library';

async function handleApiCall() {
  try {
    const result = await api.analyzeChapter(bookId, chapterIndex);
    return result;
  } catch (error) {
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          // 请求错误（如未索引）
          toast.error(data.detail || '请求参数错误');
          break;
        case 404:
          // 资源不存在
          toast.error(data.detail || '资源不存在');
          break;
        case 500:
          // 服务器错误
          toast.error('服务器错误，请稍后重试');
          break;
        default:
          toast.error('未知错误');
      }
    } else {
      // 网络错误
      toast.error('网络连接失败');
    }
    throw error;
  }
}
```

---

## 相关文件

- `apps/api/src/routers/books.py`
- `apps/api/src/routers/analysis.py`
- `apps/api/src/routers/rag.py`
