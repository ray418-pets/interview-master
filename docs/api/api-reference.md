# AI 智能面试助手 MVP — 后端 API 文档

| 项目 | 内容 |
|------|------|
| 版本 | v1.0 |
| 日期 | 2026-09-17 |
| 依据 | docs/tests/2026-09-17-backend-api-test-report.md |
| 协议 | REST / JSON（HTTP） |
| Base URL | `/api` |
| 认证方式 | `Authorization: Bearer <token>` |

---

## 1. 概述

后端采用 FastAPI 实现，前后端分离。所有接口统一返回 `{ code, message, data }` 结构，
`code = 0` 表示成功，非 0 表示业务或系统错误。

除「注册 / 登录」两个接口外，其余接口均需认证：请求头携带
`Authorization: Bearer <token>`，token 由登录或注册接口返回。

---

## 2. 统一响应结构

### 2.1 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { }
}
```

`data` 为具体业务数据，可能为对象或数组，各接口不同。

### 2.2 错误响应

```json
{
  "code": 40001,
  "message": "无效的岗位方向"
}
```

HTTP 状态码与业务 code 共同表达错误类型（见 [错误码表](#5-错误码表)）。

---

## 3. 认证

| 项目 | 说明 |
|------|------|
| 头字段 | `Authorization` |
| 格式 | `Bearer <token>` |
| token 来源 | `POST /api/auth/register` 或 `POST /api/auth/login` 的返回 |

- 缺少或非法 token → `401` + `code=40100`（缺少认证信息）。
- token 无效或过期 → `401` + `code=40101`（登录已失效）。

---

## 4. 枚举定义

### 4.1 岗位方向 `direction`

| 值 | 含义 |
|----|------|
| `technical_frontend` | 技术-前端 |
| `technical_backend` | 技术-后端 |
| `technical_algorithm` | 技术-算法 |
| `product` | 产品 |
| `operations` | 运营 |
| `general` | 通用 |

### 4.2 题型 `type`

| 值 | 含义 |
|----|------|
| `self_introduction` | 自我介绍 |
| `technical` | 技术题 |
| `behavioral` | 行为题 |
| `project_experience` | 项目经验题 |
| `open_ended` | 开放题 |

### 4.3 难度 `difficulty`（题库内部使用）

| 值 | 含义 |
|----|------|
| `easy` | 简单 |
| `medium` | 中等 |
| `hard` | 困难 |

### 4.4 面试会话状态 `status`

| 值 | 含义 |
|----|------|
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `finished` | 已结束（提前结束） |

---

## 5. 错误码表

| HTTP 状态 | code | 说明 |
|-----------|------|------|
| 400 | `40000` | 请求参数校验失败（Pydantic / FastAPI） |
| 400 | `40001` | 无效的岗位方向 |
| 400 | `40002` | 无效的题型 |
| 400 | `40003` | 无效的难度 |
| 400 | `40004` | 题目数量不足（题库该组合题目不够） |
| 400 | `40005` | 题目总数须在 1-20 之间 |
| 400 | `40006` | 题型组合不能为空 |
| 400 | `40007` | 每环节题目数量至少为 1 |
| 400 | `40008` | 必须提供模板或自定义配置 |
| 401 | `40100` | 缺少认证信息 |
| 401 | `40101` | 用户名或密码错误 / 登录已失效 |
| 403 | `40301` | 无权访问该会话（跨用户操作） |
| 404 | `40401` | 会话不存在 |
| 404 | `40402` | 模板不存在 |
| 409 | `40901` | 用户名已被占用 |
| 409 | `40902` | 会话已结束，无法继续作答 / 操作 |
| 409 | `40903` | 面试尚未完成，暂无报告 |
| 500 | `50000` | 服务器内部错误 |

---

## 6. 接口列表

### 6.1 注册

**`POST /api/auth/register`**（公开，无需认证）

请求体：

```json
{
  "username": "alice",
  "password": "secret123"
}
```

| 字段 | 类型 | 约束 |
|------|------|------|
| username | string | 3–64 字符 |
| password | string | 6–128 字符 |

成功响应（`data`）：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "…",
    "user": { "id": 1, "username": "alice" }
  }
}
```

错误：用户名已存在 → `409` + `code=40901`；参数不合法 → `400` + `code=40000`。

---

### 6.2 登录

**`POST /api/auth/login`**（公开，无需认证）

请求体：

```json
{
  "username": "alice",
  "password": "secret123"
}
```

成功响应同「注册」，返回新签发的 `token` 与用户信息。

错误：用户名或密码错误 → `401` + `code=40101`。

---

### 6.3 获取预设模板列表

**`GET /api/templates`**（需认证）

成功响应（`data` 为数组）：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "后端开发面试",
      "direction": "technical_backend",
      "segments": [
        { "type": "self_introduction", "count": 1 },
        { "type": "technical", "count": 4 },
        { "type": "behavioral", "count": 2 },
        { "type": "open_ended", "count": 1 }
      ]
    }
  ]
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| id | 模板主键，可用于创建会话 |
| name | 模板名称 |
| direction | 岗位方向（枚举） |
| segments | 环节列表，每项为 `{ type, count }`，`count` 为该题型题目数 |

---

### 6.4 创建面试会话

**`POST /api/interviews`**（需认证）

请求体二选一：

**方式 A：按预设模板**

```json
{ "template_id": 1 }
```

**方式 B：自定义配置**

```json
{
  "direction": "general",
  "segments": [
    { "type": "self_introduction", "count": 1 },
    { "type": "behavioral", "count": 2 }
  ]
}
```

| 字段 | 类型 | 约束 |
|------|------|------|
| template_id | int \| null | 与自定义配置二选一 |
| direction | string \| null | 岗位方向枚举 |
| segments | array \| null | 环节列表，非空；每个 `type` 为题型枚举、`count ≥ 1`；总数 1–20 |

成功响应（`data`）：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "session_id": 42,
    "direction": "general",
    "total_questions": 3,
    "status": "in_progress",
    "current_question": {
      "round_index": 0,
      "content": "请做一个简短的自我介绍……"
    }
  }
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| session_id | 会话主键，后续作答 / 结束 / 报告均使用 |
| total_questions | 题目总数（各环节 count 之和） |
| current_question | 第一题，`round_index` 从 0 起 |
| content | 题干 |

错误：配置非法（方向 / 题型 / 数量 / 未提供配置）→ `400`；模板不存在 → `404` + `code=40402`；
题目数量不足 → `400` + `code=40004`。

---

### 6.5 提交当前题回答

**`POST /api/interviews/{session_id}/answer`**（需认证）

请求体：

```json
{ "answer": "这是我的回答内容……" }
```

| 字段 | 类型 | 约束 |
|------|------|------|
| answer | string | 非空；长度 ≥ 10 个字符才计为有效作答 |

成功响应（`data`）：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "feedback": "回答覆盖了部分要点（……），建议补充：……。",
    "is_finished": false,
    "next_question": {
      "round_index": 1,
      "content": "下一题题干……"
    }
  }
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| feedback | 本题点评（规则引擎生成） |
| is_finished | 是否已完成全部题目 |
| next_question | 下一题；`is_finished=true` 时为 `null` |

行为说明：

- 非最后一题：返回点评 + 下一题，会话保持 `in_progress`。
- 最后一题：返回点评，`is_finished=true`，会话状态变为 `completed`。
- 回答为空或长度 < 10 字符：不写记录、不推进轮次，返回固定提示
  `feedback="回答过短，请至少输入 10 个字符后再提交。"`，`is_finished=false`，
  `next_question` 为当前题。

错误：会话不存在 → `404` + `code=40401`；跨用户 → `403` + `code=40301`；
会话已结束（`completed` / `finished`）→ `409` + `code=40902`。

---

### 6.6 提前结束面试

**`POST /api/interviews/{session_id}/finish`**（需认证）

无请求体。

成功响应（`data`）：

```json
{
  "code": 0,
  "message": "success",
  "data": { "session_id": 42, "status": "finished" }
}
```

行为说明：将会话状态由 `in_progress` 置为 `finished`，已作答题目保留并纳入报告。

错误：会话不存在 → `404`；跨用户 → `403`；会话已结束 → `409` + `code=40902`。

---

### 6.7 获取历史会话列表

**`GET /api/interviews`**（需认证）

成功响应（`data` 为数组，按创建时间倒序）：

```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 42,
      "direction": "general",
      "total_questions": 3,
      "started_at": "2026-09-17T03:00:00+00:00",
      "status": "finished"
    }
  ]
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| id | 会话主键 |
| direction | 岗位方向（枚举） |
| total_questions | 题目总数 |
| started_at | 开始时间（ISO 8601） |
| status | 会话状态（枚举） |

说明：仅返回当前登录用户自己的会话，历史记录按用户隔离。

---

### 6.8 获取评估报告

**`GET /api/reports/{session_id}`**（需认证）

成功响应（`data`）：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "session_id": 42,
    "direction": "general",
    "status": "finished",
    "overall_evaluation": "本次面试仅完成 1/3 题，建议后续多加练习。",
    "improvement_suggestions": "建议加强练习以下题型：行为题；同时多复盘已答题目，巩固知识点。",
    "questions": [
      {
        "question_content": "题干……",
        "user_answer": "我的回答……",
        "feedback": "AI 点评……"
      }
    ]
  }
}
```

字段说明：

| 字段 | 说明 |
|------|------|
| overall_evaluation | 总体评价（基于完成度的规则模板） |
| improvement_suggestions | 改进建议（汇总未作答题型 + 通用建议） |
| questions | 逐题点评，仅含已作答题目，按轮次升序 |

行为说明：

- 报告在首次查询时惰性生成并落库，重复查询幂等（不重复生成）。
- `in_progress` 会话查询报告 → `409` + `code=40903`。
- 提前结束（`finished`）的报告仅包含已作答题目。

错误：会话不存在 → `404` + `code=40401`；跨用户 → `403` + `code=40301`；
面试尚未完成 → `409` + `code=40903`。

---

## 7. 完整流程示例

```text
1. POST /api/auth/register          → 获得 token
2. GET  /api/templates              → 获取预设模板（可选）
3. POST /api/interviews             → 创建会话，返回第一题
4. POST /api/interviews/{id}/answer → 逐题作答，返回点评与下一题
   （可选）POST /api/interviews/{id}/finish → 提前结束
5. 全部答完后 GET /api/reports/{id} → 查看评估报告
6. GET  /api/interviews             → 查看历史记录
```

---

## 8. 说明

- 题库与抽题能力由后端 `questions` / `engine` 模块内部完成，MVP 不单独对外暴露题库接口。
- 点评与报告为规则模拟（基于题目参考要点关键词匹配），非真实大模型，结果可复现。
- 会话与报告归属以登录用户 `user_id` 判定，历史记录严格按用户隔离。
