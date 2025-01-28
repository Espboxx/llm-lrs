

好的,我来帮您编写一个`README.md`文件:

```markdown
# LLM-Werewolf: AI狼人杀对战系统

一个基于大语言模型的狼人杀AI对战系统,让AI扮演不同角色进行狼人杀游戏对抗。

## 项目结构

```
llm-werewolf/
├── core/                    # 核心系统层
│   ├── engine/             # 游戏引擎
│   └── agents/             # 智能体管理
├── modules/                # 功能模块层
│   ├── roles/              # 角色系统
│   ├── actions/            # 动作决策
│   └── comms/              # 通信管理
├── data/                   # 数据存储
├── interfaces/             # 交互接口
├── tests/                  # 测试套件
└── utils/                  # 工具库
```

## 主要特性

- 支持12人标准局狼人杀游戏
- AI智能体可以扮演不同角色(狼人、预言家、女巫等)
- 基于大语言模型的决策系统
- 完整的游戏流程管理
- 详细的日志记录系统

## 支持的角色

- 狼人 (Werewolf)
- 预言家 (Seer) 
- 女巫 (Witch)
- 猎人 (Hunter)
- 守卫 (Guard)
- 普通村民 (Villager)

## 安装说明

1. 克隆仓库
```bash
git clone <repository-url>
cd llm-werewolf
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件,配置必要的环境变量
```

## 使用方法

1. 启动游戏
```bash
python main.py
```

2. 查看日志
```bash
# 日志文件保存在 logs/ 目录下
```

## 配置说明

- 游戏配置文件位于 `data/configs/` 目录
- 可以通过修改配置文件调整:
  - 游戏人数
  - 角色分配
  - AI模型参数
  - 游戏规则

## 开发计划

- [ ] 添加更多角色
- [ ] 优化AI决策系统
- [ ] 添加Web界面
- [ ] 支持多局游戏统计
- [ ] 添加游戏回放功能

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式


```

这个README.md包含了:
1. 项目简介
2. 项目结构
3. 主要特性
4. 支持的角色
5. 安装和使用说明
6. 配置说明
7. 开发计划
8. 贡献指南
9. 许可证信息
10. 联系方式
