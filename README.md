# Book Insight

AI 驱动的个人书籍深度分析工具。

## 项目背景

阅读长篇小说时常遇到的问题：
- 人物太多记不住，读到后面忘了前面
- 想找某个情节在哪章，只能手动翻
- 缺乏对主题和人物弧光的系统理解

**Book Insight** 用 AI 增强阅读体验（不替代阅读）：
- 基于 RAG 的原文问答，回答有据可查
- 自动提取人物关系图谱
- 逐章 AI 分析，渐进式理解

## 功能

- **RAG 问答**：基于原文的智能问答
- **人物分析**：自动提取人物、关系、性格
- **情节时间线**：关键事件脉络梳理
- **章节分析**：逐章 AI 分析，提取摘要、人物、事件

## 技术栈

- **前端**：React 18 + Vite + TailwindCSS + TanStack Query
- **后端**：Python FastAPI + LangChain + ChromaDB
- **AI**：阿里云百炼 (qwen-plus) + text-embedding-v3

## 快速开始

### 1. 首次安装

```bash
# 一键安装前端 + 后端
pnpm setup
```

### 2. 配置环境变量

```bash
cp apps/api/.env.example apps/api/.env
# 编辑 .env 填入 LLM_API_KEY（支持阿里云百炼、火山引擎等）
```

### 3. 启动开发服务器

```bash
# 一键启动前端 + 后端（自动使用虚拟环境）
pnpm dev
```

就这么简单！自动启动：
- 后端 API: http://localhost:8000
- 前端: http://localhost:5173

## 项目结构

```
book-insight/
├── apps/
│   ├── web/              # React 前端
│   │   ├── src/
│   │   │   ├── pages/    # 页面组件
│   │   │   ├── services/ # API 调用
│   │   │   └── stores/   # 状态管理
│   │   └── ...
│   └── api/              # Python 后端
│       └── src/
│           ├── core/     # 核心逻辑
│           ├── ai/       # AI 任务
│           ├── rag/      # RAG 系统
│           ├── knowledge/# 知识模型
│           └── routers/  # API 路由
├── data/
│   ├── books/            # 书籍文件
│   ├── analysis/         # 分析结果
│   └── vector_store/     # 向量数据库
└── docs/
```

## API 端点

### 书籍管理
- `GET /api/books` - 列出所有书籍
- `POST /api/books/upload` - 上传书籍
- `GET /api/books/{book_id}` - 获取书籍详情
- `GET /api/books/{book_id}/chapters` - 获取章节列表
- `GET /api/books/{book_id}/chapters/{index}/content` - 获取章节内容
- `DELETE /api/books/{book_id}` - 删除书籍

### 分析
- `POST /api/analysis/{book_id}/chapters/{index}` - 分析单章
- `POST /api/analysis/{book_id}/batch` - 批量分析章节
- `POST /api/analysis/{book_id}/characters/search` - 搜索人物出现章节
- `GET /api/analysis/{book_id}/characters/stream` - 流式分析人物（SSE）
- `GET /api/analysis/{book_id}/characters/detailed` - 获取已分析人物列表

### RAG
- `POST /api/rag/{book_id}/index` - 创建向量索引
- `GET /api/rag/{book_id}/status` - 查看索引状态
- `POST /api/rag/{book_id}/query` - 向量检索
- `POST /api/rag/{book_id}/ask` - RAG 智能问答

### 系统
- `GET /api/health` - 健康检查

## 支持格式

- **TXT 文件**（当前唯一支持）
- 编码自动检测（UTF-8, GBK, GB2312）
- 章节识别：`第X章`、`Chapter X` 等模式

## 已知限制

1. 仅支持 TXT 格式（暂不支持 EPUB、PDF）
2. 章节检测依赖标准格式（如"第一章"）
3. 单机运行，无多用户支持
4. API 调用有成本（阿里云百炼）

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `LLM_API_KEY` | 是 | LLM 服务 API 密钥 |
| `LLM_BASE_URL` | 否 | OpenAI 兼容接口地址 |
| `CHAT_MODEL` | 否 | 对话模型名称 |
| `EMBEDDING_MODEL` | 否 | 向量模型名称 |

**支持的 LLM 服务**（OpenAI 兼容接口）：
- 阿里云百炼：qwen-plus + text-embedding-v3
- 火山引擎：doubao-pro-32k + doubao-embedding
- OpenAI：gpt-4o + text-embedding-3-small
- DeepSeek：deepseek-chat
