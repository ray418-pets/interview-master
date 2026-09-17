# AI 智能面试助手 MVP — 后端 API 测试报告

| 项目 | 内容 |
|------|------|
| 测试日期 | 2026-09-17 |
| 测试范围 | 后端全部 7 个模块（core / users / questions / engine / templates / interviews / reports） |
| 测试框架 | pytest 9.1.1 + FastAPI TestClient（httpx） |
| 数据库 | SQLite（内存库，每个用例独立实例，`db_session` fixture 自动建表 + 种子数据） |
| 测试结果 | **76 passed · 0 failed · 0 skipped** |
| 执行耗时 | 约 9 秒 |

---

## 1. 总览

本次按 TDD（先写失败测试 → 观察失败 → 实现 → 验证通过）补齐了 5 个缺失的后端模块
（questions / engine / templates / interviews / reports），并为全部 7 个模块建立了测试用例，
覆盖服务层（service/repository）与 HTTP 层（API）两条路径。

### 1.1 模块测试结果汇总

| 模块 | 测试文件 | 用例数 | 结果 |
|------|----------|--------|------|
| core（公共能力） | test_core_exceptions / test_core_handlers / test_core_schemas | 8 | ✅ |
| users（用户认证） | test_users_api / test_users_service | 9 | ✅ |
| questions（题库） | test_questions_service | 8 | ✅ |
| engine（面试引擎） | test_engine | 8 | ✅ |
| templates（面试模板） | test_templates_api / test_templates_service | 13 | ✅ |
| interviews（面试会话） | test_interviews_api / test_interviews_service | 19 | ✅ |
| reports（评估报告） | test_reports_api / test_reports_service | 11 | ✅ |
| **合计** | | **76** | **✅** |

---

## 2. API 接口覆盖

| 方法 | 路径 | 模块 | 覆盖场景 |
|------|------|------|----------|
| POST | `/api/auth/register` | users | 注册成功 / 用户名重复 409 / 参数校验 |
| POST | `/api/auth/login` | users | 登录成功 / 密码错误 401 / 用户不存在 401 |
| GET | `/api/templates` | templates | 返回预设模板列表，字段完整 |
| POST | `/api/interviews` | interviews | 未认证 401 / 按模板创建 / 自定义配置创建 / 非法配置 400 |
| POST | `/api/interviews/{id}/answer` | interviews | 正常作答返回点评与下一题 / 最后一题完成 / 过短拦截 / 跨用户 403 / 会话不存在 404 / 终态 409 |
| POST | `/api/interviews/{id}/finish` | interviews | 提前结束置为 finished / 跨用户 403 |
| GET | `/api/interviews` | interviews | 仅返回当前用户会话，倒序，字段完整 |
| GET | `/api/reports/{session_id}` | reports | 未认证 401 / 完成后返回完整报告 / 进行中 409 / 跨用户 403 |

---

## 3. 各模块测试用例明细

### 3.1 core（8 例）

- 异常体系：`AppError` 携带 code / message / status_code，默认 400，是异常实例。
- 统一异常处理：业务异常返回统一 `{code, message}` 结构；未知异常返回 500 且不泄露堆栈详情。
- 统一响应结构：`ApiResponse` 默认 `code=0`；`ErrorResponse` 字段完整。

### 3.2 users（9 例）

- 注册：创建用户并返回 token；重复用户名抛 409。
- 登录：成功返回 token；密码错误 / 用户不存在抛 401。
- API：注册 / 登录 / 密码错误 401 / 重复注册 409。

### 3.3 questions（8 例）

- 种子数据：首次导入 ≥ 100 题；幂等（重复导入不重复）；覆盖全部 6 个岗位方向 × 5 种题型。
- 筛选：按方向 + 题型、按难度正确筛选；非法方向 / 题型 / 难度均被拒绝。

### 3.4 engine（8 例）

- 抽题：按方向 + 题型返回正确数量与类型；按环节顺序与数量返回；题目不足抛业务异常；固定随机种子可复现。
- 点评：全部命中要点返回正向点评；部分命中列出遗漏要点；全部未命中返回提示；无参考要点时仍返回有效反馈。

### 3.5 templates（13 例）

- 种子：创建预设模板（≥ 3 个）；幂等。
- 配置校验：合法配置通过；非法方向 / 空题型组合 / 非法题型 / 单环节 count < 1 / 总数 > 20 均拒绝。
- 解析：按模板 id 解析；模板不存在抛错；自定义配置解析；无任何输入抛错。
- API：`GET /api/templates` 返回字段完整。

### 3.6 interviews（19 例）

- 创建：返回第一题与进度；自定义配置；无配置抛错。
- 作答：返回点评与下一题；最后一题置为 completed；过短回答拦截且不推进；跨用户 403；会话不存在 404；终态只读 409。
- 提前结束：置为 finished。
- 历史列表：仅返回当前用户会话，倒序，字段完整。
- API：完整覆盖创建 / 作答 / 结束 / 列表四条接口及其鉴权与错误分支。

### 3.7 reports（11 例）

- 完成会话：返回总体评价 + 改进建议 + 每题点评。
- 提前结束：仅包含已作答题目。
- 幂等：重复查询不重复生成（仅一行 Report）。
- 错误分支：进行中 409 / 会话不存在 404 / 跨用户 403。
- API：完整覆盖报告接口的鉴权与业务分支。

---

## 4. 设计说明与约定

1. **匿名标识 → 认证用户**：计划书中的匿名 `X-Client-Id` 已演进为注册/登录 + `Bearer` token
   认证。会话与报告归属由 `users.get_current_user` 提供的 `user_id` 决定，代替原 `client_id`。
2. **枚举契约**：岗位方向 / 题型 / 难度枚举统一定义在 `app/questions/enums.py`，全项目共享，
   数据库存 snake_case 字符串。
3. **种子数据**：`app/questions/seed_data.json` 含 120 题（6 方向 × 5 题型 × 4 难度档）；
   预设模板 6 套定义在 `templates/service.py`。首次启动由 lifespan 幂等导入。
4. **依赖方向**：严格 `router → service → repository`；engine 仅被 interviews / reports 依赖，
   上层只依赖 `InterviewEngine` 抽象，未来可零改动替换为真实大模型实现。

## 5. 已知说明

- 测试输出含 2 条来自第三方库（starlette testclient 的 `httpx`、anyio 别名）的弃用提示，
  与项目代码无关，不影响结果。
- 机器可读结果见同目录 `junit.xml`。
