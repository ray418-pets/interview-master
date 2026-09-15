# questions 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | questions（题库） |
| 状态 | 待评审 |
| 实现顺序 | 第 2 个模块（依赖 core） |

---

## 1. 模块目标

提供题目的存储、种子数据加载与筛选能力，作为面试出题（engine 模块）与模板（templates 模块）的数据来源。MVP 内置约 100–200 道题，覆盖技术（前端 / 后端 / 算法）、产品、运营、通用行为等多个岗位方向。

## 2. 职责边界

**做什么：**

- 定义题目数据模型（岗位方向、题型、难度、题目内容、参考要点）。
- 题库种子数据的加载与初始化（首次启动时导入）。
- 题目筛选：按岗位方向、题型、难度组合筛选。
- 提供题目查询能力给 engine / templates 模块使用。

**不做什么：**

- 不提供题库管理前端界面（PRD 2.2 明确不做）。
- 不向前端单独暴露题库 HTTP 接口（PRD 第 8 节说明，抽题由 engine 内部完成）。
- 不做点评、不出题策略（属于 engine 模块）。

## 3. 依赖关系

- **依赖**：core（数据库会话、`Base` 声明基类）。
- **被依赖**：engine（抽题时读取题目）、templates（题型校验时引用题型枚举）。

## 4. 文件结构

```
backend/app/questions/
  models.py        # Question 数据模型
  schemas.py       # 题目相关的请求 / 响应模型（供内部与后续扩展使用）
  repository.py    # 数据访问：题目增删改查
  service.py       # 业务逻辑：题目筛选规则
  router.py        # HTTP 层（MVP 不暴露题库接口，本文件可为空/省略）
  seed_data.json   # 题库种子数据（约 100–200 题）
```

> 说明：PRD 6.2 给出的标准包结构包含 `router.py`，但题库接口不在 MVP 前后端边界内，故 router 层暂不对外提供路由，仅保留包结构一致性。

## 5. 数据模型

### 5.1 Question（题目）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int（主键） | 自增主键 |
| `direction` | str（枚举） | 岗位方向 |
| `question_type` | str（枚举） | 题型 |
| `difficulty` | str（枚举） | 难度 |
| `content` | str | 题目内容（对用户展示的题干） |
| `reference_points` | JSON（字符串数组） | 参考要点，规则点评的依据 |

### 5.2 枚举值定义（全项目统一）

| 枚举 | 取值 | 中文含义 |
|------|------|----------|
| 岗位方向 `direction` | `technical_frontend` | 技术-前端 |
| | `technical_backend` | 技术-后端 |
| | `technical_algorithm` | 技术-算法 |
| | `product` | 产品 |
| | `operations` | 运营 |
| | `general` | 通用 |
| 题型 `question_type` | `self_introduction` | 自我介绍 |
| | `technical` | 技术题 |
| | `behavioral` | 行为题 |
| | `project_experience` | 项目经验题 |
| | `open_ended` | 开放题 |
| 难度 `difficulty` | `easy` | 简单 |
| | `medium` | 中等 |
| | `hard` | 困难 |

> 以上枚举取值是 engine / templates 模块共同遵循的契约，后续模块引用时不得另行命名。

## 6. 接口设计

### 6.1 repository（数据访问层）

| 方法 | 说明 |
|------|------|
| `get_by_id(question_id)` | 按主键查询单题 |
| `list_by_filter(direction, question_types, difficulty)` | 按条件筛选题目列表 |
| `count_by_filter(direction, question_types, difficulty)` | 按条件统计题目数量（供数量校验使用） |
| `bulk_insert(questions)` | 批量导入种子数据 |

### 6.2 service（业务逻辑层）

| 方法 | 说明 |
|------|------|
| `filter_questions(direction, question_types, difficulty=None)` | 题目筛选入口，校验枚举合法性并委托 repository |
| `seed_if_empty()` | 首次启动时若题库为空则从 `seed_data.json` 导入 |

> service 层负责筛选规则与合法性校验；repository 层只负责数据读写，保持职责单一。

## 7. 关键设计决策

1. **`reference_points` 用 JSON 字符串数组存储**：每条要点是一个字符串，规则点评时逐条比对用户回答中的关键词，生成模板化点评。这是 engine 模块点评的数据基础。
2. **枚举统一用英文 snake_case**：数据库存字符串枚举值，中文字面量仅用于前端展示映射，避免中英文混用导致校验不一致。
3. **种子数据随包分发**：`seed_data.json` 与代码同目录，`seed_if_empty` 幂等，重复启动不重复导入。
4. **不对外暴露题库接口**：题目筛选、抽题由 engine 模块内部调用 service 完成，符合 PRD 第 8 节边界约定。

## 8. 验收标准

- 首次启动后题库自动导入 100–200 道题，覆盖全部 6 个岗位方向与 5 种题型。
- `filter_questions` 能按岗位方向、题型、难度正确筛选。
- 非法枚举值（未知方向/题型）能被拒绝并返回明确错误。
- `seed_if_empty` 幂等：重复启动不会重复导入题目。
- engine / templates 模块可正常调用本模块的 service 完成抽题与题型校验。
