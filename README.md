# Cyber-Werewolf 🐺

基于 LangGraph 的多智能体编排与博弈系统

## 项目简介

Cyber-Werewolf 是一个使用 LangGraph 构建的狼人杀游戏系统，展示了多智能体系统的设计、状态管理和结构化输出等核心技术。

## 核心特性

- 🎯 **确定性工作流**：基于 LangGraph 的有向循环图，替代不稳定的自由对话模式
- 🔄 **状态管理**：全局 GameState + 条件边路由，解决多智能体交互死循环问题
- 📋 **结构化输出**：Pydantic 约束 + 重试机制，确保 100% 解析成功率
- 🔒 **隐私保护**：分级记忆系统，隔离"狼人频道"与"公共频道"，防止信息泄露
- 🤖 **完整 LLM 集成**：所有 Agent 决策（技能、发言、投票）均由 LLM 智能决策

## 项目结构

```
cyber-werewolf/
├── src/                    # 源代码
│   ├── agents/            # Agent 实现
│   │   ├── base_agent.py  # Agent 基类
│   │   ├── villager.py    # 村民 Agent
│   │   ├── werewolf.py    # 狼人 Agent（含 LLM 集成）
│   │   └── roles/         # 特殊角色（预言家、女巫、守卫，含 LLM 集成）
│   ├── graph/             # LangGraph 工作流
│   │   ├── game_graph.py      # 工作流主图
│   │   ├── nodes.py           # 节点实现
│   │   └── edges.py           # 条件边实现
│   ├── state/              # 状态管理
│   │   ├── game_state.py   # 游戏状态定义
│   │   └── state_manager.py # 状态管理器
│   ├── memory/             # 记忆系统
│   │   ├── memory_manager.py # 记忆管理器
│   │   └── filters.py        # 信息过滤
│   ├── schemas/            # 数据模型（Pydantic）
│   │   └── actions.py      # Agent 行动指令 Schema
│   └── utils/              # 工具函数
│       ├── llm_client.py    # LLM 客户端（DeepSeek/OpenAI）
│       ├── prompt_builder.py # Prompt 构建工具
│       ├── agent_factory.py  # Agent 工厂
│       ├── role_assigner.py # 身份分配
│       └── validators.py    # 验证器
├── tests/                  # 测试代码
├── examples/               # 示例代码
│   ├── run_game.py         # 完整游戏运行
│   └── test_deepseek.py    # DeepSeek API 测试
├── docs/                   # 文档
│   ├── LLM_CONFIG.md       # LLM 配置说明
│   ├── QUICKSTART.md       # 快速开始指南
│   ├── GRAPH_IMPLEMENTATION.md # 工作流实现说明
│   └── GAME_RULES.md       # 游戏规则说明
├── CHANGELOG.md            # 开发日志
├── requirements.txt        # 依赖列表
└── README.md              # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# DeepSeek-V3 API（推荐：价格便宜，中文理解好）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1  # 可选，默认值

# 或使用 OpenAI（备选）
# OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 运行示例

```bash
# 运行完整游戏
python examples/run_game.py

# 测试 DeepSeek API 连接
python examples/test_deepseek.py
```

## 文档

- [快速开始指南](docs/QUICKSTART.md)
- [LLM 配置说明](docs/LLM_CONFIG.md)
- [工作流实现说明](docs/GRAPH_IMPLEMENTATION.md) - 工作流详解
- [游戏规则说明](docs/GAME_RULES.md)
- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [架构设计文档](ARCHITECTURE.md)
- [开发日志](CHANGELOG.md)

## 开发状态

- [x] 项目结构搭建
- [x] LangGraph 工作流实现
- [x] GameState 设计
- [x] Agent 基础框架
- [x] 结构化输出 Schema
- [x] 记忆系统实现
- [x] 游戏流程节点
- [x] 身份分配系统
- [x] 警长机制
- [x] 平票重议机制
- [x] 屠边规则
- [x] 角色技能系统（预言家、女巫、守卫、狼人）
- [x] Agent LLM 集成（技能决策）
- [x] 发言系统 LLM 集成
- [x] 投票系统 LLM 集成
- [ ] 测试用例完善

## 技术栈

- **LangGraph**: 多智能体工作流编排
- **LangChain**: LLM 调用框架
- **DeepSeek-V3**: 主要 LLM（推理能力强，价格便宜，中文理解好）
- **Pydantic**: 结构化输出验证
- **Python 3.10+**: 开发语言

## License

MIT

