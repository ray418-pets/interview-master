# AI 智能面试助手 — 前端调用 API 文档

> 本文档面向前端开发者，按「提交方式 / URL / 参数 / 响应 / 示例」组织，可直接用于前端联调。

| 项目 | 内容 |
|------|------|
| 协议 | HTTP + JSON |
| Base URL | `/api` |
| 认证 | 请求头 `Authorization: Bearer <token>` |
| 字符编码 | UTF-8 |
| Content-Type | `application/json` |

---

## 1. 调用约定

### 1.1 统一响应结构

所有接口返回统一 JSON 结构：

```json
{
  "code": 0,
  "message": "success",
  "data": { }
}
```

- `code = 0`：成功；`code ≠ 0`：失败（具体含义见 [错误码表](#6-错误码表)）。
- `data`：成功时的业务数据，类型随接口而异（对象 / 数组 / null）。
- 失败时通常没有 `data` 字段。

### 1.2 认证方式

除「注册」「登录」外，所有接口都要求请求头携带：

```
Authorization: Bearer <token>
```

- `token` 由注册 / 登录接口返回。
- 未携带或非法 → `401` + `code=40100`。
- token 失效 → `401` + `code=40101`。

### 1.3 前端封装参考（fetch）

```js
const API_BASE = '/api';

async function request(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('auth_token');
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const resp = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (resp.status === 401) {
    // 登录失效：清 token，跳登录页
    localStorage.removeItem('auth_token');
    location.href = 'login.html';
    throw new Error('登录已失效，请重新登录');
  }
  const data = await resp.json();
  if (data.code !== 0) throw new Error(data.message || '请求失败');
  return data.data;   // 直接返回业务数据
}
```

> 本封装已在 `frontend/js/api.js` 中实现，可直接复用。

---

## 2. 接口总览

| # | 提交方式 | URL | 说明 | 认证 |
|---|---------|-----|------|------|
| 1 | POST | `/api/auth/register` | 注册 | 否 |
| 2 | POST | `/api/auth/login` | 登录 | 否 |
| 3 | GET | `/api/templates` | 获取预设模板列表 | 是 |
| 4 | POST | `/api/interviews` | 创建面试会话 | 是 |
| 5 | POST | `/api/interviews/{session_id}/answer` | 提交当前题回答 | 是 |
| 6 | POST | `/api/interviews/{session_id}/finish` | 提前结束面试 | 是 |
| 7 | GET | `/api/interviews` | 获取历史会话列表 | 是 |
| 8 | GET | `/api/reports/{session_id}` | 获取评估报告 | 是 |

---

## 3. 认证接口

### 3.1 注册

| 项 | 值 |
|----|----|
| 提交方式 | `POST` |
| URL | `/api/auth/register` |
| 是否需要认证 | 否 |

**请求参数（Body）**

| 参数 | 类型 | 必填 | 约束 | 示例 |
|------|------|------|------|------|
| username | string | 是 | 3–64 字符 | `"alice"` |
| password | string | 是 | 6–128 字符 | `"secret123"` |

**请求示例**

```http
POST /api/auth/register HTTP/1.1
Content-Type: application/json

{
  "username": "alice",
  "password": "secret123"
}
```

**响应数据（data）**

| 字段 | 类型 | 说明 |
|------|------|------|
| token | string | 登录凭证，后续请求携带 |
| user.id | int | 用户主键 |
| user.username | string | 用户名 |

**响应示例**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "8f2cYh…",
    "user": { "id": 1, "username": "alice" }
  }
}
```

**JS 调用**

```js
const { token, user } = await register('alice', 'secret123');
```

**错误**

| 状态码 | code | 说明 |
|--------|------|------|
| 409 | 40901 | 用户名已被占用 |
| 400 | 40000 | 参数不合法（长度不满足） |

---

### 3.2 登录

| 项 | 值 |
|----|----|
| 提交方式 | `POST` |
| URL | `/api/auth/login` |
| 是否需要认证 | 否 |

**请求参数（Body）**

| 参数 | 类型 | 必填 | 约束 | 示例 |
|------|------|------|------|------|
| username | string | 是 | 无 | `"alice"` |
| password | string | 是 | 无 | `"secret123"` |

**请求示例**

```http
POST /api/auth/login HTTP/1.1
Content-Type: application/json

{
  "username": "alice",
  "password": "secret123"
}
```

**响应数据（data）**：同「注册」，返回新签发的 `token` 与用户信息。

**响应示例**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "token": "9xQk…",
    "user": { "id": 1, "username": "alice" }
  }
}
```

**JS 调用**

```js
const { token, user } = await login('alice', 'secret123');
```

**错误**

| 状态码 | code | 说明 |
|--------|------|------|
| 401 | 40101 | 用户名或密码错误 |

---

## 4. 模板接口

### 4.1 获取预设模板列表

| 项 | 值 |
|----|----|
| 提交方式 | `GET` |
| URL | `/api/templates` |
| 是否需要认证 | 是 |

**请求参数**：无（Body / Query 均无）。

**请求示例**

```http
GET /api/templates HTTP/1.1
Authorization: Bearer 8f2cYh…
```

**响应数据（data，数组）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 模板主键，创建会话时作为 `template_id` 使用 |
| name | string | 模板名称 |
| direction | string | 岗位方向（枚举，见 [枚举](#5-枚举定义)） |
| segments | array | 环节列表 |
| segments[].type | string | 题型（枚举） |
| segments[].count | int | 该题型题目数 |

**响应示例**

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

**JS 调用**

```js
const templates = await getTemplates();
// templates[0].id → 用于创建会话
```

---

## 5. 面试接口

### 5.1 创建面试会话

| 项 | 值 |
|----|----|
| 提交方式 | `POST` |
| URL | `/api/interviews` |
| 是否需要认证 | 是 |

**请求参数（Body，二选一）**

方式 A —— 按预设模板：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| template_id | int | 是（A） | 预设模板 id | `1` |

方式 B —— 自定义配置：

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| direction | string | 是（B） | 岗位方向枚举 | `"general"` |
| segments | array | 是（B） | 环节列表，非空 | 见下 |
| segments[].type | string | 是 | 题型枚举 | `"behavioral"` |
| segments[].count | int | 是 | 该题型题数，≥ 1；总数 1–20 | `2` |

> `template_id` 与 `direction + segments` 二者必须提供其一。

**请求示例（方式 A）**

```http
POST /api/interviews HTTP/1.1
Authorization: Bearer 8f2cYh…
Content-Type: application/json

{ "template_id": 1 }
```

**请求示例（方式 B）**

```http
POST /api/interviews HTTP/1.1
Authorization: Bearer 8f2cYh…
Content-Type: application/json

{
  "direction": "general",
  "segments": [
    { "type": "self_introduction", "count": 1 },
    { "type": "behavioral", "count": 2 }
  ]
}
```

**响应数据（data）**

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话主键，后续作答 / 结束 / 报告均使用 |
| direction | string | 岗位方向 |
| total_questions | int | 题目总数 |
| status | string | 会话状态（初始为 `in_progress`） |
| current_question.round_index | int | 当前题轮次（从 0 起） |
| current_question.content | string | 第一题题干 |

**响应示例**

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

**JS 调用**

```js
// 按模板
const data = await createInterview({ template_id: 1 });
// 或自定义
const data = await createInterview({
  direction: 'general',
  segments: [
    { type: 'self_introduction', count: 1 },
    { type: 'behavioral', count: 2 },
  ],
});
// 跳转面试页
location.href = `interview.html?session_id=${data.session_id}`;
```

**错误**

| 状态码 | code | 说明 |
|--------|------|------|
| 400 | 40001 | 无效的岗位方向 |
| 400 | 40002 | 无效的题型 |
| 400 | 40005 | 题目总数须在 1-20 之间 |
| 400 | 40006 | 题型组合不能为空 |
| 400 | 40007 | 每环节题目数量至少为 1 |
| 400 | 40008 | 必须提供模板或自定义配置 |
| 400 | 40004 | 题目数量不足 |
| 404 | 40402 | 模板不存在 |

---

### 5.2 提交当前题回答

| 项 | 值 |
|----|----|
| 提交方式 | `POST` |
| URL | `/api/interviews/{session_id}/answer` |
| 是否需要认证 | 是 |

**路径参数（Path）**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话主键 |

**请求参数（Body）**

| 参数 | 类型 | 必填 | 约束 | 示例 |
|------|------|------|------|------|
| answer | string | 是 | 长度 ≥ 10 字符才计为有效作答 | `"我的回答……"` |

**请求示例**

```http
POST /api/interviews/42/answer HTTP/1.1
Authorization: Bearer 8f2cYh…
Content-Type: application/json

{ "answer": "这是我的回答内容，包含关键要点……" }
```

**响应数据（data）**

| 字段 | 类型 | 说明 |
|------|------|------|
| feedback | string | 本题点评 |
| is_finished | bool | 是否已完成全部题目 |
| next_question | object \| null | 下一题；`is_finished=true` 时为 `null` |
| next_question.round_index | int | 下一题轮次 |
| next_question.content | string | 下一题题干 |

**响应示例（非最后一题）**

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

**响应示例（最后一题，面试完成）**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "feedback": "回答覆盖了全部参考要点（……），回答较完整。",
    "is_finished": true,
    "next_question": null
  }
}
```

**响应示例（回答过短，被拦截）**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "feedback": "回答过短，请至少输入 10 个字符后再提交。",
    "is_finished": false,
    "next_question": {
      "round_index": 0,
      "content": "当前题题干……"
    }
  }
}
```

> 注意：过短回答的 `next_question.round_index` 与当前题相同（即不推进轮次）。

**JS 调用**

```js
const data = await submitAnswer(42, answer);
if (data.is_finished) {
  location.href = `report.html?session_id=${42}`;
} else if (data.next_question.round_index === currentRound) {
  // 过短回答被拦截，提示 data.feedback，不推进
} else {
  // 展示 data.feedback，进入下一题 data.next_question
}
```

**错误**

| 状态码 | code | 说明 |
|--------|------|------|
| 404 | 40401 | 会话不存在 |
| 403 | 40301 | 无权访问该会话（跨用户） |
| 409 | 40902 | 会话已结束，无法继续作答 |

---

### 5.3 提前结束面试

| 项 | 值 |
|----|----|
| 提交方式 | `POST` |
| URL | `/api/interviews/{session_id}/finish` |
| 是否需要认证 | 是 |

**路径参数（Path）**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话主键 |

**请求参数**：无 Body。

**请求示例**

```http
POST /api/interviews/42/finish HTTP/1.1
Authorization: Bearer 8f2cYh…
```

**响应数据（data）**

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话主键 |
| status | string | 结束后的状态（`finished`） |

**响应示例**

```json
{
  "code": 0,
  "message": "success",
  "data": { "session_id": 42, "status": "finished" }
}
```

**JS 调用**

```js
await finishInterview(42);
location.href = `report.html?session_id=${42}`;
```

**错误**

| 状态码 | code | 说明 |
|--------|------|------|
| 404 | 40401 | 会话不存在 |
| 403 | 40301 | 无权访问该会话（跨用户） |
| 409 | 40902 | 会话已结束，无法操作 |

---

### 5.4 获取历史会话列表

| 项 | 值 |
|----|----|
| 提交方式 | `GET` |
| URL | `/api/interviews` |
| 是否需要认证 | 是 |

**请求参数**：无。

**请求示例**

```http
GET /api/interviews HTTP/1.1
Authorization: Bearer 8f2cYh…
```

**响应数据（data，数组，按创建时间倒序）**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 会话主键 |
| direction | string | 岗位方向 |
| total_questions | int | 题目总数 |
| started_at | string | 开始时间（ISO 8601） |
| status | string | 会话状态 |

**响应示例**

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

**JS 调用**

```js
const sessions = await listInterviews();
// sessions 仅含当前登录用户自己的记录
```

---

## 6. 报告接口

### 6.1 获取评估报告

| 项 | 值 |
|----|----|
| 提交方式 | `GET` |
| URL | `/api/reports/{session_id}` |
| 是否需要认证 | 是 |

**路径参数（Path）**

| 参数 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话主键 |

**请求参数**：无。

**请求示例**

```http
GET /api/reports/42 HTTP/1.1
Authorization: Bearer 8f2cYh…
```

**响应数据（data）**

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | int | 会话主键 |
| direction | string | 岗位方向 |
| status | string | 会话状态 |
| overall_evaluation | string | 总体评价 |
| improvement_suggestions | string | 改进建议 |
| questions | array | 逐题点评，仅含已作答题目，按轮次升序 |
| questions[].question_content | string | 题干 |
| questions[].user_answer | string | 我的回答 |
| questions[].feedback | string | AI 点评 |

**响应示例**

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
        "question_content": "请做一个简短的自我介绍……",
        "user_answer": "我的回答内容……",
        "feedback": "回答覆盖了部分要点……"
      }
    ]
  }
}
```

**JS 调用**

```js
const report = await getReport(42);
// report.questions 渲染逐题点评
```

**错误**

| 状态码 | code | 说明 |
|--------|------|------|
| 404 | 40401 | 会话不存在 |
| 403 | 40301 | 无权访问该会话（跨用户） |
| 409 | 40903 | 面试尚未完成，暂无报告 |

---

## 7. 枚举定义

### 7.1 岗位方向 `direction`

| 值 | 含义 |
|----|------|
| `technical_frontend` | 技术-前端 |
| `technical_backend` | 技术-后端 |
| `technical_algorithm` | 技术-算法 |
| `product` | 产品 |
| `operations` | 运营 |
| `general` | 通用 |

### 7.2 题型 `type`

| 值 | 含义 |
|----|------|
| `self_introduction` | 自我介绍 |
| `technical` | 技术题 |
| `behavioral` | 行为题 |
| `project_experience` | 项目经验题 |
| `open_ended` | 开放题 |

### 7.3 会话状态 `status`

| 值 | 含义 |
|----|------|
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `finished` | 已结束（提前结束） |

---

## 8. 错误码表

| HTTP 状态 | code | 说明 |
|-----------|------|------|
| 400 | 40000 | 请求参数校验失败 |
| 400 | 40001 | 无效的岗位方向 |
| 400 | 40002 | 无效的题型 |
| 400 | 40003 | 无效的难度 |
| 400 | 40004 | 题目数量不足 |
| 400 | 40005 | 题目总数须在 1-20 之间 |
| 400 | 40006 | 题型组合不能为空 |
| 400 | 40007 | 每环节题目数量至少为 1 |
| 400 | 40008 | 必须提供模板或自定义配置 |
| 401 | 40100 | 缺少认证信息 |
| 401 | 40101 | 用户名或密码错误 / 登录已失效 |
| 403 | 40301 | 无权访问该会话 |
| 404 | 40401 | 会话不存在 |
| 404 | 40402 | 模板不存在 |
| 409 | 40901 | 用户名已被占用 |
| 409 | 40902 | 会话已结束，无法继续作答 / 操作 |
| 409 | 40903 | 面试尚未完成，暂无报告 |
| 500 | 50000 | 服务器内部错误 |

---

## 9. 完整流程示例

```js
// 1. 注册 / 登录
const { token, user } = await login('alice', 'secret123');
setAuth(token, user.username);

// 2. 获取模板（可选）
const templates = await getTemplates();

// 3. 创建会话（按模板或自定义）
const session = await createInterview({ template_id: templates[0].id });
// 或：await createInterview({ direction: 'general', segments: [{ type: 'behavioral', count: 2 }] });

// 4. 逐题作答
let res = await submitAnswer(session.session_id, '第一题的回答……');
while (!res.is_finished) {
  res = await submitAnswer(session.session_id, '下一题的回答……');
}

// 5. 查看报告
const report = await getReport(session.session_id);

// 6. 历史列表
const history = await listInterviews();
```
