# 项目概览

## 项目信息

- **项目名称**: Cyber-Werewolf
- **版本**: 0.3.9
- **作者**: F0rJay
- **描述**: 基于 LangGraph 的多智能体编排与博弈系统
- **许可证**: MIT

## 项目统计

- **代码行数**: ~2500+ 行 Python 代码
- **文件数量**: 28 个 Python 文件
- **文档数量**: 10+ 个 Markdown 文档
- **测试文件**: 6 个测试文件（test_agents.py, test_state.py, test_graph.py, test_roles.py, test_game_rules.py, __init__.py）
- **示例代码**: 4 个示例文件

## 核心模块

### 1. 工作流引擎 (graph/)
- **文件**: `game_graph.py`, `nodes.py`, `edges.py`
- **功能**: LangGraph 工作流定义和节点实现
- **状态**: ✅ 完成

### 2. 状态管理 (state/)
- **文件**: `game_state.py`, `state_manager.py`
- **功能**: 游戏状态定义和管理
- **状态**: ✅ 完成

### 3. Agent 系统 (agents/)
- **文件**: `base_agent.py`, `villager.py`, `werewolf.py`, `roles/*.py`
- **功能**: 各角色智能体实现（含 LLM 集成）
- **状态**: ✅ 完成（LLM 集成已完成）

### 4. 记忆系统 (memory/)
- **文件**: `memory_manager.py`, `filters.py`
- **功能**: 分级记忆管理和信息过滤
- **状态**: ✅ 完成

### 5. 工具函数 (utils/)
- **文件**: `llm_client.py`, `prompt_builder.py`, `agent_factory.py`, `role_assigner.py`, `validators.py`
- **功能**: LLM 调用、Prompt 构建、Agent 工厂、身份分配、验证
- **状态**: ✅ 完成

### 6. 数据模型 (schemas/)
- **文件**: `actions.py`
- **功能**: Pydantic Schema 定义
- **状态**: ✅ 完成

## 功能特性

### ✅ 已实现

1. **完整游戏流程**
   - 身份随机分配
   - 夜晚阶段（狼人、预言家、守卫、女巫）
   - 警长竞选和投票
   - 发言阶段（支持自爆）
   - 放逐投票（支持平票重议）
   - 屠边规则判定

2. **状态管理**
   - 全局 GameState
   - 完整历史记录
   - 投票和发言记录

3. **工作流引擎**
   - LangGraph 有向循环图
   - 条件边路由
   - 熔断机制

4. **记忆系统**
   - 三级记忆（PUBLIC/ROLE/PRIVATE）
   - 信息过滤防止泄露

5. **LLM 集成**
   - DeepSeek-V3 支持
   - OpenAI 支持
   - 结构化输出
   - 角色技能决策 LLM 集成（预言家、女巫、守卫、狼人）
   - 发言系统 LLM 集成（所有 Agent 支持 LLM 生成发言）
   - 投票系统 LLM 集成（所有 Agent 支持 LLM 决策投票）
   - 遗言系统 LLM 集成（所有 Agent 支持 LLM 生成遗言）
   - Prompt 构建工具

6. **测试系统**
   - 单元测试完善（33 个测试通过）
   - Agent 测试（所有角色）
   - 状态管理测试
   - 游戏规则测试
   - 角色技能测试
   - 使用 mock LLM client 支持无 API key 测试

7. **游戏规则完善**
   - 狼人投票平票逻辑修正（平票时从平票玩家中随机选一人攻击）
   - 预言家查验结果修正（只能知道"好人"或"狼人"）
   - 自爆机制规则修正（只有狼人可以自爆，与是否警长无关）
   - 遗言规则实现（第一天夜里出局和放逐的玩家有遗言）
   - 警长移交机制实现（警长出局后可以移交警徽或销毁，LLM 决策）
   - 发言顺序机制完善（警上顺序发言，警长选择顺序/逆序）

### 🚧 待完善

1. **特殊机制**
   - 特殊技能发动（夜里出局玩家的技能）

2. **测试和优化**
   - [x] 单元测试完善（基础测试已完成，包括 Agent、状态管理、游戏规则、角色技能等）
   - [ ] 集成测试
   - [ ] 性能优化

## 技术栈

- **Python**: 3.10+
- **LangGraph**: 工作流编排
- **LangChain**: LLM 调用框架
- **Pydantic**: 数据验证
- **DeepSeek-V3**: 主要 LLM（推荐）
- **OpenAI**: 备选 LLM

## 项目结构

```
cyber-werewolf/
├── src/              # 源代码（1683 行）
├── tests/            # 测试代码
├── examples/         # 示例代码
├── docs/             # 文档（8 个文件）
├── CHANGELOG.md      # 开发日志
├── ARCHITECTURE.md   # 架构设计
└── README.md         # 项目说明
```

## 文档体系

1. **README.md** - 项目主文档
2. **CHANGELOG.md** - 版本更新日志
3. **ARCHITECTURE.md** - 架构设计文档
4. **docs/QUICKSTART.md** - 快速开始指南
5. **docs/LLM_CONFIG.md** - LLM 配置说明
6. **docs/GRAPH_IMPLEMENTATION.md** - 工作流实现说明
7. **docs/GAME_RULES.md** - 游戏规则说明
8. **docs/PROJECT_STRUCTURE.md** - 项目结构说明

## 开发状态

- **当前版本**: 0.3.8
- **开发阶段**: 核心功能完成，所有 LLM 集成完成（角色技能、发言、投票、遗言、警长移交、发言顺序），单元测试完善
- **下一步**: 功能完善（特殊技能发动）、集成测试和性能优化

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

