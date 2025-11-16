---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: 示例任务包含 `pytest` / `python main.py` 验证项。仅在规格要求时保留自动化测试，否则至少提供手动对局回放步骤。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **核心引擎**: `core/engine/`, `core/agents/`
- **角色/行动**: `modules/roles/`, `modules/actions/`
- **AI 服务**: `services/AIDecisionService/`
- **接口层**: `interfaces/`（CLI/Web）
- **公共工具**: `utils/`
- **测试套件**: `tests/`（按需新增场景）
- 路径示例均基于项目默认结构，若在计划中调整需同步注明

<!-- 
  ============================================================================
  IMPORTANT: The tasks below are SAMPLE TASKS for illustration purposes only.
  
  The /speckit.tasks command MUST replace these with actual tasks based on:
  - User stories from spec.md (with their priorities P1, P2, P3...)
  - Feature requirements from plan.md
  - Entities from data-model.md
  - Endpoints from contracts/
  
  Tasks MUST be organized by user story so each story can be:
  - Implemented independently
  - Tested independently
  - Delivered as an MVP increment
  
  DO NOT keep these sample tasks in the generated tasks.md file.
  ============================================================================
-->

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 确认 `config/`、`logs/`、`services/` 相关目录存在且具备写权限
- [ ] T002 在 `.env.example` 中记录本次需求涉及的环境变量（若无则标注 N/A）
- [ ] T003 [P] 更新 README/运行指南，说明如何运行 `python main.py [--web]` 验证
- [ ] T004 [P] 准备所需 Prompt 或配置模板文件，放置在约定目录

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [ ] T010 确认 `core/engine/GameLoop` 可挂接新的阶段/事件（若涉及核心流程）
- [ ] T011 [P] 设计 `modules/actions` 公共 API，明确输入输出结构
- [ ] T012 [P] 为 `utils.logger.logger` 定义新增日志字段或上下文
- [ ] T013 建立本地/降级模型封装，确保 `AIDecisionService` 可复用
- [ ] T014 配置所需的静态资源或数据文件，并在 `config/` 中注册
- [ ] T015 校验 `.env` 中的必需键值是否齐全，记录缺失项的处理方式

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - [Title] (Priority: P1) 🎯 MVP

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T020 [P] [US1] `pytest tests/[scope]/test_[feature].py` 覆盖关键胜利条件
- [ ] T021 [P] [US1] 运行 `python main.py` 并附带日志校验脚本，确保新流程复现

### Implementation for User Story 1

- [ ] T022 [P] [US1] 更新 `core/engine/GameLoop` 以挂接 [阶段/事件]
- [ ] T023 [P] [US1] 在 `modules/roles/[role].py` 定义新角色能力或状态
- [ ] T024 [US1] 在 `modules/actions/[action].py` 实现公共行动逻辑（依赖 T022/T023）
- [ ] T025 [US1] 扩展 `services/AIDecisionService` Prompt/降级策略
- [ ] T026 [US1] 在 `interfaces/` 更新 CLI/Web 展示或交互
- [ ] T027 [US1] 通过 `utils.logger.logger` 增加日志字段并验证输出
- [ ] T028 [US1] 更新 `config/` 或 `.env.example`，记录默认值及回滚方案

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T030 [P] [US2] `pytest tests/[scope]/test_[feature].py` 检查夜晚/白天边界
- [ ] T031 [P] [US2] 运行 `python main.py --web`（若使用面板）并记录观测点

### Implementation for User Story 2

- [ ] T032 [P] [US2] 在 `modules/roles` 中扩展相关角色或状态机
- [ ] T033 [US2] 扩展 `modules/actions` 或新增行动协调器
- [ ] T034 [US2] 为 `services/AIDecisionService` 加入额外提示词或参数
- [ ] T035 [US2] 在 `interfaces/` 更新玩家可见信息，保持与日志同步
- [ ] T036 [US2] 校验配置/文档更新，并与 US1 产物保持独立可回滚

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T040 [P] [US3] `pytest` 针对本故事的契约/集成测试
- [ ] T041 [P] [US3] 记录一次对局回放日志，确认关键事件被追踪

### Implementation for User Story 3

- [ ] T042 [P] [US3] 修改 `core/engine` 或新建调度器以支持额外场景
- [ ] T043 [US3] 在 `services/` 实现特定策略或降级逻辑
- [ ] T044 [US3] 在 `interfaces/` 或 `utils/` 添加辅助工具（如日志过滤、统计）
- [ ] T045 [US3] 更新 `config/`/文档，确保故事可独立启用与回滚

**Checkpoint**: All user stories should now be independently functional

---

[Add more user story phases as needed, following the same pattern]

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Documentation updates in docs/
- [ ] TXXX Code cleanup and refactoring
- [ ] TXXX Performance optimization across all stories
- [ ] TXXX [P] Additional unit tests (if requested) in tests/unit/
- [ ] TXXX Security hardening
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Launch all models for User Story 1 together:
Task: "更新 core/engine/GameLoop 以挂接 [阶段]"
Task: "实现 modules/roles/[role].py 的新能力"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
