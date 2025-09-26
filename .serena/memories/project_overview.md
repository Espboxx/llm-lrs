## 项目概述
- 项目目标：模拟狼人杀游戏的完整流程，引入 AI 决策服务为各角色生成行动和发言，实现自动化对局。
- 核心功能：阶段管理、角色分配与技能冷却、胜负判定、消息广播、AI 决策与发言生成。
- 技术栈：Python 3，依赖 `openai`/兼容 OpenAI API 的客户端、`python-dotenv` 读取 `.env` 配置，自定义日志工具输出到 `logs/`。
- 环境配置：通过 `.env` 提供 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`AI_MODEL_NAME` 等变量，代码使用 `OpenAI` 客户端调用聊天补全接口。