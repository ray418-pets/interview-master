# reports 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | reports（评估报告） |
| 状态 | 待评审 |
| 实现顺序 | 第 6 个模块（依赖 core、questions、interviews） |

---

## 1. 模块目标

在面试进入终态后生成并查询评估报告，内容包括总体评价、改进建议与每题点评。报告与会话一对一，可重复查看，并支持提前结束的面试（基于已作答题目生成）。

## 2. 职责边界

**做什么：**

- 定义报告数据模型（与会话一对一）。
- 报告生成：基于会话的已作答记录，用规则模板生成总体评价与改进建议。
- 报告查询：按会话 id 返回完整报告（总体评价 + 改进建议 + 每题点评）。
- 惰性生成：查询时若报告不存在且会话已终态，则生成并保存。

**不做什么：**

- 不实现点评算法（点评已在 engine / interviews 阶段生成并落库）。
- 不管理会话状态（由 interviews 模块完成）。
- 不接入真实大模型的评价（MVP 用规则模板）。

## 3. 依赖关系

- **依赖**：core（数据库会话）、questions（join 题目内容）、interviews（读取会话与问答记录）。
- **被依赖**：无后端模块依赖本模块（仅前端调用其接口）。

## 4. 文件结构

```
backend/app/reports/
  models.py        # Report 数据模型
  schemas.py       # 报告响应模型
  repository.py    # 数据访问：报告增删改查
  service.py       # 业务逻辑：报告生成与查询（惰性生成）
  router.py        # HTTP 层：GET /api/reports/{session_id}
```

## 5. 数据模型

### 5.1 Report（评估报告）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int（主键） | 自增主键 |
| `session_id` | int（外键，唯一） | 关联会话，一对一 |
| `overall_evaluation` | str | 总体评价（文字） |
| `improvement_suggestions` | str | 改进建议（文字） |
| `created_at` | datetime | 生成时间 |

> 每题点评（题目、我的回答、AI 点评）不重复存储，直接取自 interviews 模块的 `InterviewRecord`，报告查询时组装返回。

## 6. 接口设计

### 6.1 HTTP 层（对外，对应 PRD 第 8 节）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/reports/{session_id}` | 获取某次会话的评估报告 |

响应结构：

| 字段 | 说明 |
|------|------|
| `session_id` | 会话 id |
| `direction` | 岗位方向 |
| `status` | 会话状态 |
| `overall_evaluation` | 总体评价文字 |
| `improvement_suggestions` | 改进建议文字 |
| `questions` | 每题点评数组（按 `round_index` 升序，仅已作答） |

`questions` 数组每项：`question_content`（题目内容）、`user_answer`（我的回答）、`feedback`（AI 点评）。

### 6.2 service（业务逻辑层）

| 方法 | 说明 |
|------|------|
| `get_report(session_id, client_id)` | 校验会话归属与状态 → 存在则返回，缺失且已终态则生成 |
| `generate_report(session_id)` | 基于已作答记录生成报告并保存 |

### 6.3 生成逻辑（规则模板）

1. 读取会话与其已作答记录（`user_answer` 非空）。
2. **每题点评**：直接组装记录的 `question_content + user_answer + feedback`。
3. **总体评价**：模板化，基于完成度（已作答数 / 总题数）与岗位方向生成。
4. **改进建议**：模板化，汇总未作答的题型，并附通用改进建议。

### 6.4 查询规则

- 会话不存在或不属于当前 `client_id` → 返回 404 / 403。
- 会话仍为 `in_progress` → 返回业务异常（「面试尚未完成，暂无报告」）。
- 会话为 `completed` / `finished` 且报告缺失 → 生成后返回；已存在 → 直接返回（幂等，不重复生成）。

## 7. 关键设计决策

1. **惰性生成**：报告在首次查询时生成，而非在 interviews 会话结束时同步生成，避免 interviews → reports 的反向依赖，模块职责更清晰。
2. **每题点评不冗余存储**：来自 `InterviewRecord` 的题目、回答、点评是唯一事实来源，Report 只存总体评价与改进建议。
3. **总体评价为完成度导向模板**：MVP 不依赖大模型，总体评价按完成度 + 方向生成确定性模板；质量维度的量化评价留待接入真实大模型后增强（PRD 3 节已知限制）。
4. **幂等生成**：同一会话报告只生成一次，重复查询不重复写库。

## 8. 验收标准

- 完成（`completed`）或提前结束（`finished`）的面试能查到完整报告（总体评价 + 改进建议 + 每题点评）。
- 提前结束的报告仅包含已作答题目，未作答题目不出现。
- `in_progress` 会话查询报告返回明确错误。
- 报告可重复查看，重复查询不重复生成（幂等）。
- 跨用户查询他人会话报告被拒绝（403）。
- 报告与会话正确关联，每题点评包含题目内容、我的回答、AI 点评。
