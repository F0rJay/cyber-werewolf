# Cyber-Werewolf 🐺

基于 LangGraph 的多智能体编排与博弈系统

## 项目简介

Cyber-Werewolf 是一个使用 LangGraph 构建的狼人杀游戏系统，展示了多智能体系统的设计、状态管理和结构化输出等核心技术。

## 核心特性

- 🎯 **确定性工作流**：基于 LangGraph 的有向循环图，替代不稳定的自由对话模式
- 🔄 **状态管理**：全局 GameState + 条件边路由，解决多智能体交互死循环问题
- 📋 **结构化输出**：Pydantic 约束 + 重试机制，确保 100% 解析成功率
- 🔒 **隐私保护**：分级记忆系统，隔离"狼人频道"与"公共频道"，防止信息泄露

## 项目结构

```
cyber-werewolf/
├── src/              # 源代码
│   ├── agents/       # Agent 实现
│   ├── graph/        # LangGraph 工作流
│   ├── state/        # 状态管理
│   ├── memory/       # 记忆系统
│   ├── schemas/      # 数据模型
│   └── utils/        # 工具函数
├── tests/            # 测试代码
├── examples/         # 示例代码
└── requirements.txt  # 依赖列表
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
python examples/demo_game.py
```

## 开发计划

- [x] 项目结构搭建
- [ ] LangGraph 工作流实现
- [ ] GameState 设计
- [ ] Agent 基础框架
- [ ] 结构化输出 Schema
- [ ] 记忆系统实现
- [ ] 游戏流程节点
- [ ] 测试用例

## 技术栈

- **LangGraph**: 多智能体工作流编排
- **LangChain**: LLM 调用框架
- **DeepSeek-V3**: 主要 LLM（推理能力强，价格便宜，中文理解好）
- **Pydantic**: 结构化输出验证
- **Python 3.10+**: 开发语言

## License

MIT

