<!--
Sync Impact Report
Version change: N/A → 1.0.0
Modified principles:
- 初版发布，无历史原则
Added sections:
- Core Principles
- 关键工程约束
- 开发流程与审查
Removed sections:
- 无
Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated
- .specify/templates/checklist-template.md ✅ updated
Follow-up TODOs:
- 无
-->

# LLM-Werewolf 宪章

## Core Principles

### I. 游戏完整性优先
系统必须保持 12 人标准局的昼夜轮转、投票和胜利判定，由 `core/engine/GameLoop` 作为唯一阶段与胜利检查入口。任何偏离标准流程的改动都必须在 `config/` 中提供可审阅配置，并在计划中说明验证策略；否则不得合入。理由：标准化流程是复现 AI 策略与保障角色能力平衡的基础。

### II. 模块职责清晰
实现必须遵守既定分层：角色能力仅在 `modules/roles`，公共行动在 `modules/actions`，用户界面与适配器在 `interfaces/`，AI 推理在 `services/AIDecisionService` 或其子模块。禁止跨层直接嵌入游戏循环、持久化或配置解析逻辑。理由：职责单一便于调试、复用与团队协作。

### III. 日志与可观测性强制
运行期输出必须使用 `utils.logger.logger`，覆盖阶段切换、投票结果、AI 决策要点与角色技能效果；严禁使用 `print` 或无格式输出。新增功能需定义最低日志字段，确保 `logs/` 中能够追踪对局。理由：充分的观测性是回放失误和训练模型的前提。

### IV. AI 决策可控
所有大模型请求必须通过 `.env` 配置的 `OPENAI_*` 或等价本地端点，并复用 `services/AIDecisionService` 的调用路径。Prompt 模板与系统消息需集中存放于对应模块，提交时应附带回退策略（本地模型或确定性模拟）。理由：控制输入输出可避免策略漂移并降低外部依赖故障的影响。

### V. 配置与安全隔离
静态配置仅放置于 `config/`，运行日志写入 `logs/`，环境密钥仅保留在 `.env`，严禁提交敏感信息。任何配置或目录结构变更必须同步更新文档并在评审中确认部署步骤。理由：清晰的配置边界可以减少环境差异及安全风险。

## 关键工程约束

- 代码需遵循 PEP 8 与 snake_case，关键函数与类提供类型注解和简洁 docstring，复杂逻辑需辅以行内注释。
- 默认通过 `python main.py` 驱动 12 人对局；自定义场景需在计划与配置中描述并给出回归验证方法。
- 缺失的自动化测试应在 spec 或 tasks 中列出验证脚本（`pytest`、模拟对局或日志断言），并记录预期输出。
- 日志目录与配置文件的写权限必须在部署前验证；新增文件夹需在仓库中预建并纳入 `.gitkeep`。
- 外部依赖（LLM、Web 面板等）需要列出降级路径与出错时的告警/日志方案。

## 开发流程与审查

- 立项前执行 Constitution Check：确认功能不破坏核心原则，必要时更新验证计划或提出豁免说明。
- 任务分解需保持用户故事独立交付，每个故事包含日志、验证与回退要求，避免跨模块耦合。
- 提交前运行 `python main.py [--web]` 或提供无法执行原因，确保日志不报错且输出目录可写。
- 评审需核对 `.env` 变量、配置文件与 README/项目文档是否同步更新；新增环境项必须在 PR 描述中列出。
- 发布后将关键对局日志或验证结果存入 `logs/`，供后续训练与问题回溯。

## Governance

宪章优先于其他工程实践文档；任何与原则冲突的流程都需要在此文件中先行修订。修订流程如下：

1. 在计划阶段记录拟议修改的原因与影响，并征求核心维护者一致同意。
2. 根据变更范围执行语义化版本更新：业务或原则重写为主版本，新增原则或重大指导为次版本，措辞澄清为修订号。
3. 更新受影响的模板与运行指南，确保所有工具（plan/spec/tasks/checklist）产出与最新原则一致。
4. 记录修订日期与版本号，并将对局验证或检查结果附在 PR/变更说明中。

合规性检查至少在每个主要版本发布前执行一次，确认现有流程（计划、规格、任务、日志）均遵守宪章。若发现违反项，必须创建整改任务并在下一个迭代解决。

**Version**: 1.0.0 | **Ratified**: 2025-10-12 | **Last Amended**: 2025-10-12
