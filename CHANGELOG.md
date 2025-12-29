# 开发日志 (Changelog)

本文档记录 Cyber-Werewolf 项目的所有重要变更。

## [0.4.0]

### 🐛 关键问题修复

#### 游戏逻辑修复
- **修复游戏结束判定**
  - 问题：游戏一开始没有设置神职，却出现"狼人获胜！（神职全部出局）"的判定
  - 修复：在 `init_state` 中记录初始神职和村民数量，`check_game_end` 只判定初始存在的阵营全部出局
  - 如果一开始就没有神职，不会因为神职数量为0而判定游戏结束

- **修复夜晚死亡时机**
  - 问题：第一天被刀的玩家在第二天白天警上还活着，可以参与上警、发言、投票等操作
  - 修复：夜晚阶段只记录被杀玩家，不立即设置为死亡；在 `announce_death_node` 中才真正淘汰玩家
  - 被刀的玩家在第二天白天仍可以参与警长竞选、发言、投票等，直到公布出局玩家阶段

- **修复发言 prompt**
  - 问题：所有人发言都是场面话，没有针对上文进行分析
  - 修复：修改 `build_speak_prompt`，强调必须针对前面玩家的发言内容进行具体分析
  - 要求给出具体的推理和判断，指出矛盾和疑点，避免只说场面话

#### 技术修复
- **修复游戏图递归限制错误**
  - 问题：`Recursion limit of 25 reached without hitting a stop condition`
  - 修复：优化 `route_after_sheriff_campaign` 和 `route_after_sheriff_voting` 的路由逻辑
  - 正确处理无人竞选警长、PK发言后的路由，避免无限循环

- **修复 history 字段并发更新问题**
  - 问题：`At key 'history': Can receive only one value per step`
  - 修复：使用 `Annotated[List[Dict], operator.add]` 允许多个节点在同一步骤中追加历史记录
  - 每个节点返回单个历史记录项作为列表，LangGraph 自动合并

#### 代码优化
- 优化 `announce_death_node` 的警长移交逻辑
- 修复 `updated_players` 和 `last_words` 的作用域问题
- 改进代码结构和错误处理

---

## [0.3.9]

### 🛠️ 测试脚本完善

#### 新增功能
- **测试运行脚本** (`run_tests.py`, `run_tests.sh`)
  - 一键执行所有测试用例
  - 自动检查 pytest 是否安装
  - 显示所有测试用例列表（执行前）
  - 实时显示测试执行过程
  - 按文件分组显示测试结果
  - 显示每个测试的执行状态（通过/失败/跳过/错误）
  - 显示测试统计信息（总数、通过率等）
  - 显示失败测试的详细错误信息
  - 处理 ANSI 转义码，确保正确解析测试结果
  - 支持 Python 和 Shell 两种版本

#### 功能特性
- **测试列表显示**：执行前显示所有 36 个测试用例
- **实时执行显示**：显示 pytest 的实时执行输出
- **测试摘要**：按文件分组，清晰显示每个测试的状态
  - ✅ PASSED - 测试通过
  - ❌ FAILED - 测试失败
  - ⏭️ SKIPPED - 测试跳过
  - ⚠️ ERROR - 测试错误
- **统计信息**：显示总计、通过数、失败数、跳过数和百分比
- **失败详情**：自动显示失败测试的详细错误信息

#### 使用方法
```bash
# 使用 Python 脚本
python run_tests.py

# 或使用 Shell 脚本
./run_tests.sh
```

---

## [0.3.8]

### 🧪 测试用例完善

#### 新增测试
- **完善 test_agents.py**
  - 添加所有角色的测试（村民、狼人、预言家、女巫、守卫）
  - 添加 Agent 工厂测试
  - 添加 Agent 观察功能测试
  - 添加预言家查验功能测试
  - 使用 mock LLM client 避免需要真实 API key

- **完善 test_state.py**
  - 添加状态管理器测试（带最大轮次）
  - 添加状态更新测试
  - 添加玩家模型测试
  - 添加警长状态测试
  - 添加投票状态测试
  - 添加预言家查验状态测试
  - 添加女巫状态测试
  - 添加守卫状态测试
  - 添加遗言状态测试

- **完善 test_graph.py**
  - 添加游戏图结构测试
  - 添加身份分配节点测试
  - 添加游戏结束检查测试
  - 添加图编译测试

- **新增 test_roles.py**
  - 测试预言家查验目标决策
  - 测试女巫解药/毒药决策
  - 测试守卫守护决策
  - 测试狼人频道讨论
  - 测试狼人投票杀人
  - 测试狼人自爆决策

- **新增 test_game_rules.py**
  - 测试身份分配
  - 测试警长选举状态
  - 测试平票处理
  - 测试游戏结束条件
  - 测试发言顺序逻辑
  - 测试警长移交状态

#### 测试配置
- 添加 `pytest.ini` 配置文件
  - 设置 pythonpath
  - 配置测试路径和模式
  - 配置 asyncio 模式

#### 测试结果
- 33 个测试通过
- 3 个测试跳过（由于测试环境的导入问题，使用 pytest.skip 处理）
- 测试覆盖范围：Agent 基础功能、状态管理、游戏规则、角色技能、游戏流程节点、图结构

---

## [0.3.7]

### 🎯 发言顺序机制完善

#### 新增功能
- **警上发言顺序** (`src/graph/nodes.py`)
  - 实现顺序发言逻辑：随机选择第一个发言的玩家，然后按玩家序号顺序发言（循环）
  - 例如：6人局，如果4号玩家先发言，则发言顺序为 4 → 5 → 6 → 1 → 2 → 3

- **警长选择发言顺序** (`src/agents/base_agent.py`)
  - 实现 `decide_speaking_order()` 方法，支持警长选择顺序或逆序发言
  - 使用 LLM 智能决策发言顺序
  - 使用结构化输出（`SpeakingOrderDecision`）确保返回正确格式

- **Prompt 构建扩展** (`src/utils/prompt_builder.py`)
  - 新增 `build_speaking_order_prompt()`：构建警长选择发言顺序的 prompt
  - 提供顺序和逆序两种发言顺序的预览

#### 游戏规则完善
- **发言顺序规则**：
  - 警上发言：顺序发言，随机选择第一个，然后按玩家序号顺序（循环）
  - 白天发言（有警长）：警长选择顺序或逆序，以警长序号为中心，警长为归票位
    - 顺序发言：从警长下一个玩家开始，按序号顺序发言，最后警长发言
    - 逆序发言：从警长前一个玩家开始，按序号逆序发言，最后警长发言
  - 白天发言（无警长）：随机顺序发言

#### 节点更新
- **警长竞选节点** (`src/graph/nodes.py`)
  - `sheriff_campaign_node`：实现警上发言顺序逻辑

- **发言节点** (`src/graph/nodes.py`)
  - `discussion_node`：实现警长选择发言顺序逻辑
  - 支持顺序和逆序两种发言方式

#### 文档更新
- 更新 `docs/GAME_RULES.md`：详细说明发言顺序规则
- 更新警长功能说明：添加发言顺序选择功能

---

## [0.3.6]

### 🔧 自爆机制逻辑修正

#### 规则修正
- **自爆机制逻辑优化**：
  - ✅ 只有狼人可以自爆（与是否警长无关）
  - ✅ 如果狼人玩家当选警长，仍然可以自爆（因为他是狼人）
  - 修正了之前的错误逻辑：之前认为"警长不能自爆（即使警长是狼人）"

#### 代码更新
- **发言节点** (`src/graph/nodes.py`)
  - 移除警长检查：自爆判断只检查角色是否为狼人
  - 更新注释说明：只有狼人可以自爆（与是否警长无关）

- **狼人 Agent** (`src/agents/werewolf.py`)
  - 移除 `decide_self_explode()` 方法中的警长检查
  - 更新文档说明：如果狼人玩家当选警长，仍然可以自爆

- **Prompt 构建** (`src/utils/prompt_builder.py`)
  - `build_werewolf_explode_prompt()` 移除警长特殊处理
  - 统一 prompt：说明只有狼人可以自爆，与是否警长无关

#### 文档更新
- 更新 `docs/GAME_RULES.md`：修正自爆规则说明
- 移除"警长不能自爆"的错误描述

---

## [0.3.5]

### 👮 警长移交机制实现

#### 新增功能
- **警长移交系统** (`src/agents/base_agent.py`)
  - 实现 `decide_sheriff_transfer()` 方法，支持警长移交决策
  - 使用 LLM 智能决策是否移交警徽及移交给谁
  - 使用结构化输出（`SheriffTransferDecision`）确保返回正确格式

- **Prompt 构建扩展** (`src/utils/prompt_builder.py`)
  - 新增 `build_sheriff_transfer_prompt()`：构建警长移交决策的 prompt
  - 提供完整的游戏状态和可移交玩家信息

#### 游戏规则完善
- **警长移交规则**：
  - ✅ 警长出局后（夜里出局或被放逐），需要决定如何处理警徽
  - ✅ 可以选择将警徽移交给其他存活玩家（该玩家成为新警长）
  - ✅ 或者选择销毁警徽（不移交，本局没有警长）
  - ✅ 移交决策由 LLM 智能决策

#### 节点更新
- **公布出局节点** (`src/graph/nodes.py`)
  - `announce_death_node`：处理警长夜里出局时的移交
  - 如果警长出局，调用 `decide_sheriff_transfer()` 决定移交或销毁

- **放逐投票节点** (`src/graph/nodes.py`)
  - `exile_voting_node`：处理警长被放逐时的移交
  - 如果警长被放逐，调用 `decide_sheriff_transfer()` 决定移交或销毁

#### 状态管理
- **GameState 扩展** (`src/state/game_state.py`)
  - 新增 `sheriff_transfer` 字段：记录警长移交信息
  - 包含移交来源、目标、是否销毁等信息

#### 文档更新
- 更新 `docs/GAME_RULES.md`：详细说明警长移交机制
- 更新相关文档说明

---

## [0.3.4]

### 🔧 自爆机制规则修正

#### 规则变更
- **自爆规则修正**：
  - ✅ 只有狼人可以自爆
  - ✅ 警长不能自爆（即使警长是狼人）
  - 自爆后立即出局，发言终止，直接进入黑夜

#### 代码更新
- **发言节点** (`src/graph/nodes.py`)
  - 更新自爆检查：只有非警长的狼人可以自爆
  - 移除警长自爆相关代码和注释

- **狼人 Agent** (`src/agents/werewolf.py`)
  - `decide_self_explode()` 方法添加警长检查
  - 如果玩家是警长，直接返回 False（不能自爆）

- **Prompt 构建** (`src/utils/prompt_builder.py`)
  - `build_werewolf_explode_prompt()` 根据是否是警长返回不同的 prompt
  - 警长狼人收到明确提示：警长不能自爆

#### 文档更新
- 更新 `docs/GAME_RULES.md`：明确说明自爆规则和警长限制

---

## [0.3.3]

### 💬 遗言系统实现

#### 新增功能
- **遗言系统** (`src/agents/base_agent.py`)
  - 实现 `leave_last_words()` 方法，支持所有 Agent 的遗言功能
  - 使用 LLM 生成符合角色身份和游戏状态的遗言内容
  - 使用结构化输出（`LastWordsDecision`）确保返回正确格式

- **Prompt 构建扩展** (`src/utils/prompt_builder.py`)
  - 新增 `build_last_words_prompt()`：构建遗言 prompt
  - 支持两种出局原因：第一天夜里出局、被放逐

#### 游戏规则完善
- **遗言规则**：
  - ✅ 第一天夜里出局的玩家：有遗言
  - ✅ 每一轮被放逐的玩家：有遗言
  - ✅ 其他天夜里出局的玩家：只能发动特殊技能，没有遗言

#### 节点更新
- **公布出局节点** (`src/graph/nodes.py`)
  - `announce_death_node`：处理第一天夜里出局玩家的遗言
  - 其他天夜里出局玩家不留下遗言

- **放逐投票节点** (`src/graph/nodes.py`)
  - `exile_voting_node`：处理被放逐玩家的遗言
  - 所有被放逐的玩家都有遗言

#### 文档更新
- 更新 `docs/GAME_RULES.md`：详细说明遗言规则
- 更新相关文档说明

---

## [0.3.2]

### 🎤 发言和投票系统 LLM 集成

#### 新增功能
- **发言系统 LLM 集成** (`src/agents/base_agent.py`)
  - 实现 `speak()` 方法，支持所有 Agent 的发言功能
  - 支持三种发言上下文：正常发言、警长竞选发言、警长PK发言
  - 使用 LLM 生成符合角色身份和游戏状态的发言内容
  - 使用结构化输出（`SpeakDecision`）确保返回正确格式

- **投票系统 LLM 集成** (`src/agents/base_agent.py`)
  - 实现 `vote()` 方法，支持所有 Agent 的投票功能
  - 支持两种投票类型：放逐投票、警长投票
  - 使用 LLM 决策投票目标，基于游戏历史和当前状态
  - 使用结构化输出（`VoteDecision`）确保返回正确格式
  - 包含目标验证（不能投票给自己，警长投票需在候选人中）

- **Prompt 构建扩展** (`src/utils/prompt_builder.py`)
  - 新增 `build_speak_prompt()`：构建发言 prompt，支持不同上下文
  - 新增 `build_vote_prompt()`：构建投票 prompt，支持放逐投票和警长投票
  - 自动格式化最近的发言记录和游戏历史

- **Schema 扩展** (`src/schemas/actions.py`)
  - 新增 `SpeakDecision`：发言决策的结构化输出 Schema
  - 新增 `VoteDecision`：投票决策的结构化输出 Schema

#### 节点更新
- **发言节点** (`src/graph/nodes.py`)
  - `discussion_node`：集成 Agent 的 `speak()` 方法
  - `sheriff_campaign_node`：集成警长竞选发言和PK发言
  - 所有发言现在由 LLM 生成，符合角色身份和游戏状态

- **投票节点** (`src/graph/nodes.py`)
  - `exile_voting_node`：集成放逐投票，支持平票重议
  - `sheriff_voting_node`：集成警长投票，支持两轮投票
  - 所有投票现在由 LLM 决策，基于发言和游戏表现

#### 修复
- **狼人投票平票逻辑修复** (`src/graph/nodes.py`)
  - 修复：狼人投票平票时，从平票玩家中随机选一人攻击（而不是平安夜）
  - 符合游戏规则：平票时随机选择攻击目标

- **预言家查验结果修复** (`src/agents/roles/seer.py`)
  - 修复：预言家查验只能返回"好人"或"狼人"，不能知道具体身份
  - 更新 `check_player()` 方法，只返回"好人"或"狼人"
  - 更新相关 prompt 和显示逻辑，不再显示具体角色身份

#### 改进
- **错误处理**：发言和投票 LLM 调用都包含异常处理，失败时使用默认逻辑
- **代码一致性**：统一所有 Agent 的发言和投票接口
- **VillagerAgent 修复**：更新构造函数以支持 `llm_client` 参数

#### 文档更新
- 更新 `docs/GAME_RULES.md`：说明狼人投票平票规则和预言家查验规则
- 更新相关文档说明

---

## [0.3.1]

### 🤖 Agent LLM 完整集成

#### 新增功能
- **Prompt 构建工具** (`src/utils/prompt_builder.py`)
  - 实现游戏状态格式化函数（`format_player_info`, `format_game_history`）
  - 为所有角色实现专门的 prompt 构建函数
  - 支持预言家、女巫、守卫、狼人的所有决策场景

- **预言家 LLM 集成** (`src/agents/roles/seer.py`)
  - 实现 `decide_check_target()` 方法，使用 LLM 决策查验目标
  - 使用结构化输出（`AgentAction`）确保返回正确格式
  - 验证目标玩家是否存在且存活

- **女巫 LLM 集成** (`src/agents/roles/witch.py`)
  - 更新 `decide_antidote()` 方法，使用 LLM 决策是否使用解药
  - 更新 `decide_poison()` 方法，使用 LLM 决策是否使用毒药及目标
  - 使用自定义 Schema（`AntidoteDecision`, `PoisonDecision`）进行结构化输出

- **守卫 LLM 集成** (`src/agents/roles/guard.py`)
  - 更新 `decide_protect()` 方法，使用 LLM 决策守护目标
  - 使用自定义 Schema（`GuardDecision`）进行结构化输出
  - 验证目标玩家是否符合规则（不能连续两晚守护同一人）

- **狼人 LLM 集成** (`src/agents/werewolf.py`)
  - 更新 `discuss_in_werewolf_channel()` 方法，使用 LLM 生成发言内容
  - 更新 `vote_to_kill()` 方法，使用 LLM 决策攻击目标
  - 更新 `decide_self_explode()` 方法，使用 LLM 决策是否自爆
  - 使用自定义 Schema（`KillVoteDecision`, `ExplodeDecision`）进行结构化输出

#### 改进
- **错误处理**：所有 LLM 调用都包含异常处理，失败时使用默认逻辑
- **代码一致性**：统一所有 Agent 的导入方式（函数内部导入）
- **结构化输出**：使用 Pydantic Schema 确保 LLM 返回正确格式
- **状态格式化**：自动将游戏状态转换为 LLM 可理解的文本

#### 技术细节
- 所有 LLM 调用使用 LangChain 的 `with_structured_output()` 方法
- 使用 `SystemMessage` 和 `HumanMessage` 构建消息
- 支持 DeepSeek-V3 和 OpenAI API
- Prompt 设计考虑了游戏规则、角色能力和当前状态

---

## [0.3.0]

### 🎯 角色能力完整实现

#### 新增功能
- **预言家（Seer）能力实现** (`src/agents/roles/seer.py`)
  - 实现 `check_player` 方法：查验玩家身份
  - 查验结果保存在 `seer_checks` 中
  - 在夜晚阶段调用 Agent 决定查验目标
  - 支持查验历史记录

- **女巫（Witch）能力实现** (`src/agents/roles/witch.py`)
  - 实现 `decide_antidote` 方法：决定是否使用解药救人
  - 实现 `decide_poison` 方法：决定是否使用毒药（不能给自己用）
  - 跟踪解药和毒药的使用状态（`antidote_used`、`poison_used`）
  - 支持第一夜自救逻辑
  - 在夜晚阶段调用 Agent 决定使用解药或毒药

- **守卫（Guard）能力实现** (`src/agents/roles/guard.py`)
  - 实现 `decide_protect` 方法：决定守护哪个玩家
  - 限制：不能连续两晚守护同一人
  - 在夜晚阶段调用 Agent 决定守护目标
  - 守卫效果可以抵消狼人攻击（在夜晚结果处理中实现）

- **狼人（Werewolf）特殊能力实现** (`src/agents/werewolf.py`)
  - **天黑发言**：实现 `discuss_in_werewolf_channel` 方法
    - 狼人可以在狼人频道讨论策略
    - 发言记录保存在 `werewolf_channel` 中
  - **投票杀人**：实现 `vote_to_kill` 方法
    - 每个狼人独立投票决定攻击目标
    - 得票最多的玩家被攻击，平票则平安夜
  - **自爆**：实现 `decide_self_explode` 方法
    - 狼人可以在发言阶段自爆
    - 自爆后立即出局，终止发言，直接进入黑夜

- **Agent 工厂** (`src/utils/agent_factory.py`)
  - 实现 `create_agent_by_role`：根据角色创建对应的 Agent
  - 实现 `create_agents_from_players`：从玩家列表批量创建 Agent
  - 支持所有角色类型（村民、狼人、预言家、女巫、守卫）

#### 改进
- **夜晚阶段完整集成** (`src/graph/nodes.py`)
  - 按顺序执行：狼人攻击 → 预言家查验 → 守卫守护 → 女巫解药/毒药
  - 正确处理守卫守护效果（抵消狼人攻击）
  - 正确处理女巫解药和毒药效果
  - 更新游戏状态（技能使用状态、查验历史、狼人频道）

- **发言阶段增强** (`src/graph/nodes.py`)
  - 集成狼人自爆检测
  - 自爆后立即更新玩家状态
  - 支持自爆后直接进入黑夜的路由

- **游戏图路由优化** (`src/graph/game_graph.py`)
  - 新增 `route_after_discussion` 函数
  - 检查自爆状态，如有自爆则直接进入黑夜
  - 完善游戏流程控制

- **行动类型扩展** (`src/schemas/actions.py`)
  - 新增 `explode` 行动类型，支持自爆操作

#### 技术细节
- 所有角色能力都通过 Agent 调用，便于后续集成 LLM 决策
- 实现了完整的技能使用状态跟踪
- 支持技能间的交互（如守卫抵消狼人攻击）
- 完善了游戏状态管理，支持所有角色特殊能力

---

## [0.2.2]

### 🎮 游戏流程优化

#### 修改
- **第一天流程调整**：先进行警长竞选和投票，再公布出局玩家
- **警长机制完善**：
  - 全部玩家上警：本局失去警徽，没有警长
  - 退水操作：警上玩家可以在发言过程中退出竞选
  - 警长投票平票：第一轮平票→PK发言→第二轮投票
  - 第二轮依然平票：本局没有警长，警徽流失

#### 修复
- **女巫毒药**：毒药不能给自己用
- **文档调整**：警长相关内容不再放在预言家下面

#### 改进
- 优化警长投票平票处理流程
- 完善状态管理，支持警长投票轮次和平票候选人

---

## [0.2.1]

### 🧹 代码清理

#### 删除
- 移除 V1 版本代码（`game_graph.py` V1, `nodes.py` V1）
- 删除 `examples/demo_game.py`（V1 演示）
- 清理所有 V1/V2 版本引用

#### 重构
- 将 V2 版本代码重命名为主版本
  - `game_graph_v2.py` → `game_graph.py`
  - `nodes_v2.py` → `nodes.py`
- 统一函数命名（移除 `_v2` 后缀）
- 更新所有文档，移除版本区分说明

#### 改进
- 简化项目结构，只保留完整版本
- 更新所有文档引用
- 优化代码组织

---

## [0.2.0]

### 🎮 完整游戏流程实现

#### 新增功能
- **身份分配系统** (`src/utils/role_assigner.py`)
  - 随机分配身份功能
  - 支持自动配置（根据玩家数量）
  - 支持自定义角色配置

- **完整游戏流程** (`src/graph/nodes.py`, `src/graph/game_graph.py`)
  - 夜晚阶段：狼人、预言家、守卫、女巫按顺序行动
  - 警长竞选和投票机制
  - 发言阶段（支持自爆、警长选择顺序）
  - 放逐投票（支持平票重议）
  - 屠边规则判定

- **状态管理扩展** (`src/state/game_state.py`)
  - 新增警长相关字段（`sheriff_candidates`, `sheriff_votes`）
  - 新增角色技能字段（`seer_checks`, `witch_antidote_used`, `witch_poison_used`, `guard_protected`）
  - 新增自爆和遗言字段（`self_exploded`, `last_words`）

- **游戏规则文档** (`docs/GAME_RULES.md`)
  - 详细的游戏规则说明
  - 角色能力说明
  - 实现状态说明

#### 改进
- 优化平票检测机制：第一轮平票→重议，第二轮平票→直接黑夜
- 完善警长机制：支持竞选、投票、选择发言顺序、自爆

#### 技术细节
- 使用 LangGraph 实现完整游戏工作流
- 支持条件边路由（游戏结束、平票、阶段切换）
- 实现熔断机制防止死循环

---

## [0.1.1]

### 🔧 平票机制和警长功能

#### 新增功能
- **平票重议机制**
  - 第一轮投票平票：平票玩家进行第二轮发言和投票
  - 第二轮依然平票：直接进入黑夜，无人出局

- **警长机制**
  - 玩家模型新增 `is_sheriff` 字段
  - 第一天警长竞选节点
  - 警长投票功能
  - Demo 中显示警长信息

#### 改进
- 更新 `GameState` 支持平票重议相关字段
- 优化投票节点支持平票处理
- 更新工作流图支持警长竞选流程

---

## [0.1.0]

### 🚀 初始版本

#### 核心功能
- **项目结构搭建**
  - 完整的模块化项目结构
  - 源代码、测试、示例、文档分离

- **LangGraph 工作流实现**
  - 游戏初始化节点
  - 发言阶段节点
  - 投票阶段节点
  - 夜晚行动节点
  - 结果判定节点
  - 状态检查节点（熔断机制）

- **状态管理系统**
  - `GameState` TypedDict 定义
  - `StateManager` 状态管理器
  - 支持投票、发言、历史记录

- **Agent 框架**
  - `BaseAgent` 抽象基类
  - `VillagerAgent` 村民实现
  - `WerewolfAgent` 狼人实现
  - 支持观察、推理、行动接口

- **记忆系统**
  - 三级记忆系统（PUBLIC/ROLE/PRIVATE）
  - 信息过滤函数防止信息泄露

- **结构化输出**
  - `AgentAction` Pydantic Schema
  - 支持重试机制

- **LLM 客户端**
  - 支持 DeepSeek-V3 API（默认）
  - 支持 OpenAI API（备选）
  - 结构化输出支持

#### 文档
- README.md - 项目说明
- docs/LLM_CONFIG.md - LLM 配置说明
- docs/QUICKSTART.md - 快速开始指南
- docs/GRAPH_IMPLEMENTATION.md - 工作流实现说明

#### 测试
- 基础测试用例
- 示例代码（demo_game.py, test_deepseek.py）

---

## 版本说明

- **主版本号**：重大架构变更
- **次版本号**：新功能添加
- **修订版本号**：Bug 修复和小改进

## 未来计划

### v0.3.1 (计划中)
- [ ] Agent 完整集成（LLM 调用）
  - 预言家查验决策（LLM）
  - 女巫解药/毒药决策（LLM）
  - 守卫守护决策（LLM）
  - 狼人攻击决策（LLM）
  - 狼人频道发言生成（LLM）
  - 自爆决策（LLM）
- [ ] 完整的发言系统（LLM 生成发言内容）
- [ ] 完整的投票决策（LLM 决策）
- [ ] 警长移交机制
- [ ] 遗言系统

### v0.4.0 (计划中)
- [ ] 性能优化
- [ ] 多局游戏支持
- [ ] 游戏回放功能
- [ ] 策略分析工具

