# AI 智能面试助手 — 前端 Mock 测试报告

| 项目 | 内容 |
|------|------|
| 测试日期 | 2026-09-21 |
| 测试范围 | 前端 4 个业务模块（用户 / 模板 / 面试 / 报告） |
| 技术栈 | 原生 HTML + CSS + JavaScript |
| 测试方式 | Mock 数据（localStorage 模拟后端全接口）+ Python 镜像验证 |
| 测试结果 | **23 passed · 0 failed · 0 skipped** |

---

## 1. 总览

前端项目（`frontend/`）采用「接口封装 `api.js` + 全接口 mock 后端 `mock.js` + 统一交互 `app.js`」的结构。
`api.js` 在 URL 携带 `?mock=1` 时自动将请求路由到 `mock.js`，用 localStorage 模拟后端
注册 / 登录 / 模板 / 面试 / 报告的全部接口，从而在无后端环境下完成前端功能验证。

由于当前环境无 Node / 浏览器运行时，本次通过 **Python 镜像**忠实复刻 `mock.js` 的后端逻辑，
执行与 `frontend/test/*.html` 完全一致的 23 个断言；真实的测试页可在浏览器打开
`frontend/test/*.html` 实时运行并展示 PASS/FAIL。

### 1.1 模块测试结果汇总

| 模块 | 测试页 | 用例数 | 结果 |
|------|--------|--------|------|
| 用户（users） | user-module-test.html | 7 | ✅ |
| 模板（templates） | templates-module-test.html | 3 | ✅ |
| 面试（interviews） | interviews-module-test.html | 9 | ✅ |
| 报告（reports） | reports-module-test.html | 4 | ✅ |
| **合计** | | **23** | **✅** |

---

## 2. 测试用例明细

### 2.1 用户模块（7 例）

| 用例 | 验证点 |
|------|--------|
| 注册成功返回 token 与 user | 注册返回 token 与用户信息 |
| 重复注册被拒绝 | 用户名已占用 → 错误「用户名已被占用」 |
| 用户名过短被拒绝 | < 3 字符 → 「参数校验失败」 |
| 密码过短被拒绝 | < 6 字符 → 「参数校验失败」 |
| 登录成功返回 token | 正确账号密码 → 返回 token |
| 密码错误登录失败 | → 「用户名或密码错误」 |
| 用户不存在登录失败 | → 「用户名或密码错误」 |

### 2.2 模板模块（3 例）

| 用例 | 验证点 |
|------|--------|
| 获取模板列表返回非空数组 | 返回非空数组 |
| 每个模板字段完整 | 含 id / name / direction / segments |
| segments 项包含 type 与 count | 每个环节含 type 且 count ≥ 1 |

### 2.3 面试模块（9 例）

| 用例 | 验证点 |
|------|--------|
| 按模板创建会话返回第一题 | session_id / total_questions / 第一题 |
| 自定义配置创建会话 | total_questions 与环节 count 之和一致 |
| 无配置创建被拒绝 | → 「必须提供模板或自定义配置」 |
| 提交回答返回点评与下一题 | 非最后一题返回下一题（round_index + 1） |
| 最后一题提交完成 | is_finished=true，next_question=null |
| 过短回答被拦截 | < 10 字符不推进轮次，返回「过短」提示 |
| 提前结束面试 | status 置为 finished |
| 历史列表仅含当前用户会话 | 列表字段完整、按用户隔离 |
| 跨用户访问被拒绝 | 他人会话 → 「无权访问该会话」 |

### 2.4 报告模块（4 例）

| 用例 | 验证点 |
|------|--------|
| 完成会话报告包含逐题点评 | 含总体评价 / 改进建议 / 2 条逐题点评 |
| 提前结束报告仅含已答题目 | 只含已作答题目（1 条） |
| 进行中会话查报告被拒绝 | → 「面试尚未完成，暂无报告」 |
| 跨用户查报告被拒绝 | → 「无权访问该会话」 |

---

## 3. 页面与接口覆盖

| 页面 | 关联接口 | 模块 |
|------|----------|------|
| login.html | POST /api/auth/register、POST /api/auth/login | 用户 |
| index.html | GET /api/templates、POST /api/interviews | 模板 / 面试 |
| interview.html | POST /api/interviews/{id}/answer、/finish | 面试 |
| report.html | GET /api/reports/{session_id} | 报告 |
| history.html | GET /api/interviews | 面试 |

---

## 4. 运行方式

- **Mock 演示（无需后端）**：浏览器打开 `frontend/login.html?mock=1`，走完整流程。
- **Mock 测试**：浏览器打开 `frontend/test/*.html`，页面自动运行并展示 PASS/FAIL。
- **真实联调**：启动后端后，用静态服务器托管 `frontend/`，`api.js` 默认走 `/api`。

## 5. 说明

- 测试断言覆盖各模块的**成功路径与错误分支**（参数校验、跨用户隔离、状态机终态、惰性报告生成等）。
- 认证状态（setAuth / getAuth / clearAuth）为纯浏览器 localStorage 逻辑，由前端用户模块测试页
  `user-module-test.html` 中的 3 个用例在浏览器内验证，不计入上述 23 个接口断言。
- 机器可读结果未单独生成（原生无构建工具，无 Node 运行测试框架）；如需 JUnit 格式可后续补充。
