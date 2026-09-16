# frontend 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | frontend（前端） |
| 状态 | 待评审 |
| 实现顺序 | 第 7 个模块（依赖后端全部接口） |

---

## 1. 模块目标

实现 PC 端 Web 的四个页面（面试配置、面试进行、评估报告、历史记录），打通「配置 → 面试 → 报告 → 历史回顾」的完整用户闭环。使用原生 HTML + CSS + JavaScript（无框架），通过 REST API 与后端交互。

## 2. 职责边界

**做什么：**

- 面试配置页：预设模板选择 + 自定义配置，发起面试。
- 面试进行页：逐题对话、进度展示、提交回答、查看点评、提前结束。
- 评估报告页：展示总体评价、改进建议、每题点评。
- 历史记录页：展示当前匿名标识下的历史会话列表。
- 请求封装 `api.js`：统一附加匿名标识、统一错误处理。
- 匿名标识管理：生成 UUID 并持久化到 localStorage。

**不做什么：**

- 不使用前端框架（PRD 6.1）。
- 不实现语音交互、移动端适配、暗色主题（PRD 2.2）。
- 不做题库管理界面。

## 3. 依赖关系

- **依赖**：后端全部接口（templates、interviews、reports 模块），以及 core 模块定义的统一响应结构 `{ code, message, data }`。
- **被依赖**：无。

## 4. 文件结构

```
frontend/
  index.html        # 面试配置页（首页）
  interview.html    # 面试进行页
  report.html       # 评估报告页
  history.html      # 历史记录页
  css/common.css    # 共享样式
  js/api.js         # 请求封装 + 匿名标识管理
  js/index.js       # 配置页逻辑
  js/interview.js   # 进行页逻辑
  js/report.js      # 报告页逻辑
  js/history.js     # 历史页逻辑
```

## 5. 页面设计

### 5.1 index.html（面试配置页）

- **预设模板区**：进入页面调用 `getTemplates()` 渲染模板卡片（名称 + 岗位方向），点击选中。
- **自定义配置区**：岗位方向下拉、题型多选、题目数量设置。
- **开始面试**：组装配置 → `createInterview()` → 成功后跳转 `interview.html?session_id={id}`。
- **校验**：未选题型、题数为 0 时前端给出明确提示，不允许发起（与后端校验互补）。

### 5.2 interview.html（面试进行页）

- **进度**：显示「第 N 题 / 共 M 题」。
- **对话区**：展示当前题目；下方输入框 + 提交按钮。
- **提交回答**：调用 `submitAnswer()`；返回点评与下一题（或结束标识）。
- **点评展示**：提交后展示 AI 点评，随后进入下一题。
- **提前结束**：调用 `finishInterview()`，随后跳转报告页。
- **完成**：最后一题提交后跳转 `report.html?session_id={id}`。

### 5.3 report.html（评估报告页）

- 从 URL 读取 `session_id`，调用 `getReport()`。
- 展示：总体评价、改进建议、每题点评列表（题目 / 我的回答 / AI 点评）。
- 提供「返回历史」入口。

### 5.4 history.html（历史记录页）

- 调用 `listInterviews()` 获取会话列表，按时间倒序展示。
- 每条展示：岗位方向、题目数量、开始时间、状态（已完成 / 已结束）。
- 点击记录跳转 `report.html?session_id={id}`。

## 6. 接口封装（api.js）

### 6.1 匿名标识管理

- `getClientId()`：从 localStorage 读取，不存在则生成 UUID v4 并写入。
- 存储键：`client_id`（与 PRD 6.4 约定一致）。

### 6.2 通用请求

- `request(method, path, body)`：fetch 封装，自动附加请求头 `X-Client-Id`，解析统一响应结构。
- 统一响应约定（来自 core 模块）：`{ code, message, data }`；`code != 0` 时抛错并向用户展示 `message`。

### 6.3 业务 API 封装

| 函数 | 对应接口 | 说明 |
|------|----------|------|
| `getTemplates()` | GET `/api/templates` | 获取预设模板 |
| `createInterview(config)` | POST `/api/interviews` | 创建会话 |
| `submitAnswer(sessionId, answer)` | POST `/api/interviews/{id}/answer` | 提交回答 |
| `finishInterview(sessionId)` | POST `/api/interviews/{id}/finish` | 提前结束 |
| `listInterviews()` | GET `/api/interviews` | 历史列表 |
| `getReport(sessionId)` | GET `/api/reports/{session_id}` | 获取报告 |

## 7. 关键设计决策

1. **无框架、原生实现**：页面按 PRD 6.5 拆分，每页一个独立 JS 文件，共享 `api.js` 与 `common.css`，避免框架引入。
2. **跨页传参用 URL query**：`session_id` 通过 URL 参数在页面间传递（`interview.html?session_id=`、`report.html?session_id=`），简单可靠。
3. **匿名标识统一由 api.js 管理**：所有请求自动携带 `X-Client-Id`，业务页面无需关心，保证历史记录隔离。
4. **统一响应结构驱动**：前端所有错误提示统一走 core 定义的 `{ code, message, data }`，避免各页面重复处理。
5. **已知限制——面试页刷新不恢复进度**：PRD 第 8 节未提供「获取会话当前状态」接口，故面试进行页刷新后无法恢复进行中会话；此场景提示用户返回首页重新开始，恢复能力留待后续版本（可新增 `GET /api/interviews/{id}`）。

## 8. 验收标准

- 首页可加载预设模板，可选择模板或自定义配置发起面试。
- 配置无效时前端给出明确提示且不发起请求。
- 面试页逐题展示、进度正确、提交后展示点评并进入下一题。
- 最后一题提交后跳转报告页；提前结束也能跳转报告页。
- 报告页完整展示总体评价、改进建议、每题点评。
- 历史页按匿名标识展示当前浏览器的会话列表，点击可进入报告。
- 全部页面在 Chrome / Edge / Firefox 最新两个大版本正常使用。
- 所有请求自动携带 `X-Client-Id`，匿名标识在同一浏览器内保持稳定。
