# 项目结构说明

## 目录结构

### `/src` - 源代码目录

#### `/src/agents` - Agent 实现
- `base_agent.py`: Agent 抽象基类，定义 `observe`、`think`、`act` 接口
- `villager.py`: 村民角色 Agent 实现
- `werewolf.py`: 狼人角色 Agent 实现
- `roles/`: 特殊角色 Agent（预言家、女巫、守卫）- 待实现

#### `/src/graph` - LangGraph 工作流
- `game_graph.py`: 工作流主图（完整游戏流程）
- `nodes.py`: 节点实现（完整游戏流程）
- `edges.py`: 条件边实现（游戏结束、平票检测等）

#### `/src/state` - 状态管理
- `game_state.py`: 游戏状态定义（TypedDict + Player 模型）
- `state_manager.py`: 状态管理器（已整合到 game_state.py）

#### `/src/memory` - 记忆系统
- `memory_manager.py`: 记忆管理器，支持三级记忆（PUBLIC/ROLE/PRIVATE）
- `filters.py`: 信息过滤函数，防止信息泄露

#### `/src/schemas` - 数据模型
- `actions.py`: Agent 行动指令 Pydantic Schema
- `game_state.py`: 游戏状态 Schema（已整合到 state/game_state.py）

#### `/src/utils` - 工具函数
- `llm_client.py`: LLM 客户端封装（支持 DeepSeek-V3 和 OpenAI）
- `role_assigner.py`: 身份分配工具
- `validators.py`: 验证器（带重试机制）

### `/tests` - 测试代码
- `test_agents.py`: Agent 测试
- `test_graph.py`: 工作流测试
- `test_state.py`: 状态管理测试

### `/examples` - 示例代码
- `run_game.py`: 完整游戏运行
- `test_deepseek.py`: DeepSeek API 连接测试

### `/docs` - 文档
- `LLM_CONFIG.md`: LLM 配置详细说明
- `QUICKSTART.md`: 快速开始指南
- `GRAPH_IMPLEMENTATION.md`: 工作流实现说明
- `GAME_RULES.md`: 完整游戏规则说明

## 文件命名规范

- **模块文件**: 小写字母，下划线分隔（如 `game_state.py`）
- **类名**: 大驼峰（如 `GameState`, `BaseAgent`）
- **函数名**: 小写字母，下划线分隔（如 `create_game_graph`）
- **常量**: 全大写，下划线分隔（如 `MAX_ROUNDS`）

## 代码组织原则

1. **模块化**: 每个功能模块独立，职责清晰
2. **可扩展**: 易于添加新角色、新功能
3. **可测试**: 每个模块都有对应的测试
4. **文档化**: 关键功能都有文档说明

## 版本管理

- **V1 版本**: 基础实现，用于快速原型
- **V2 版本**: 完整实现，用于正式开发
- 两个版本可以共存，便于对比和迁移

## 依赖关系

```
src/
├── agents/ (依赖: utils, schemas, state)
├── graph/ (依赖: state, agents, utils)
├── state/ (独立)
├── memory/ (独立)
├── schemas/ (独立)
└── utils/ (独立)
```

## 扩展指南

### 添加新角色
1. 在 `src/agents/roles/` 创建新的 Agent 类
2. 继承 `BaseAgent`
3. 实现 `observe`、`think`、`act` 方法
4. 在 `role_assigner.py` 中添加角色配置

### 添加新节点
1. 在 `src/graph/nodes.py` 添加新节点函数
2. 在 `src/graph/game_graph.py` 注册节点
3. 添加相应的条件边

### 添加新功能
1. 在相应模块添加功能代码
2. 更新 `GameState` 如果需要新状态
3. 添加测试用例
4. 更新文档

