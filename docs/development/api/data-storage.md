# 数据存储文档

> 文件存储结构与 JSON 格式规范

**位置**: `data/`
**管理模块**: `apps/api/src/core/book.py`
**最后更新**: 2025-12-09

---

## 目录结构总览

```
data/
├── books/                       # 书籍存储
│   ├── {filename}.txt           # 原始书籍文件
│   └── {book_id}/               # 书籍数据目录
│       ├── meta.json            # 书籍元信息
│       └── chapters/            # 章节独立存储
│           ├── 0001.json
│           ├── 0002.json
│           └── ...
│
├── analysis/                    # 分析结果
│   └── {book_id}/
│       ├── chapters/            # 章节分析
│       │   ├── 0000.json
│       │   ├── 0001.json
│       │   └── ...
│       ├── characters.json      # 人物列表（简略）
│       └── characters_detailed/ # 详细人物分析
│           ├── {hash}.json
│           └── ...
│
└── vector_store/                # 向量数据库
    └── {book_id}/               # ChromaDB 数据
```

---

## Book ID 生成规则

```python
book_id = hashlib.md5(filename.encode()).hexdigest()[:12]
```

- 输入：文件名（不含路径）
- 输出：12 位十六进制字符串
- 示例：`那些热血飞扬的日子.txt` → `a04f9ba66252`

---

## 书籍存储（books/）

### 原始文件存储

原始 TXT 文件直接存储在 `data/books/` 目录：

```
data/books/那些热血飞扬的日子.txt
```

### 书籍元信息（meta.json）

```json
{
  "id": "a04f9ba66252",
  "title": "那些热血飞扬的日子",
  "author": "肤浅失眠中",
  "total_chapters": 8098,
  "total_characters": 18743116,
  "note": "章节标题已修复，原书有大量编号错误"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 书籍唯一标识（12位） |
| title | string | 书名 |
| author | string | 作者 |
| total_chapters | int | 总章节数 |
| total_characters | int | 总字符数 |
| note | string | 备注（可选） |

### 章节文件（chapters/{index}.json）

文件名格式：`{index + 1:04d}.json`（从 0001 开始）

```json
{
  "index": 0,
  "title": "第一章 重生",
  "content": "章节完整内容..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| index | int | 章节索引（从 0 开始） |
| title | string | 章节标题 |
| content | string | 章节完整内容 |

---

## 分析结果存储（analysis/）

### 章节分析（chapters/{index}.json）

文件名格式：`{chapter_index:04d}.json`（从 0000 开始）

```json
{
  "chapter_index": 0,
  "title": "第一章 重生",
  "summary": "主角张成在一场意外中重生回到高中时代...",
  "characters": ["张成", "李明", "王芳"],
  "events": [
    "张成重生回到高中时代",
    "与李明在教室相遇"
  ],
  "sentiment": "热血",
  "keywords": ["重生", "高中", "觉醒"]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| chapter_index | int | 章节索引 |
| title | string | 章节标题 |
| summary | string | 章节摘要（100-200字） |
| characters | list[str] | 出场人物列表 |
| events | list[str] | 关键事件列表 |
| sentiment | string | 情感基调 |
| keywords | list[str] | 关键词列表 |

### 人物列表（characters.json）

```json
[
  {
    "id": "zhang_cheng",
    "name": "张成",
    "aliases": ["小成", "成哥"],
    "description": "主角，重生者，性格坚毅果断...",
    "first_appearance": 0,
    "role": "protagonist",
    "attributes": {}
  }
]
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 人物唯一标识 |
| name | string | 人物名称 |
| aliases | list[str] | 别名列表 |
| description | string | 人物描述（50-100字） |
| first_appearance | int | 首次出场章节索引 |
| role | string | 角色类型：protagonist/antagonist/supporting/minor |
| attributes | dict | 扩展属性 |

### 详细人物分析（characters_detailed/{hash}.json）

文件名格式：`{md5(name)[:12]}.json`

```json
{
  "name": "张成",
  "aliases": ["小成", "成哥"],
  "description": "主角，重生者，性格坚毅果断，善于把握机会...",
  "role": "protagonist",
  "personality": ["坚毅", "果断", "重情义", "有谋略"],
  "appearances": [
    {
      "chapter_index": 0,
      "chapter_title": "第一章 重生",
      "events": ["重生回到高中", "决定改变命运"],
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
      "description": "高中同学，后来成为生死之交",
      "evidence_chapters": [0, 5, 10]
    }
  ],
  "analysis_status": "completed",
  "analyzed_chapters": [0, 100, 500, 1000, 2000],
  "error_message": ""
}
```

---

## BookManager API

### 书籍操作

```python
from src.core.book import BookManager

# 列出所有书籍
books = BookManager.list_books()

# 获取单本书
book = BookManager.get_book(book_id)

# 导入书籍
book = await BookManager.import_book(content_bytes, filename)

# 删除书籍
success = BookManager.delete_book(book_id)
```

### 章节文件操作

```python
# 将书籍拆分为章节文件
num_chapters = BookManager.split_book_to_chapters(book_id)

# 检查是否已拆分
has_files = BookManager.has_chapter_files(book_id)

# 读取单个章节文件
chapter_data = BookManager.get_chapter_file(book_id, chapter_index)
```

### 章节分析操作

```python
# 获取所有章节分析
analyses = BookManager.get_analyses(book_id)

# 获取单章分析
analysis = BookManager.get_chapter_analysis(book_id, chapter_index)

# 保存章节分析
BookManager.save_chapter_analysis(book_id, analysis)
```

### 人物分析操作

```python
# 获取人物列表
characters = BookManager.get_characters(book_id)

# 保存人物列表
BookManager.save_characters(book_id, characters)

# 获取详细人物分析
detailed = BookManager.get_detailed_character(book_id, character_name)

# 获取所有详细人物
all_detailed = BookManager.get_detailed_characters(book_id)

# 保存详细人物分析
BookManager.save_detailed_character(book_id, detailed_character)
```

---

## 文件命名规范

| 类型 | 格式 | 示例 |
|------|------|------|
| 章节文件 | `{index+1:04d}.json` | `0001.json`, `0100.json` |
| 章节分析 | `{index:04d}.json` | `0000.json`, `0099.json` |
| 人物详情 | `{md5(name)[:12]}.json` | `a1b2c3d4e5f6.json` |

> 注意：章节文件从 `0001` 开始，分析文件从 `0000` 开始

---

## 相关文件

- **核心模块**: `apps/api/src/core/book.py`
- **数据模型**: `apps/api/src/knowledge/models.py`
- **配置文件**: `apps/api/src/config.py`
