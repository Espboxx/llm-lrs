# Repository Guidelines

## Project Structure & Module Organization
The entry point `main.py` seeds a standard twelve-player match and hands the configuration to `core/engine/GameLoop`. Core engine modules govern phase rotation, victory checks, and config validation. Role logic lives under `modules/roles`, while shared actions and vote handling sit in `modules/actions`. User-facing adapters go in `interfaces/`, AI integrations in `services/AIDecisionService`, and reusable helpers such as logging live under `utils/`. Static JSON-free configuration resides in `config/`, and runtime logs are emitted to `logs/`.

## Build, Test, and Development Commands
Create a virtual environment with `python -m venv .venv` and activate it via `.venv\Scripts\activate`. Install required packages with `pip install -r requirements.txt` (currently includes `python-dotenv`, `openai`, and `Flask`). Launch a local match through `python main.py`; append `--web` 可同时启动观战面板，例如 `python main.py --web`. The run will fail unless `.env` supplies API credentials or a compatible local model endpoint.

## Coding Style & Naming Conventions
Follow PEP 8 spacing and snake_case naming for modules, functions, and variables. Classes encapsulate single responsibilities (e.g., `GameLoop` handles orchestration, while each role class governs its own abilities). Prefer type hints and concise docstrings that clarify gameplay intent. Use `utils.logger.logger` for structured output rather than `print`, so file and console logs stay aligned.

## Testing Guidelines
A formal test suite is not yet checked in. When adding coverage, scaffold `tests/` with `pytest` and mirror the engine/role boundaries; name files `test_<module>.py`. Ensure new mechanics include unit tests for victory conditions, cooldown resets, and AI fallbacks, and run them with `pytest`.

## Commit & Pull Request Guidelines
Write commits in the imperative mood with short subject lines; Chinese summaries are welcome when they describe behavior (see `初始化项目：狼人杀AI对战系统`). Each pull request should link to the relevant issue, outline gameplay or API changes, call out new environment variables, and include screenshots or log excerpts if behavior differs. Confirm `python main.py` runs cleanly before requesting review.

## Environment & Security Notes
Keep secrets in `.env` only; never commit API keys. Default `.env` keys include `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `AI_MODEL_NAME`. If you rely on a self-hosted model, document the endpoint and ensure the log directory remains writable.

## 用户规则必须遵守
- 始终使用中文回答