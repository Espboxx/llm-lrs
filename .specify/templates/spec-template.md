# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

> 至少确保一个用户故事覆盖 12 人标准局流程。如设计变更标准配置，需说明验证对局及回放方式。

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently - e.g., "Can be fully tested by [specific action] and delivers [specific value]"]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and why it has this priority level]

**Independent Test**: [Describe how this can be tested independently]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- 夜晚阶段多个行动冲突时如何裁决？（例如女巫解救与猎人反杀顺序）
- 当大模型超时、拒答或返回无效内容时如何降级？
- 如果日志目录不可写或 `.env` 缺失关键变量，系统行为是什么？
- 对局进入罕见胜利条件（双阵营同灭等）时如何记录并终止？

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 游戏循环在 `core/engine/GameLoop` 中必须 [具体能力，例如「支持新增阶段 X」]。
- **FR-002**: `modules/roles/[role].py` 必须定义 [角色技能/限制]，并描述胜利条件影响。
- **FR-003**: `modules/actions` 必须提供 [具体公共行动]，说明投票/冷却规则。
- **FR-004**: 接口层（CLI/Web）必须展示 [玩家可见信息] 并保证与日志同步。
- **FR-005**: 系统必须在成功回合结束后持久化 [需要的日志或统计]。

*对不明确需求进行标注：*

- **FR-00X**: [能力]（NEEDS CLARIFICATION: 说明缺失的上下文或依赖）

### Key Entities *(include if feature involves data)*

- **[Entity 1: e.g., PlayerState]**: [模块职责、关键字段、生命周期]
- **[Entity 2: e.g., NightActionResult]**: [字段说明、与角色/行动的关系]

### Logging & Observability Requirements

- **LO-001**: 在 `utils.logger.logger` 中记录 [事件/字段]，包括阶段、行动结果与异常。
- **LO-002**: 为新增特性提供回放或调试指引（例如指定日志关键字）。
- **LO-003**: 明确验证日志可写及落盘路径（本地/部署环境）。

### AI Interaction Contracts

- **AI-001**: 通过 `services/AIDecisionService` 配置 Prompt 模板 `[路径]` 与变量说明。
- **AI-002**: 指定 `.env` 所需新增键值及降级策略（如本地模型、静态决策）。
- **AI-003**: 描述模型输入输出的期望格式与校验步骤。

### Configuration & Security Requirements

- **CFG-001**: 修改的配置文件路径、默认值与回滚方案。
- **CFG-002**: 新增或调整的环境变量，确保 README/运行指南同步。
- **CFG-003**: 权限和安全要求（例如日志敏感信息脱敏、角色配置校验）。

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 运行 1 局 12 人对局（含夜晚/白天循环）无未捕获异常，日志完整记录关键事件。
- **SC-002**: 模型或降级策略在出现 [错误类型] 时于指定超时时间内给出可用决策。
- **SC-003**: 新增用户故事可通过独立验证步骤重放（手动/pytest/脚本）并复现核心价值。
- **SC-004**: 如果引入配置或环境变量，部署文档更新到位，评审检查通过率 100%。
