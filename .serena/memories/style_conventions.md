## 代码风格
- 语言统一使用 Python，遵循 PEP 8 缩进（4 空格）、snake_case 命名和类型注解（核心引擎、服务层方法均带 `Dict[str, Any]` 等注解）。
- 类和模块职责保持单一，例如 `GameLoop` 负责主循环，角色行为封装在 `modules/roles` 中，遵循 SRP。
- 采用段内中文文档字符串和注释说明业务背景；保持注释精炼，仅注明关键业务规则。
- 日志统一使用 `utils.logger.logger` 提供的封装方法，而非直接 `print`。