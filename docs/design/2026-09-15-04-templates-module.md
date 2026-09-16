# templates 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | templates（面试模板） |
| 状态 | 待评审 |
| 实现顺序 | 第 4 个模块（依赖 core、questions） |

---

## 1. 模块目标

提供面试模板能力：内置若干预设模板（一键开始），以及对自定义面试配置的校验。模板/配置是创建面试会话的输入，interviews 模块据此委托 engine 抽题。

## 2. 职责边界

**做什么：**

- 定义模板数据模型（预设模板）与自定义配置数据结构。
- 内置预设模板（如「前端开发面试」「后端开发面试」「产品经理面试」「通用行为面试」等）。
- 自定义配置校验：岗位方向、题型组合、题目数量的合法性校验。
- 提供预设模板列表查询能力（对应接口 `GET /api/templates`）。

**不做什么：**

- 不做实际抽题（由 engine 模块完成）。
- 不管理会话状态（由 interviews 模块完成）。
- 不提供模板管理前端界面（MVP 仅后端提供模板数据能力）。

## 3. 依赖关系

- **依赖**：core（数据库会话）、questions（题型枚举契约）。
- **被依赖**：interviews（创建会话时校验配置并获取模板）。

## 4. 文件结构

```
backend/app/templates/
  models.py        # InterviewTemplate 数据模型
  schemas.py       # 模板 / 自定义配置的请求 / 响应模型
  repository.py    # 数据访问：模板增删改查
  service.py       # 业务逻辑：配置校验、模板查询
  router.py        # HTTP 层：GET /api/templates
```

## 5. 数据模型

### 5.1 InterviewTemplate（预设模板）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int（主键） | 自增主键 |
| `name` | str | 模板名称（如「前端开发面试」） |
| `direction` | str（枚举） | 岗位方向，取值见 questions 模块 5.2 |
| `segments` | JSON（环节列表） | 环节 = 题型 + 数量，如 `[{"type":"technical","count":5}]` |

### 5.2 自定义配置结构（非持久化，仅请求/校验用）

| 字段 | 类型 | 说明 |
|------|------|------|
| `direction` | str（枚举） | 岗位方向 |
| `segments` | JSON（环节列表） | 题型 + 数量，可多选 |
| `total_count` | int | 题目总数量（各环节数量之和，1–20） |

### 5.3 环节（segment）结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `type` | str（枚举） | 题型，取值见 questions 模块 5.2 |
| `count` | int | 该题型题目数量，≥ 1 |

## 6. 接口设计

### 6.1 HTTP 层（对外）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/templates` | 返回预设模板列表 |

响应结构：模板数组，每项含 `id`、`name`、`direction`、`segments`。

### 6.2 service（业务逻辑层）

| 方法 | 说明 |
|------|------|
| `list_templates()` | 返回全部预设模板 |
| `validate_config(direction, segments)` | 校验自定义配置合法性，返回规范化后的配置或抛业务异常 |
| `resolve_config(template_id=None, custom_config=None)` | 统一入口：要么按模板 id 取配置，要么校验自定义配置 |

### 6.3 校验规则

- `direction` 必须在 questions 模块定义的枚举内。
- `segments` 非空，且每个 `type` 在题型枚举内、`count ≥ 1`。
- 题目总数（各环节 count 之和）在 1–20 之间。
- 任一校验失败 → 抛业务异常，返回 400 与明确提示（PRD F1 验收标准）。

## 7. 关键设计决策

1. **预设模板存库、自定义配置仅校验**：预设模板持久化到数据库（种子数据），自定义配置是请求时校验的临时结构，不落库。
2. **`segments` 用 JSON 存储环节列表**：与 engine 抽题输入的 `segments` 结构一致，模板/配置解析后直接透传给 engine，避免二次转换。
3. **数量校验放 templates 层**：1–20 题、环节 count 约束在此层统一校验，engine 与 interviews 不必重复。
4. **模板与配置统一为「配置」概念**：interviews 创建会话时只接收一份规范化的 `direction + segments`，无论来源是预设模板还是自定义。

## 8. 验收标准

- `GET /api/templates` 返回内置预设模板列表，字段完整。
- 自定义配置校验：合法配置通过，非法配置（未选题型、题数为 0、方向非法、总数超 20）返回 400 + 明确提示。
- 通过模板 id 能解析出规范化的 `direction + segments`。
- interviews 模块可调用 `resolve_config` 获取可用于 engine 抽题的配置。
