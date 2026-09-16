# interviews 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | interviews（面试会话） |
| 状态 | 待评审 |
| 实现顺序 | 第 5 个模块（依赖 core、questions、engine、templates） |

---

## 1. 模块目标

提供面试会话的完整生命周期管理：创建会话并生成题目序列、逐题对话流转、提前结束、历史记录列表。这是打通「配置 → 面试」核心链路的关键模块，包含会话状态机与问答记录。

## 2. 职责边界

**做什么：**

- 创建面试会话：接收配置，委托 engine 抽题，生成题目序列与问答记录，返回第一题。
- 逐题流转：接收当前题回答，委托 engine 生成点评，推进到下一题或结束。
- 空 / 过短回答拦截：给出固定提示，不推进。
- 提前结束：将进行中的会话置为「已结束」。
- 历史列表：按匿名标识查询会话列表（时间倒序）。
- 会话状态机维护（进行中 / 已完成 / 已结束）。

**不做什么：**

- 不实现抽题与点评算法（由 engine 模块完成）。
- 不生成评估报告（由 reports 模块完成）。
- 不校验配置合法性（由 templates 模块完成，interviews 仅消费规范化配置）。

## 3. 依赖关系

- **依赖**：core（数据库会话）、users（匿名标识）、questions（题目实体）、engine（抽题 + 点评）、templates（配置解析）。
- **被依赖**：reports（读取会话与问答记录生成报告）。

## 4. 文件结构

```
backend/app/interviews/
  models.py        # InterviewSession、InterviewRecord 数据模型
  schemas.py       # 创建 / 回答 / 结束 / 列表的请求与响应模型
  repository.py    # 数据访问：会话与记录增删改查
  service.py       # 业务逻辑：会话创建、对话流转、状态机、历史列表
  router.py        # HTTP 层：会话相关接口
```

## 5. 数据模型

### 5.1 InterviewSession（面试会话）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int（主键） | 自增主键 |
| `client_id` | str | 匿名标识，来自请求头 `X-Client-Id` |
| `direction` | str（枚举） | 岗位方向，取值见 questions 模块 |
| `segments` | JSON（环节列表） | 模板配置快照（题型 + 数量） |
| `status` | str（枚举） | `in_progress` 进行中 / `completed` 已完成 / `finished` 已结束 |
| `started_at` | datetime | 开始时间 |
| `ended_at` | datetime（可空） | 结束时间（终态时写入） |
| `created_at` | datetime | 创建时间 |

### 5.2 InterviewRecord（问答记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int（主键） | 自增主键 |
| `session_id` | int（外键） | 所属会话 |
| `round_index` | int | 轮次（0 起，按抽题顺序） |
| `question_id` | int（外键） | 题目（关联 questions 模块） |
| `user_answer` | str（可空） | 用户回答，未答为空 |
| `feedback` | str（可空） | AI 点评，未答为空 |

> 会话创建时即按题目序列为每道题生成一条记录（answer/feedback 为空）；「当前题」= 第一条 `user_answer` 为空的记录。

## 6. 接口设计

### 6.1 HTTP 层（对外，对应 PRD 第 8 节）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/interviews` | 创建会话，返回会话信息 + 第一题 |
| POST | `/api/interviews/{id}/answer` | 提交当前题回答，返回点评 + 下一题 / 结束标识 |
| POST | `/api/interviews/{id}/finish` | 提前结束面试 |
| GET | `/api/interviews` | 获取当前匿名标识下的历史会话列表 |

请求 / 响应要点：

- 创建：请求体为「模板 id」或「自定义配置（direction + segments）」二者其一；响应含 `session_id`、`direction`、`total_questions`、`current_question`（轮次 + 题干）、`status`。
- 回答：请求体 `{ "answer": str }`；响应含 `feedback`、`is_finished`、`next_question`（无下一题时为 null）。
- 结束：响应含 `session_id`、`status`。
- 历史列表：返回数组，每项含 `id`、`direction`、`total_questions`、`started_at`、`status`。

### 6.2 service（业务逻辑层）

| 方法 | 说明 |
|------|------|
| `create_session(client_id, config)` | 校验并解析配置 → engine 抽题 → 创建会话与记录 → 返回会话 + 第一题 |
| `submit_answer(session_id, client_id, answer)` | 校验会话归属与状态 → 校验回答 → 点评 → 推进或完成 |
| `finish_session(session_id, client_id)` | 将进行中会话置为「已结束」 |
| `list_sessions(client_id)` | 按匿名标识查询历史列表（倒序） |

### 6.3 状态机

```
（创建）──▶ in_progress
in_progress ──answer（非最后一题）──▶ in_progress
in_progress ──answer（最后一题）────▶ completed
in_progress ──finish────────────────▶ finished
completed / finished 为终态，不再接受 answer / finish
```

### 6.4 业务规则

1. **会话归属校验**：answer / finish 时校验 `session_id` 对应的 `client_id` 与请求头一致，不一致返回 403（防止跨用户操作）。
2. **空 / 过短回答拦截**：`answer` 为空或长度低于阈值（建议 `MIN_ANSWER_LENGTH = 10` 字符）时返回固定提示，不写记录、不推进（PRD F2）。
3. **终态只读**：对 `completed` / `finished` 会话调用 answer / finish 返回业务异常。
4. **题目序列生成**：创建时委托 engine `draw_questions` 生成有序题目列表，并一次性写入记录。

## 7. 关键设计决策

1. **记录创建时即生成全部轮次**：会话创建时一次性写入所有题目记录，answer 逐条回填，使「当前题」推导与「已答题目」统计都基于记录状态，状态单一来源。
2. **当前题推导而非冗余字段**：当前题 = 第一条 `user_answer` 为空的记录，避免在会话上维护 `current_index` 造成不一致。
3. **归属校验在 service 层**：所有会话操作强制校验 `client_id`，保证匿名标识隔离（PRD 6.4、F4）。
4. **报告不在本模块生成**：interviews 只维护会话与记录，报告生成由 reports 模块在查询时惰性完成，避免反向依赖。

## 8. 验收标准

- 创建会话后返回第一题，进度信息（第 1 题 / 共 N 题）正确。
- 逐题提交：每答一题返回点评；非最后一题返回下一题，最后一题后状态变为 `completed`。
- 空 / 过短回答被拦截并返回固定提示，不推进轮次。
- 提前结束后状态变为 `finished`，已答题目记录保留。
- 历史列表仅返回当前 `X-Client-Id` 对应的会话，按时间倒序，字段完整。
- 跨用户访问他人会话（answer / finish）被拒绝（403）。
