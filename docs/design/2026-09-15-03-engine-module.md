# engine 模块执行计划书

| 项目 | 内容 |
|------|------|
| 所属项目 | AI 智能面试助手 MVP |
| 依据 PRD | docs/prd/2026-09-15-ai-interview-assistant-mvp-prd.md |
| 模块 | engine（AI 面试引擎） |
| 状态 | 待评审 |
| 实现顺序 | 第 3 个模块（依赖 core、questions） |

---

## 1. 模块目标

定义「面试引擎」抽象接口 `InterviewEngine`，并提供一个基于规则的 MVP 实现 `RuleBasedEngine`。上层 interviews、reports 模块只依赖抽象接口，不感知具体实现，从而为未来接入真实大模型（`LLMEngine`）预留零改动的替换点。

## 2. 职责边界

**做什么：**

- 定义 `InterviewEngine` 抽象接口：出题（抽题）与点评两大能力。
- 实现 `RuleBasedEngine`：按模板配置从题库抽题，按题目参考要点生成规则化点评。
- 封装抽题算法：按岗位方向 + 题型组合 + 数量，从题库中选取题目序列。
- 封装点评算法：基于用户回答与题目参考要点做关键词/规则匹配，生成点评模板。

**不做什么：**

- 不直接操作数据库读写会话/记录（由 interviews 模块负责，engine 只消费题目与生成点评结果）。
- 不定义 HTTP 路由，不对外暴露接口（engine 被上层 service 调用）。
- 不接入真实大模型（MVP 范围外，仅预留扩展点）。

## 3. 依赖关系

- **依赖**：core（仅基础设施，弱依赖）、questions（读取题目数据与筛选能力）。
- **被依赖**：interviews（出题 + 点评）、reports（复用点评结果生成报告）。

## 4. 文件结构

```
backend/app/engine/
  base.py           # InterviewEngine 抽象接口（Protocol / ABC）
  rule_based.py     # RuleBasedEngine 规则实现
  schemas.py        # 引擎输入 / 输出数据结构（抽题结果、点评结果）
```

> 说明：engine 是抽象能力层，不采用 `router → service → repository` 分层；它是被 interviews / reports 调用的领域能力。

## 5. 数据模型

engine 不定义持久化实体，仅定义引擎的输入/输出数据结构：

### 5.1 抽题输入 / 输出

| 结构 | 字段 | 说明 |
|------|------|------|
| 抽题输入 | `direction`、`segments`（题型+数量列表）、`difficulty`（可选） | 来自模板配置或自定义配置 |
| 抽题输出 | 题目序列 `List[Question]` | 已按配置排序的题目列表 |

### 5.2 点评输入 / 输出

| 结构 | 字段 | 说明 |
|------|------|------|
| 点评输入 | 题目 `Question`、用户回答 `answer`（str） | 单轮问答 |
| 点评输出 | `feedback`（str） | 规则生成的文字点评 |

## 6. 接口设计

### 6.1 `InterviewEngine` 抽象接口

| 方法 | 签名（示意） | 说明 |
|------|------|------|
| `draw_questions(direction, segments, difficulty=None)` | `-> List[Question]` | 按配置抽题 |
| `evaluate_answer(question, answer)` | `-> str` | 生成单题点评 |

> `InterviewEngine` 用 Python `Protocol` 或 ABC 定义均可，关键是被依赖方只 import 接口，不 import `RuleBasedEngine`。

### 6.2 `RuleBasedEngine` 实现要点

**抽题逻辑：**

1. 按 `direction` 与 `segments`（每个 segment = 题型 + 数量）遍历。
2. 对每个 segment，调用 questions 模块的 `filter_questions` 筛选符合「方向 + 题型」的题目。
3. 从筛选结果中随机（或按规则）选取指定数量的题目，保证不重复。
4. 题目不足时抛业务异常，交由上层返回明确错误（如「该组合题目数量不足」）。

**点评逻辑（规则模拟）：**

1. 取题目的 `reference_points`（参考要点字符串数组）。
2. 对每条要点，检查用户回答是否命中要点中的关键词（简单包含匹配）。
3. 命中要点按比例生成点评：命中多 → 正向点评模板；命中少 → 提示性点评模板，并附上未覆盖的参考要点。
4. 返回文字点评，模板化、确定性（同输入同输出），不依赖大模型。

## 7. 关键设计决策

1. **面向接口编程**：上层只依赖 `InterviewEngine`，通过依赖注入注入 `RuleBasedEngine` 实例，未来替换 `LLMEngine` 时上层模块零改动（PRD 6.3）。
2. **点评为确定性规则**：MVP 不调用大模型，点评基于参考要点关键词匹配生成模板，结果可复现、易测试（PRD 3 节说明的已知限制）。
3. **抽题随机但可注入随机源**：为保证可测试性，随机源作为可注入依赖，测试时可固定种子。
4. **题目不足显式报错**：抽题数量超过题库可用数量时抛出明确业务异常，由 interviews 层转换为 HTTP 错误，而非静默降级。

## 8. 验收标准

- 定义出 `InterviewEngine` 抽象接口，`RuleBasedEngine` 实现该接口。
- 给定方向 + 题型组合 + 数量，能抽取出正确数量、匹配题型与方向的题目序列。
- 抽题数量超过题库可用数量时抛出明确业务异常。
- 点评基于参考要点生成，命中与未命中要点的点评结果可区分。
- 上层模块（interviews / reports）仅依赖 `InterviewEngine` 接口即可完成出题与点评，替换实现无需修改上层代码。
