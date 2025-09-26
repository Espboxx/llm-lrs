## 目录结构
- `main.py`：入口脚本，组装配置并启动 `core.engine.game_loop.GameLoop`。
- `config/`：游戏阶段、角色冷却等静态配置。
- `core/engine/`：游戏主循环、阶段管理、配置校验和胜利判定等核心逻辑。
- `core/agents/`：存放代理相关基础代码（待进一步梳理）。
- `modules/`：按领域划分的模块，包含 `roles/`（各角色实现与工厂）、`actions/`（昼夜行为与投票）、`comms/`（消息路由）、`validators/` 等。
- `services/`：对外服务层，目前包含 `AIDecisionService` 调用 OpenAI/Ollama。
- `interfaces/`：用户界面层（如 `web_ui/`）。
- `utils/`：工具函数与自定义日志器，日志输出至 `logs/` 目录。