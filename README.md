# Book Insight

AI 驱动的个人书籍深度分析工具。

## 功能

- **RAG 问答**：基于原文的智能问答
- **人物分析**：自动提取人物、关系、性格
- **情节时间线**：关键事件脉络梳理
- **章节分析**：逐章 AI 分析，提取摘要、人物、事件

## 技术栈

- **前端**：React 18 + Vite + TailwindCSS + TanStack Query
- **后端**：Python FastAPI + LangChain + ChromaDB
- **AI**：Claude API + OpenAI Embeddings

## 快速开始

### 1. 首次安装

```bash
# 一键安装前端 + 后端
pnpm setup
```

### 2. 配置环境变量

```bash
cp apps/api/.env.example apps/api/.env
# 编辑 .env 填入 ANTHROPIC_API_KEY 和 OPENAI_API_KEY
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
- `GET /api/books/{id}/chapters` - 获取章节列表

### 分析
- `POST /api/analysis/{book_id}/chapters/{index}` - 分析单章
- `POST /api/analysis/{book_id}/characters/extract` - 提取人物

### RAG
- `POST /api/rag/{book_id}/index` - 创建索引
- `POST /api/rag/{book_id}/ask` - 智能问答
