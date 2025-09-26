## 常用命令
- `python -m venv .venv`：在仓库根目录创建虚拟环境。
- `.venv\Scripts\activate`：于 Windows PowerShell 激活虚拟环境。
- `pip install python-dotenv openai`：安装当前代码运行所需的核心依赖；若后续添加 `requirements.txt`，则改为 `pip install -r requirements.txt`。
- `python main.py`：使用默认 12 人配置启动一局模拟对战，日志会写入 `logs/`。