# Book Insight 架构文档

> 系统架构、数据流、存储结构完整参考

**创建时间**: 2025-12-10
**最后更新**: 2025-12-10
**架构版本**: v2.0（三层职责架构）

---

## 1. 设计理念

### 1.1 核心原则

| 原则 | 说明 |
|------|------|
| **离线分析 + 在线展示** | AI 分析通过脚本离线执行，前端只做数据可视化 |
| **数据即真相** | 所有分析结果持久化为 JSON，前端不触发 AI 调用 |
| **增量积累** | 人物分析支持多次运行，数据逐步丰富 |
| **单一数据入口** | 所有数据读写通过 API 层，脚本不直接操作文件 |

### 1.2 为什么这样设计？

**问题**：早期架构中，前端实时触发 AI 分析存在问题：
- API 调用成本高（每次打开页面都要付费）
- 响应时间长（用户等待体验差）
- 数据不持久（刷新后丢失）

**解决方案**：分离"分析"和"展示"两个阶段
- **分析阶段**：开发者通过 CLI 脚本离线执行，结果存为 JSON
- **展示阶段**：前端读取已有 JSON，秒级响应，零 API 成本

---

## 2. 三层职责架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLI 层 (scripts/)                           │
│  职责：用户交互、任务编排、进度显示                                   │
│  原则：只通过 HTTP 调用 API，不直接访问文件系统                       │
│  文件：analyze.py, migrate_data.py, lib/api_client.py               │
├─────────────────────────────────────────────────────────────────────┤
│                         API 层 (apps/api/)                          │
│  职责：所有业务逻辑、数据读写的唯一入口                               │
│  包含：                                                              │
│    - 实时 API（前端用）：书籍管理、数据查询、RAG 问答                 │
│    - 分析 API（脚本用）：人物搜索、流式分析、增量更新                 │
│  文件：routers/, ai/tasks/, core/book.py                            │
├─────────────────────────────────────────────────────────────────────┤
│                         数据层 (data/)                              │
│  职责：持久化存储，只通过 BookManager 访问                           │
│  格式：JSON 文件 + ChromaDB 向量库                                  │
│  原则：统一格式，人物按名字组织目录                                  │
├─────────────────────────────────────────────────────────────────────┤
│                         展示层 (apps/web/)                          │
│  职责：纯可视化，只读取已有数据，不触发 AI 分析                       │
│  技术：React 18 + Zustand + TanStack Query                          │
│  特点：主题切换、响应式设计、Editorial 杂志风格                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 层间通信

```
用户 ──▶ CLI 脚本 ──HTTP/SSE──▶ FastAPI ──▶ BookManager ──▶ JSON 文件
                                   │
用户 ──▶ React 前端 ──HTTP GET──▶ FastAPI ──▶ BookManager ──▶ JSON 文件
```

**关键约束**：
- CLI 脚本 **禁止** 直接 import 后端模块
- CLI 脚本 **禁止** 直接读写 data/ 目录
- 前端 **禁止** 调用分析 API（只调用查询 API）

---

## 3. 数据流详解

### 3.1 分析阶段（离线执行）

```
┌─────────────────────────────────────────────────────────────────────┐
│                        人物分析流程                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  python scripts/analyze.py 赵秦                                     │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ 1. 搜索阶段  │  POST /api/analysis/{book_id}/characters/search   │
│  │   全书正则   │  ──────────────────────────────────────────────▶  │
│  └──────┬───────┘                                                   │
│         │ 返回: found_in_chapters = [168, 169, 170, ...]           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ 2. 采样阶段  │  智能采样：从 1112 章中选 30 章（均匀分布）        │
│  │   均匀分布   │                                                   │
│  └──────┬───────┘                                                   │
│         │ 采样: chapters_to_analyze = [168, 288, 439, ...]         │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ 3. 分析阶段  │  GET /api/analysis/{book_id}/characters/stream    │
│  │   SSE 流式   │  ──────────────────────────────────────────────▶  │
│  └──────┬───────┘                                                   │
│         │ SSE 事件流:                                               │
│         │   search_complete → chapter_analyzed (x30) → completed   │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ 4. 存储阶段  │  BookManager.save_detailed_character()           │
│  │   JSON 持久化│  ──────────────────────────────────────────────▶  │
│  └──────────────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  data/analysis/{book_id}/characters/赵秦/profile.json               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 展示阶段（实时响应）

```
┌─────────────────────────────────────────────────────────────────────┐
│                        前端数据加载流程                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  用户访问 /characters/赵秦                                          │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ React 组件   │  CharacterDetail.jsx                              │
│  │ useEffect    │                                                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ Hook 调用    │  useCharacterAnalysis().loadCached('赵秦')        │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐  GET /api/analysis/{book_id}/characters/detailed/赵秦
│  │ API 请求     │  ──────────────────────────────────────────────▶  │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ FastAPI      │  BookManager.get_detailed_character('赵秦')       │
│  │ 读取 JSON    │                                                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  data/analysis/{book_id}/characters/赵秦/profile.json               │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │ 渲染页面     │  展示人物档案、章节足迹、人物关系等                │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.3 两阶段对比

| 维度 | 分析阶段 | 展示阶段 |
|------|----------|----------|
| 执行方式 | 命令行脚本 | 浏览器访问 |
| 触发者 | 开发者主动执行 | 用户访问页面 |
| AI 调用 | ✅ 调用百炼 API | ❌ 无 AI 调用 |
| 耗时 | 分钟级（取决于章节数） | 毫秒级 |
| 成本 | 按 token 计费 | 零成本 |
| 数据变化 | 写入 JSON | 只读 |

---

## 4. 数据存储结构

### 4.1 目录总览

```
data/
├── books/                              # 原始书籍
│   ├── 那些热血飞扬的日子.txt          # 原始 TXT 文件
│   └── a04f9ba66252/                   # book_id = MD5(filename)[:12]
│       ├── meta.json                   # 书籍元信息
│       └── chapters/                   # 章节独立存储（8098 个文件）
│           ├── 0001.json               # 第 1 章（index=0）
│           ├── 0002.json               # 第 2 章（index=1）
│           └── ...
│
├── analysis/                           # 分析结果
│   └── a04f9ba66252/
│       ├── characters.json             # 人物索引（轻量列表）
│       ├── characters/                 # 详细人物分析（按人物名组织）
│       │   ├── 张成/
│       │   │   └── profile.json
│       │   ├── 赵秦/
│       │   │   └── profile.json
│       │   └── 夏诗/
│       │       └── profile.json
│       └── chapters/                   # 章节分析结果
│           ├── 0000.json               # 第 1 章分析
│           └── ...
│
└── vector_store/                       # RAG 向量数据库
    └── a04f9ba66252/                   # ChromaDB 持久化目录
```

### 4.2 文件命名规则

| 类型 | 命名格式 | 示例 |
|------|----------|------|
| 书籍 ID | `MD5(filename)[:12]` | `a04f9ba66252` |
| 章节文件 | `{index+1:04d}.json` | `0001.json`（第1章） |
| 章节分析 | `{index:04d}.json` | `0000.json`（第1章分析） |
| 人物目录 | `{人物名}/` | `赵秦/` |
| 人物档案 | `profile.json` | 固定名称 |

---

## 5. 数据格式定义

### 5.1 书籍元信息 `meta.json`

```json
{
  "id": "a04f9ba66252",
  "title": "那些热血飞扬的日子",
  "author": "肤浅失眠中",
  "total_chapters": 8098,
  "total_characters": 18743116,
  "note": "章节标题已修复"
}
```

### 5.2 章节文件 `chapters/0001.json`

```json
{
  "index": 0,
  "title": "第一章 重生",
  "content": "章节完整内容..."
}
```

### 5.3 人物索引 `characters.json`

```json
[
  {
    "id": "2fecbc8a",
    "name": "张成",
    "aliases": ["成哥"],
    "description": "主角，重生者，性格坚毅果断...",
    "first_appearance": 0,
    "role": "protagonist",
    "attributes": {}
  },
  {
    "name": "赵秦",
    "aliases": [],
    "description": "赵琳的姐姐，性格冷静理智...",
    "first_appearance": 168,
    "role": "supporting"
  }
]
```

**字段说明**：
| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识（可选，旧数据有） |
| name | string | 人物名称 |
| aliases | string[] | 别名列表 |
| description | string | 简短描述（50-100字） |
| first_appearance | int | 首次出场章节索引 |
| role | string | 角色类型：protagonist/antagonist/supporting/minor |

### 5.4 人物详细档案 `characters/{name}/profile.json`

```json
{
  // === 基础信息 ===
  "name": "赵秦",
  "aliases": [],
  "description": "赵琳的姐姐，性格冷静理智，对妹妹的学业极为重视...",
  "role": "supporting",
  "personality": ["冷静", "理智", "有担当", "围棋高手"],

  // === 深度分析（AI 生成）===
  "summary": "张成生命中的重要女性，从初恋姐姐逐步发展为恋人",
  "growth_arc": "从冷淡旁观者 → 工作伙伴 → 亲密恋人的转变过程",
  "core_traits": [
    {
      "trait": "冷静理智",
      "description": "面对危机时保持冷静，善于分析局势",
      "evidence": "第 XXX 章：'不管发生什么，先冷静下来再说...'"
    },
    {
      "trait": "重情重义",
      "description": "对家人和爱人有强烈的保护欲",
      "evidence": "第 XXX 章：..."
    }
  ],
  "strengths": ["围棋高手", "思维缜密", "临危不乱"],
  "weaknesses": ["有时过于理性", "不善表达情感"],
  "notable_quotes": [
    "这盘棋，我认输。",
    "有些事，不是你想躲就能躲得掉的。"
  ],

  // === 出场记录 ===
  "appearances": [
    {
      "chapter_index": 168,
      "chapter_title": "第一百六十九章 初见",
      "events": ["首次出场", "与张成对弈围棋"],
      "interactions": ["与张成的初次交锋"],
      "quote": "你的棋路很野，但缺乏章法。"
    },
    {
      "chapter_index": 288,
      "chapter_title": "第二百八十九章 重逢",
      "events": ["在公司偶遇", "得知成为同事"],
      "interactions": ["与张成工作中的配合"],
      "quote": "没想到会在这里见到你。"
    }
    // ... 更多章节
  ],

  // === 人物关系 ===
  "relations": [
    {
      "target_name": "张成",
      "relation_type": "lover",
      "description": "从初恋女友的姐姐 → 同事 → 恋人",
      "evidence_chapters": [168, 500, 1000, 2000]
    },
    {
      "target_name": "赵琳",
      "relation_type": "family",
      "description": "亲妹妹，张成的初恋女友",
      "evidence_chapters": [168, 200]
    }
  ],

  // === 统计信息 ===
  "first_appearance": 168,
  "last_appearance": 8097,
  "total_chapters": 1112,

  // === 分析元信息 ===
  "analyzed_chapters": [168, 288, 439, 590, 741, ...],  // 已分析的章节列表
  "total_analyzed_chapters": 30,
  "analysis_status": "completed",  // pending/searching/analyzing/completed/error
  "error_message": ""
}
```

### 5.5 章节分析 `chapters/0000.json`

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

---

## 6. API 端点参考

### 6.1 书籍管理

| 端点 | 方法 | 描述 | 调用方 |
|------|------|------|--------|
| `/api/books` | GET | 列出所有书籍 | 前端 |
| `/api/books/upload` | POST | 上传书籍 | 前端 |
| `/api/books/{id}` | GET | 获取书籍详情 | 前端 |
| `/api/books/{id}` | DELETE | 删除书籍 | 前端 |
| `/api/books/{id}/chapters` | GET | 获取章节列表 | 前端 |
| `/api/books/{id}/chapters/{index}/content` | GET | 获取章节内容 | 前端 |

### 6.2 分析 API（脚本使用）

| 端点 | 方法 | 描述 | 调用方 |
|------|------|------|--------|
| `/api/analysis/{book_id}/characters/search` | POST | 搜索人物出现章节 | 脚本 |
| `/api/analysis/{book_id}/characters/stream` | GET | SSE 流式分析人物 | 脚本 |
| `/api/analysis/{book_id}/characters/continue` | GET | 增量分析更多章节 | 脚本 |
| `/api/analysis/{book_id}/chapters/{index}` | POST | 分析单章 | 脚本 |
| `/api/analysis/{book_id}/batch` | POST | 批量分析章节 | 脚本 |

### 6.3 查询 API（前端使用）

| 端点 | 方法 | 描述 | 调用方 |
|------|------|------|--------|
| `/api/analysis/{book_id}/characters` | GET | 获取人物列表 | 前端 |
| `/api/analysis/{book_id}/characters/detailed/{name}` | GET | 获取人物详细档案 | 前端 |
| `/api/analysis/{book_id}/characters/detailed` | GET | 获取所有已分析人物 | 前端 |
| `/api/analysis/{book_id}/chapters` | GET | 获取所有章节分析 | 前端 |
| `/api/analysis/{book_id}/chapters/{index}` | GET | 获取单章分析 | 前端 |

### 6.4 RAG 问答

| 端点 | 方法 | 描述 | 调用方 |
|------|------|------|--------|
| `/api/rag/{book_id}/index` | POST | 创建向量索引 | 前端/脚本 |
| `/api/rag/{book_id}/status` | GET | 获取索引状态 | 前端 |
| `/api/rag/{book_id}/ask` | POST | RAG 智能问答 | 前端 |
| `/api/rag/{book_id}/query` | POST | 向量相似度查询 | 前端 |

---

## 7. 前端页面与数据源

### 7.1 页面列表

| 页面 | 路由 | 数据源 API | 数据文件 |
|------|------|------------|----------|
| Dashboard | `/` | `GET /api/books` | `books/*/meta.json` |
| Characters | `/characters` | `GET /api/analysis/{id}/characters` | `characters.json` |
| CharacterDetail | `/characters/:name` | `GET /api/analysis/{id}/characters/detailed/{name}` | `characters/{name}/profile.json` |
| ChapterAnalysis | `/chapters/:bookId` | `GET /api/analysis/{id}/chapters` | `chapters/*.json` |
| Timeline | `/timeline` | `GET /api/analysis/{id}/chapters` | `chapters/*.json` |
| RAGChat | `/chat` | `POST /api/rag/{id}/ask` | `vector_store/` |

### 7.2 CharacterDetail 数据映射

| UI 区块 | 数据字段 |
|---------|----------|
| Header 标题区 | `name`, `aliases`, `first_appearance`, `total_chapters` |
| 人物概述 | `summary` |
| 成长轨迹 | `growth_arc` |
| 性格剖析 | `core_traits[].trait`, `core_traits[].evidence` |
| 优点 | `strengths[]` |
| 缺点 | `weaknesses[]` |
| 经典语录 | `notable_quotes[]` |
| 人物关系 | `relations[].target_name`, `relations[].description` |
| 章节足迹 | `appearances[].chapter_title`, `appearances[].events`, `appearances[].quote` |

---

## 8. CLI 脚本使用指南

### 8.1 统一入口 `scripts/analyze.py`

```bash
# 智能采样分析（新人物，默认 30 章）
python scripts/analyze.py 赵秦

# 查看分析状态
python scripts/analyze.py 赵秦 --status

# 增量分析（已有人物，再分析 50 章）
python scripts/analyze.py 赵秦 --continue --chapters 50

# 批量分析多个人物
python scripts/analyze.py 张成 赵秦 夏诗
```

### 8.2 脚本架构

```
scripts/
├── analyze.py              # 统一人物分析 CLI
├── migrate_data.py         # 数据迁移工具（一次性）
└── lib/
    ├── __init__.py
    └── api_client.py       # HTTP/SSE 客户端封装
```

### 8.3 api_client.py 功能

```python
class BookInsightClient:
    def __init__(self, base_url="http://localhost:8000")

    # 健康检查
    def check_health() -> bool

    # 人物分析
    def search_character(book_id, name) -> dict
    def stream_character_analysis(book_id, name, chapters) -> Generator[dict]
    def continue_character_analysis(book_id, name, chapters) -> Generator[dict]
    def get_detailed_character(book_id, name) -> dict

    # 书籍信息
    def get_books() -> list
    def get_book(book_id) -> dict
```

---

## 9. 核心模块职责

### 9.1 BookManager (`apps/api/src/core/book.py`)

**职责**：数据层唯一入口，所有文件读写通过此模块

```python
class BookManager:
    # 书籍操作
    @classmethod
    def list_books() -> list[dict]
    @classmethod
    def get_book(book_id: str) -> dict
    @classmethod
    def import_book(content: bytes, filename: str) -> dict
    @classmethod
    def delete_book(book_id: str) -> bool

    # 章节操作
    @classmethod
    def get_chapter_file(book_id: str, index: int) -> dict
    @classmethod
    def split_book_to_chapters(book_id: str) -> int

    # 人物操作
    @classmethod
    def get_characters(book_id: str) -> list[dict]
    @classmethod
    def get_detailed_character(book_id: str, name: str) -> dict | None
    @classmethod
    def get_detailed_characters(book_id: str) -> list[dict]
    @classmethod
    def save_detailed_character(book_id: str, character: DetailedCharacter) -> None
```

### 9.2 AI Tasks (`apps/api/src/ai/tasks/`)

| 模块 | 文件 | 职责 |
|------|------|------|
| 章节分析 | `chapter.py` | 单章 AI 分析（摘要、人物、事件） |
| 人物提取 | `character.py` | 全书人物识别（采样分析） |
| 按需分析 | `character_analyzer.py` | 指定人物深度分析（SSE 流式） |

### 9.3 RAG System (`apps/api/src/rag/`)

| 模块 | 文件 | 职责 |
|------|------|------|
| 向量存储 | `store.py` | ChromaDB 索引管理 |
| 检索器 | `retriever.py` | 语义搜索 + 上下文构建 |

---

## 10. 设计决策记录

### 10.1 为什么人物目录用名字而不是 ID？

**决策**：`characters/赵秦/profile.json` 而非 `characters/3c755ea96b38.json`

**原因**：
1. 可读性：直接看目录就知道有哪些人物
2. 可调试：手动检查/修改数据更方便
3. 唯一性：人物名在同一本书内唯一

**代价**：
- 人物名有特殊字符时需要处理（URL 编码）
- 重命名人物需要移动目录

### 10.2 为什么脚本不直接读写文件？

**决策**：CLI 脚本只通过 HTTP 调用 API

**原因**：
1. 单一数据入口：避免数据格式不一致
2. 逻辑复用：分析逻辑只在 API 层实现一次
3. 可测试性：API 可单独测试，脚本只是调用方
4. 未来扩展：可以远程部署 API，脚本无需修改

### 10.3 为什么前端不触发分析？

**决策**：前端只调用查询 API，不调用分析 API

**原因**：
1. 成本控制：避免用户无意中触发大量 API 调用
2. 用户体验：秒级响应 vs 分钟级等待
3. 数据稳定：分析结果持久化，不会因刷新丢失

---

## 11. 常见问题

### Q1: 如何添加新人物分析？

```bash
python scripts/analyze.py 新人物名
```

脚本会自动：搜索全书 → 智能采样 → AI 分析 → 保存 JSON

### Q2: 如何查看已分析的人物？

```bash
# 方式 1：查看文件系统
ls data/analysis/a04f9ba66252/characters/

# 方式 2：API 查询
curl http://localhost:8000/api/analysis/a04f9ba66252/characters/detailed
```

### Q3: 分析数据在哪里？

```
data/analysis/{book_id}/characters/{人物名}/profile.json
```

### Q4: 前端显示"暂无分析数据"怎么办？

运行分析脚本：
```bash
python scripts/analyze.py 人物名
```

然后刷新页面。

---

## 12. 相关文档

| 文档 | 路径 | 内容 |
|------|------|------|
| 项目上下文 | `docs/ai-context/CONTEXT.md` | 快速恢复项目记忆 |
| 当前进度 | `docs/ai-context/CURRENT.md` | 开发日志、下一步计划 |
| API 路由 | `docs/development/api/routers.md` | 端点详细说明 |
| 数据模型 | `docs/development/api/models.md` | Pydantic 模型定义 |
| 数据存储 | `docs/development/api/data-storage.md` | 文件格式详细说明 |
| 前端页面 | `docs/development/web/pages.md` | React 组件说明 |
| 赵秦分析计划 | `docs/character-analysis/赵秦.md` | 具体人物分析案例 |

---

**文档维护**：架构变更时同步更新此文档
