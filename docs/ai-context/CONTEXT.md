# 项目上下文（AI 快速恢复）

> AI 协作记忆文件 - 快速恢复项目上下文，立即开始工作

**最后更新**: 2025-12-09 12:45
**项目阶段**: MVP 开发
**当前状态**: 核心功能已完成，待测试优化

---

## TL;DR（30秒速览）

**项目名称**: Book Insight
**项目性质**: 个人 AI 书籍深度分析工具
**技术栈**: React 18 + FastAPI + 阿里云百炼(qwen-plus)
**核心特点**:
- RAG 问答：基于原文的智能问答
- 人物分析：自动提取人物、关系、性格
- 章节分析：逐章 AI 分析，提取摘要、人物、事件

**开发进度**: MVP 核心功能已实现
**下一步**: 测试优化 + UI 美化

---

## 项目背景与动机

### 为什么做这个项目？

阅读长篇小说（尤其是网络小说）时常遇到的痛点：
1. **人物记忆困难** - 角色众多，读到后面忘了前面的人物关系
2. **情节回顾困难** - 想找某个情节在哪一章，只能手动翻找
3. **深度理解不足** - 缺乏对主题、伏笔、人物弧光的系统性分析

### 解决方案

用 AI 增强阅读体验：
- **不是替代阅读**，而是阅读后的辅助工具
- **基于原文**，RAG 确保回答有据可查
- **渐进式分析**，可以只分析感兴趣的章节

### 目标用户

**我自己**（个人项目）- 用于分析收藏的网络小说和文学作品

### 支持的书籍格式

- **TXT 文件**（当前唯一支持格式）
- 编码：自动检测（UTF-8, GBK, GB2312 等）
- 章节检测：正则匹配（第X章、Chapter X 等模式）

---

## 项目本质

这是一个 **个人书籍深度分析工具**，主要功能：

- **RAG 智能问答**：上传书籍后，基于原文内容进行问答
- **人物图谱分析**：自动识别书中人物及其关系
- **章节深度分析**：逐章提取摘要、关键事件、人物动态
- **情节时间线**：梳理故事主线和关键事件脉络

**设计理念**:
- 个人使用，简洁优先
- AI 增强阅读体验，不替代阅读
- 离线优先，数据本地存储

---

## 技术决策说明

### 为什么选择这些技术？

| 选择 | 原因 |
|------|------|
| **FastAPI** (非 Spring Boot) | AI/ML 项目用 Python 生态更方便，LangChain、ChromaDB 都是 Python 原生 |
| **ChromaDB** (非 Pinecone) | 本地部署，无需云服务，数据隐私 |
| **阿里云百炼** | qwen-plus 模型，OpenAI 兼容接口，国内访问稳定 |
| **百炼 Embeddings** | text-embedding-v3，配合 qwen 使用 |
| **React + Vite** | 快速开发，热更新体验好 |
| **Zustand** (非 Redux) | 轻量，适合小型项目 |

### 已知限制

1. **仅支持 TXT** - 暂不支持 EPUB、PDF
2. **章节检测依赖格式** - 需要标准的"第X章"格式
3. **单机运行** - 无多用户支持
4. **API 成本** - 百炼 API 调用有费用

---

## 当前开发状态

### ✅ 已完成

- 项目架构搭建（Monorepo + pnpm）
- 后端 FastAPI 框架 + 路由
- 前端 React 页面框架
- RAG 系统基础实现
- AI 任务模块（章节分析、人物提取）

### 🚧 进行中

- 功能联调测试

### 📋 待开始

- UI 美化（TailwindCSS 样式优化）
- 错误处理完善
- 性能优化

---

## 技术栈

### 前端（apps/web/）
- **框架**: React 18 + Vite 5
- **样式**: TailwindCSS
- **状态管理**: Zustand
- **数据获取**: TanStack Query
- **包管理**: pnpm

### 后端（apps/api/）
- **框架**: FastAPI
- **语言**: Python 3.11+
- **AI**: 阿里云百炼 (qwen-plus) + 百炼 Embeddings (text-embedding-v3)
- **RAG**: LangChain + ChromaDB
- **数据存储**: JSON 文件 + ChromaDB 向量库
- **虚拟环境**: .venv（使用 pip）

### 启动命令
```bash
# 一键启动（推荐）
pnpm dev

# 分别启动
pnpm dev:web   # 前端 :5173
pnpm dev:api   # 后端 :8000
```

---

## 项目结构

```
book-insight/
├── apps/
│   ├── web/                  # React 前端
│   │   └── src/
│   │       ├── pages/        # 5 个页面组件
│   │       ├── stores/       # Zustand 状态
│   │       └── services/     # API 调用
│   └── api/                  # Python 后端
│       └── src/
│           ├── routers/      # API 路由 (books, analysis, rag)
│           ├── ai/           # AI 任务 (chapter, character)
│           ├── rag/          # RAG 系统 (store, retriever)
│           ├── knowledge/    # 知识模型
│           └── core/         # 核心逻辑
├── data/
│   ├── books/                # 书籍原始文件 (.txt)
│   │   └── {book_id}/
│   │       ├── meta.json     # 书籍元信息
│   │       └── chapters/     # 章节独立存储
│   │           ├── 0001.json
│   │           └── ...
│   ├── analysis/             # 分析结果
│   │   └── {book_id}/
│   │       └── characters/   # 人物分析（分层存储）
│   │           └── {name}/
│   │               ├── profile.json
│   │               └── appearances/
│   └── vector_store/         # ChromaDB（暂缓）
└── docs/
    ├── ai-context/           # AI 协作文档
    └── development/          # 开发文档
```

---

## API 端点概览

| 模块 | 端点 | 描述 |
|------|------|------|
| Books | `GET /api/books` | 列出所有书籍 |
| Books | `POST /api/books/upload` | 上传书籍 |
| Books | `GET /api/books/{id}/chapters` | 获取章节列表 |
| Analysis | `POST /api/analysis/{book_id}/chapters/{index}` | 分析单章 |
| Analysis | `POST /api/analysis/{book_id}/characters/extract` | 提取人物 |
| RAG | `POST /api/rag/{book_id}/index` | 创建向量索引 |
| RAG | `POST /api/rag/{book_id}/ask` | 智能问答 |

---

## 协作偏好

### 开发节奏
- ✅ **每次只执行一步** - 不要一次性做太多改动
- ✅ **说明原因和目的** - 每一步都要解释为什么
- ✅ **等待确认** - 完成一步后等待用户确认

### 代码风格
- ✅ Python: 遵循 PEP 8，使用 type hints
- ✅ React: 函数组件 + Hooks，避免 class 组件
- ✅ 简洁优先，避免过度工程化
- ❌ 不添加未请求的功能

### Git 提交规范
```
<type>(<scope>): <subject>

type: feat | fix | docs | refactor | perf | test | chore
```

---

## 快速导航

- [当前进度](CURRENT.md)
- [API 文档](../development/api/routers.md)
- [页面文档](../development/web/pages.md)

---

## 快速恢复上下文

```bash
/start              # 快速启动（默认）
/start --full       # 完整启动（首次使用）
/start --api        # API 开发模式
/start --web        # 前端开发模式
```

---

**Token 效率**: ~2200 tokens
**更新频率**: 每周或重大变更时
