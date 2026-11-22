# AI 私厨 · 多模态食谱助手

输入手头的食材或上传一张食材照片，获取做法建议。用户可以在同一会话追问和替换食材，页面会逐段显示回答。

## 一条完整的演示

1. 输入「我有番茄、鸡蛋和一碗剩米饭，只有 20 分钟，可以做什么？」
2. 等页面开始逐段显示回复，再追问「如果没有鸡蛋，可以换成豆腐吗？」
3. 配好 OSS 后，在页面上传食材照片，测试同样的对话流程。

## 实现

- **模型和工具**。通过 LangChain 调用通义千问多模态模型。Agent 接收文字和图片 URL，并可用 Tavily 搜索菜谱。
- **流式回复**。FastAPI 的 `StreamingResponse` 把生成片段直接交给浏览器，页面使用 ReadableStream 逐段读取。
- **会话状态**。LangGraph 的 SQLite checkpointer 按 `thread_id` 保存上下文，并提供查询和清空接口。
- **图片直传**。FastAPI 签发有时效的 OSS PUT URL，浏览器上传文件后，把图片 URL 用于后续对话。

## 本地运行

需要 Python 3.14、uv、DashScope 和 Tavily 密钥。先试文字问答时，只填 `DASHSCOPE_API_KEY` 与 `TAVILY_API_KEY`。

```bash
cp .env.example .env
uv sync --locked
uv run --locked uvicorn app.main:app --host 127.0.0.1 --port 8001
```

打开 [聊天页面](http://localhost:8001) 或 [Swagger](http://localhost:8001/docs)。首次启动会创建本地 SQLite 文件。

启用图片上传时，填入 `OSS_BUCKET`、`OSS_REGION`、`OSS_ENDPOINT` 和有签名权限的 OSS 凭证。桶的 CORS 需允许演示页面来源发起 PUT 请求，图片 URL 需能被模型读取。请使用演示图片。上传签名和会话接口按本地演示设计。

## 接口

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| POST | `/api/v1/chat/stream` | 接收 `message`、`thread_id` 与可选的 `image_url`，返回文字流。 |
| GET | `/api/v1/chat/messages` | 按 `thread_id` 查询消息。 |
| DELETE | `/api/v1/chat/messages` | 按 `thread_id` 清空消息。 |
| GET | `/api/v1/oss/presign` | 按 `filename` 获取签名 URL 和请求类型。 |

项目源于 FastAPI + LangChain 课程实践。`app/static/` 是配套前端的静态构建产物，主要展示内容是 Agent 和 FastAPI 后端。
