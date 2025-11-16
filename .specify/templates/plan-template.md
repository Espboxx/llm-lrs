# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

**Language/Version**: Python 3.11（建议使用仓库 `.venv`）  
**Primary Dependencies**: `openai`/兼容本地模型端点、`python-dotenv`、`Flask`（观战面板）  
**Storage**: 静态配置位于 `config/`，运行日志写入 `logs/`，无长期数据库  
**Testing**: `pytest`（逐步补齐），可通过 `python main.py` 驱动 12 人对局验证  
**Target Platform**: 本地或服务器终端，可选 `--web` 面板  
**Project Type**: AI 驱动的狼人杀对局模拟及日志系统  
**Performance Goals**: 单局 12 名玩家决策在数分钟内完成，日志完整落盘  
**Constraints**: 必须确保日志写入、LLM 降级策略和 `.env` 安全；不得破坏核心原则  
**Scale/Scope**: 单实例运行，未来扩展多局统计与更多角色

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- 游戏完整性优先：说明是否保持 12 人标准局；若需变更，列出配置差异与验证计划。
- 模块职责清晰：罗列会触及的目录/模块，避免跨层嵌入游戏循环或配置解析。
- 日志与可观测性强制：描述要新增或调整的日志事件与验证方式。
- AI 决策可控：列出新增 Prompt、模型或降级策略，并确认复用 `AIDecisionService`。
- 配置与安全隔离：标明涉及的 `config/`、`.env` 或目录结构改动，并计划同步文档。

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```
core/
├── engine/                # 游戏循环与阶段控制
├── agents/                # 玩家与 AI 抽象层
modules/
├── roles/                 # 角色能力定义
├── actions/               # 投票与公共行动
interfaces/                # CLI / Web 适配器
services/
└── AIDecisionService/     # 大模型请求管道
utils/                     # 日志等通用工具
config/                    # 静态对局配置
tests/                     # pytest 套件（按需补充）
logs/                      # 运行期输出（保持可写）
```

**Structure Decision**: 记录与上述结构的偏离（新增目录、命名规范）以及对核心模块的影响。

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
