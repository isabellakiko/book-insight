# LLM API 配置指南

> 如何配置不同的 LLM 服务提供商

**最后更新**: 2025-12-12

---

## 概述

Book Insight 使用 OpenAI 兼容接口，支持多种 LLM 服务提供商。只需修改环境变量即可切换。

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `LLM_API_KEY` | 是 | API 密钥 |
| `LLM_BASE_URL` | 否 | 接口地址（默认阿里云百炼） |
| `CHAT_MODEL` | 否 | 对话模型（默认 qwen-plus） |
| `EMBEDDING_MODEL` | 否 | 向量模型（默认 text-embedding-v3） |

---

## 配置方式

### 方式一：.env 文件（推荐）

编辑 `apps/api/.env`：

```bash
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CHAT_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

### 方式二：系统环境变量

添加到 `~/.zshrc` 或 `~/.bashrc`：

```bash
export LLM_API_KEY=sk-xxx
export LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
export CHAT_MODEL=qwen-plus
export EMBEDDING_MODEL=text-embedding-v3
```

生效：`source ~/.zshrc`

---

## 支持的 LLM 服务

### 阿里云百炼 (DashScope)

**控制台**: https://bailian.console.aliyun.com/

```bash
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CHAT_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v3
```

**可用模型**:
- 对话: `qwen-plus`, `qwen-turbo`, `qwen-max`
- 向量: `text-embedding-v3`, `text-embedding-v2`

**获取密钥**:
1. 登录阿里云控制台
2. 进入"百炼" → "API-KEY 管理"
3. 创建新密钥

---

### 火山引擎 (Volcengine)

**控制台**: https://console.volcengine.com/ark

```bash
LLM_API_KEY=xxx
LLM_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
CHAT_MODEL=doubao-pro-32k
EMBEDDING_MODEL=doubao-embedding
```

**可用模型**:
- 对话: `doubao-pro-32k`, `doubao-lite-32k`
- 向量: `doubao-embedding`

**获取密钥**:
1. 登录火山引擎控制台
2. 进入"方舟大模型" → "API Key 管理"
3. 创建访问密钥

**注意**: 火山引擎需要先在控制台开通模型访问权限。

---

### OpenAI

**控制台**: https://platform.openai.com/

```bash
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

**可用模型**:
- 对话: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- 向量: `text-embedding-3-small`, `text-embedding-3-large`

**获取密钥**:
1. 登录 OpenAI 平台
2. 进入 "API Keys"
3. 创建新密钥

**注意**: 需要有效的付费账户，国内访问可能需要代理。

---

### DeepSeek

**控制台**: https://platform.deepseek.com/

```bash
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.deepseek.com/v1
CHAT_MODEL=deepseek-chat
# EMBEDDING_MODEL 需配合其他服务使用
```

**可用模型**:
- 对话: `deepseek-chat`, `deepseek-coder`
- 向量: 暂不提供，需配合其他服务

**注意**: DeepSeek 暂无 Embedding 模型，RAG 功能需配合阿里云百炼或其他服务。

---

### 混合配置示例

使用 DeepSeek 对话 + 阿里云百炼向量：

```bash
# 对话模型用 DeepSeek
LLM_API_KEY=sk-deepseek-xxx
LLM_BASE_URL=https://api.deepseek.com/v1
CHAT_MODEL=deepseek-chat

# 向量模型需要单独配置（目前不支持混合配置）
# 暂时建议使用同一提供商的全套服务
```

---

## 验证配置

启动后端验证：

```bash
cd apps/api
source .venv/bin/activate
python -c "from src.config import settings; print(f'API Key: {settings.llm_api_key[:10]}...')"
```

启动服务测试：

```bash
pnpm dev:api

# 另一终端测试
curl http://localhost:8000/api/health
```

---

## 常见问题

### Q: 提示 "API key is invalid"

1. 检查密钥是否正确复制（无多余空格）
2. 确认密钥未过期或被禁用
3. 确认 `LLM_BASE_URL` 与密钥匹配

### Q: 提示 "Model not found"

1. 检查 `CHAT_MODEL` 或 `EMBEDDING_MODEL` 名称是否正确
2. 确认该模型在你的账户中已开通

### Q: 网络连接超时

1. 检查网络是否能访问对应服务
2. OpenAI 可能需要代理
3. 国内服务优先选择阿里云百炼或火山引擎

### Q: .env 文件不生效

1. 确保 `.env` 在 `apps/api/` 目录下
2. 重启后端服务
3. 检查是否有系统环境变量覆盖

---

## 成本参考

| 服务 | 对话模型 | 大致价格 |
|------|----------|----------|
| 阿里云百炼 | qwen-plus | ¥0.004/千tokens |
| 火山引擎 | doubao-pro-32k | ¥0.008/千tokens |
| OpenAI | gpt-4o | $0.005/千tokens |
| DeepSeek | deepseek-chat | ¥0.001/千tokens |

*价格可能变动，以官方为准*

---

## 相关文档

- [API 路由文档](../development/api/routers.md)
- [AI 任务文档](../development/api/ai-tasks.md)
- [数据存储文档](../development/api/data-storage.md)
