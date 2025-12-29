# LangGraph 工作流实现说明

## 概述

已实现完整的 LangGraph 工作流，支持多智能体狼人杀游戏的确定性流程编排。

## 工作流结构

### 节点（Nodes）

1. **init_node** - 游戏初始化节点
   - 初始化游戏状态
   - 设置初始阶段和轮次
   - 记录游戏开始历史

2. **state_check_node** - 状态检查节点
   - 检查熔断机制（最大轮次限制）
   - 防止游戏无限循环
   - 检查游戏是否已结束

3. **discussion_node** - 发言阶段节点
   - 按顺序让所有存活玩家发言
   - 记录发言内容到历史
   - 为后续 Agent 集成预留接口

4. **voting_node** - 投票阶段节点
   - 收集所有存活玩家的投票
   - 统计投票结果
   - 处理平票情况
   - 淘汰得票最多的玩家

5. **night_node** - 夜晚行动节点
   - 狼人选择攻击目标
   - 神职角色行动（预言家、女巫、守卫）
   - 执行夜晚结果
   - 进入新的一天

6. **judgment_node** - 结果判定节点
   - 判断游戏胜负条件
   - 检查存活玩家数量
   - 确定获胜方
   - 记录游戏结束历史

### 条件边（Conditional Edges）

1. **check_game_end** - 游戏结束检测
   - 检查游戏状态是否为 "ended"
   - 检查存活玩家数量（狼人/村民比例）
   - 返回 "end" 或 "continue"

2. **check_tie_vote** - 平票检测
   - 检测投票是否平票
   - 连续平票3次后随机淘汰
   - 返回 "replay" 或 "continue"

3. **route_after_voting** - 投票后路由
   - 判断进入夜晚、重议或判定结果
   - 处理游戏结束和平票情况

4. **route_after_night** - 夜晚后路由
   - 判断进入新的一天或判定结果
   - 处理游戏结束情况

## 工作流程图

```
[init] 
  ↓
[state_check] 
  ↓ (continue)
[discussion] 
  ↓
[voting] 
  ↓ (night/replay/judgment)
  ├─→ [night] → [state_check] (循环)
  ├─→ [discussion] (重议)
  └─→ [judgment] → [END]
```

## 状态管理

### GameState 扩展

新增字段：
- `votes`: 投票记录 `{voter_id: target_id}`
- `vote_results`: 投票统计 `{target_id: vote_count}`
- `discussions`: 发言记录列表
- `current_speaker`: 当前发言玩家ID
- `night_actions`: 夜晚行动记录
- `max_rounds`: 最大轮次限制（熔断机制）
- `consecutive_ties`: 连续平票次数

## 核心特性

### 1. 确定性工作流

- 使用 LangGraph 替代自由对话模式
- 明确的节点和边定义
- 可预测的游戏流程

### 2. 条件路由

- 游戏结束自动检测
- 平票重议机制
- 阶段自动切换（白天/夜晚）

### 3. 熔断机制

- 最大轮次限制（默认20轮）
- 防止游戏无限循环
- 连续平票处理（3次后随机淘汰）

### 4. 状态持久化

- 完整的历史记录
- 投票和发言记录
- 夜晚行动记录

## 使用示例

```python
from src.state.game_state import StateManager, Player
from src.graph.game_graph import create_game_graph

# 创建玩家
players = [
    Player(player_id=1, name="玩家1", role="villager"),
    Player(player_id=2, name="玩家2", role="werewolf"),
    # ...
]

# 初始化状态
state_manager = StateManager()
initial_state = state_manager.init_state(players, max_rounds=10)

# 创建并运行游戏图
graph = create_game_graph()
final_state = await graph.ainvoke(initial_state)
```

## 运行示例

```bash
python examples/run_game.py
```

## 待完善功能

1. **Agent 集成**
   - 在 `discussion_node` 中调用 Agent 的发言逻辑
   - 在 `voting_node` 中调用 Agent 的投票逻辑
   - 在 `night_node` 中调用各角色的行动逻辑

2. **结构化输出**
   - 使用 Pydantic Schema 验证 Agent 输出
   - 实现重试机制确保解析成功率

3. **记忆系统**
   - 在节点中集成分级记忆系统
   - 根据角色过滤可见信息

4. **错误处理**
   - 添加异常处理机制
   - 实现降级策略

## 技术亮点

- ✅ 基于 LangGraph 的有向循环图
- ✅ 条件边实现复杂业务路由
- ✅ 全局状态管理（GameState）
- ✅ 熔断机制防止死循环
- ✅ 完整的历史记录系统

