# users 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | users（匿名用户标识） |
| 状态 | 待评审 |
| 实现顺序 | 依赖 core；需早于 interviews / reports 实现（本计划书后补） |

---

## 1. 模块目标

封装「匿名用户标识」这一横切关注点：从请求头 `X-Client-Id` 解析并校验匿名标识，为各业务模块提供统一的「当前用户」获取方式。MVP 为免登录匿名模式（无账号体系），但模块边界为未来接入注册/登录预留演进空间。

## 2. 职责边界

**做什么：**

- 解析请求头 `X-Client-Id`，校验为合法 UUID。
- 提供 `get_client_id` 依赖注入，供各模块 router 获取当前用户标识。
- 定义匿名标识的校验 / 规范化规则。

**不做什么：**

- 不实现注册 / 登录体系（PRD 2.2 范围外）。
- 不持久化用户实体（匿名标识即字符串，无 User 表）。
- 不生成 UUID（生成逻辑在前端 `api.js` 的 `getClientId`，本模块仅校验后端收到的标识）。
- 不提供用户相关 HTTP 接口。

## 3. 依赖关系

- **依赖**：core（统一异常，用于标识非法时返回 400）。
- **被依赖**：interviews（历史隔离 + 会话归属校验）、reports（报告归属校验）。

## 4. 文件结构

```
backend/app/users/
  schemas.py     # 匿名标识的校验模型（UUID 格式）
  service.py     # 标识校验 / 规范化逻辑
  deps.py        # get_client_id 依赖注入（解析 X-Client-Id）
```

> 说明：MVP 匿名模式下无持久化实体、无对外接口，故不含 `router.py` / `repository.py` / `models.py`，仅保留 `schemas + service + deps`。未来接入账号体系时在此包内扩展 User 模型与注册/登录接口。

## 5. 数据模型

无持久化实体。核心概念：

| 概念 | 说明 |
|------|------|
| `client_id` | 字符串，UUID v4，作为匿名用户的唯一标识 |

## 6. 接口设计

### 6.1 依赖注入

| 方法 | 说明 |
|------|------|
| `get_client_id(x_client_id: str)` | 从请求头 `X-Client-Id` 解析匿名标识，供各模块 router 注入 |

### 6.2 校验规则

| 方法 | 说明 |
|------|------|
| `validate_client_id(client_id: str)` | 校验并规范化（小写、去空白）；非法抛业务异常 |

- 缺失或非 UUID 格式 → 抛统一业务异常，返回 400 + 统一错误结构（复用 core 异常体系）。

## 7. 关键设计决策

1. **后端只校验不生成**：UUID 由前端 `localStorage` 生成（`api.js` 的 `getClientId`），后端负责校验与使用，职责清晰、避免两端生成规则不一致。
2. **无用户表**：历史隔离直接按 `client_id` 字符串过滤（由 interviews 模块完成），无需持久化用户实体，符合 PRD「仅使用浏览器匿名标识」。
3. **预留演进点**：users 包是未来账号体系的落点；届时在包内增加 User 模型与注册/登录接口，上层由 `get_client_id` 平滑升级为「当前登录用户」，其余模块改动最小。

## 8. 验收标准

- 合法 UUID 的 `X-Client-Id` 正常通过并返回标识。
- 缺失或非法 `X-Client-Id` 返回 400 + 统一错误结构。
- interviews / reports 模块可通过本模块提供的依赖获取当前标识，完成历史隔离与归属校验。
- core 模块不再承担匿名标识解析职责。
