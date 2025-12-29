"""
Prompt 构建工具：将游戏状态转换为 LLM 可理解的格式
"""
from typing import Dict, Any, List, Optional


def format_player_info(players: List[Any], include_role: bool = False) -> str:
    """
    格式化玩家信息
    
    Args:
        players: 玩家列表
        include_role: 是否包含角色信息（仅对可见角色）
    
    Returns:
        格式化的玩家信息字符串
    """
    if not players:
        return "无玩家"
    
    lines = []
    for p in players:
        if hasattr(p, 'player_id') and hasattr(p, 'name'):
            info = f"玩家{p.player_id} ({p.name})"
            if include_role and hasattr(p, 'role'):
                role_cn = {
                    "villager": "村民",
                    "werewolf": "狼人",
                    "seer": "预言家",
                    "witch": "女巫",
                    "guard": "守卫"
                }.get(p.role, p.role)
                info += f" - {role_cn}"
            if hasattr(p, 'is_alive') and not p.is_alive:
                info += " [已出局]"
            if hasattr(p, 'is_sheriff') and p.is_sheriff:
                info += " [警长]"
            lines.append(info)
    
    return "\n".join(lines) if lines else "无玩家"


def format_game_history(history: List[Dict[str, Any]], limit: int = 5) -> str:
    """
    格式化游戏历史记录
    
    Args:
        history: 历史记录列表
        limit: 最多显示多少条记录
    
    Returns:
        格式化的历史记录字符串
    """
    if not history:
        return "暂无历史记录"
    
    recent_history = history[-limit:] if len(history) > limit else history
    lines = []
    
    for entry in recent_history:
        entry_type = entry.get("type", "unknown")
        day = entry.get("day", "?")
        
        if entry_type == "night_action":
            actions = entry.get("actions", {})
            killed = entry.get("killed", [])
            lines.append(f"第{day}天夜晚：{len(actions)}个行动，{len(killed)}人出局")
        elif entry_type == "discussion":
            discussions = entry.get("discussions", [])
            lines.append(f"第{day}天发言：{len(discussions)}人发言")
        elif entry_type == "exile_voting":
            eliminated = entry.get("eliminated")
            if eliminated:
                lines.append(f"第{day}天放逐：玩家{eliminated}被放逐")
            else:
                lines.append(f"第{day}天放逐：平票或无人出局")
        elif entry_type == "self_explode":
            player_name = entry.get("player_name", "?")
            lines.append(f"第{day}天：{player_name}自爆")
    
    return "\n".join(lines) if lines else "暂无历史记录"


def build_seer_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any]
) -> tuple[str, str]:
    """
    构建预言家查验的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    seer_checks = observation.get("seer_checks", {})
    
    # 格式化已查验的玩家
    checked_info = []
    for target_id, result in seer_checks.items():
        target_player = next((p for p in players if p.player_id == target_id), None)
        if target_player:
            # 预言家只能知道是好人还是狼人
            checked_info.append(f"玩家{target_id} ({target_player.name}) - {result}")
    
    system_prompt = """你是一名狼人杀游戏中的预言家。你的能力是每晚可以查验一名玩家的身份（好人/狼人）。

游戏规则：
- 你是好人阵营，目标是找出并淘汰所有狼人
- 每晚你可以查验一名玩家的真实身份
- 查验结果只有你知道，不能直接告诉其他玩家（需要通过发言暗示）
- 你需要通过查验找出狼人，并引导好人投票淘汰狼人

请根据当前游戏状态，决定今晚查验哪个玩家。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：预言家（玩家{agent_id} - {agent_name}）

存活玩家：
{format_player_info(alive_players)}

已查验结果：
{chr(10).join(checked_info) if checked_info else "暂无查验结果"}

游戏历史：
{format_game_history(game_state.get("history", []))}

请分析当前情况，决定今晚查验哪个玩家。请返回你的决策，包括：
1. 推理过程（为什么选择这个玩家）
2. 目标玩家ID
3. 置信度（0-1）
4. 决策理由"""
    
    return system_prompt, user_prompt


def build_witch_antidote_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any],
    killed_player_id: int
) -> tuple[str, str]:
    """
    构建女巫解药决策的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    killed_player = next((p for p in players if p.player_id == killed_player_id), None)
    
    system_prompt = """你是一名狼人杀游戏中的女巫。你拥有解药和毒药各一瓶。

解药规则：
- 解药可以救活被狼人攻击的玩家
- 解药只能使用一次，使用后永久失效
- 第一夜如果自己被杀，通常应该自救
- 其他夜晚需要判断被杀玩家的价值，决定是否使用解药

请根据当前情况，决定是否使用解药。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：女巫（玩家{agent_id} - {agent_name}）

被杀的玩家：玩家{killed_player_id} ({killed_player.name if killed_player else '未知'})

存活玩家：
{format_player_info([p for p in players if p.is_alive])}

解药状态：{'已使用' if observation.get('antidote_used') else '未使用'}
毒药状态：{'已使用' if observation.get('poison_used') else '未使用'}
是否第一夜：{'是' if observation.get('first_night') else '否'}

游戏历史：
{format_game_history(game_state.get("history", []))}

请分析当前情况，决定是否使用解药救活玩家{killed_player_id}。请返回你的决策，包括：
1. 推理过程
2. 是否使用解药（True/False）
3. 置信度（0-1）
4. 决策理由"""
    
    return system_prompt, user_prompt


def build_witch_poison_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any]
) -> tuple[str, str]:
    """
    构建女巫毒药决策的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    targets = [p for p in alive_players if p.player_id != agent_id]
    
    system_prompt = """你是一名狼人杀游戏中的女巫。你拥有解药和毒药各一瓶。

毒药规则：
- 毒药可以淘汰一名玩家
- 毒药只能使用一次，使用后永久失效
- 毒药不能对自己使用
- 毒药通常用于淘汰疑似狼人的玩家

请根据当前情况，决定是否使用毒药，以及毒谁。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：女巫（玩家{agent_id} - {agent_name}）

存活玩家（可毒目标）：
{format_player_info(targets)}

解药状态：{'已使用' if observation.get('antidote_used') else '未使用'}
毒药状态：{'已使用' if observation.get('poison_used') else '未使用'}

游戏历史：
{format_game_history(game_state.get("history", []))}

请分析当前情况，决定是否使用毒药。如果使用，请选择目标玩家。请返回你的决策，包括：
1. 推理过程
2. 是否使用毒药（True/False）
3. 如果使用，目标玩家ID（如果不用则返回None）
4. 置信度（0-1）
5. 决策理由"""
    
    return system_prompt, user_prompt


def build_guard_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any],
    last_protected_id: Optional[int]
) -> tuple[str, str]:
    """
    构建守卫守护决策的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    targets = [p for p in alive_players if p.player_id != agent_id and p.player_id != last_protected_id]
    
    last_protected_info = ""
    if last_protected_id:
        last_protected = next((p for p in players if p.player_id == last_protected_id), None)
        if last_protected:
            last_protected_info = f"上一晚守护了：玩家{last_protected_id} ({last_protected.name})"
    
    system_prompt = """你是一名狼人杀游戏中的守卫。你的能力是每晚可以守护一名玩家。

守护规则：
- 每晚可以守护一名玩家（包括自己）
- 被守护的玩家如果被狼人攻击，不会死亡
- 不能连续两晚守护同一名玩家
- 守卫不能防御女巫的毒药
- 通常应该守护疑似神职或重要的玩家

请根据当前情况，决定今晚守护哪个玩家。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：守卫（玩家{agent_id} - {agent_name}）

存活玩家（可守护目标，不能连续两晚守护同一人）：
{format_player_info(targets)}

{last_protected_info if last_protected_info else "上一晚未守护任何人"}

游戏历史：
{format_game_history(game_state.get("history", []))}

请分析当前情况，决定今晚守护哪个玩家。请返回你的决策，包括：
1. 推理过程
2. 目标玩家ID（如果不守护则返回None）
3. 置信度（0-1）
4. 决策理由"""
    
    return system_prompt, user_prompt


def build_werewolf_discuss_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any],
    werewolf_teammates: List[Any]
) -> tuple[str, str]:
    """
    构建狼人频道讨论的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    non_werewolves = [p for p in alive_players if p.role != "werewolf"]
    
    teammates_info = format_player_info(werewolf_teammates, include_role=True)
    
    system_prompt = """你是狼人杀游戏中的狼人。你属于狼人阵营，目标是淘汰所有好人（村民和神职）。

狼人频道规则：
- 这是只有狼人才能看到的频道
- 你可以和队友讨论策略
- 讨论内容不会被好人看到
- 讨论后需要投票决定攻击目标

请根据当前情况，在狼人频道发言，与队友讨论今晚的攻击策略。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：狼人（玩家{agent_id} - {agent_name}）

狼人队友：
{teammates_info if teammates_info else "无队友（你是唯一狼人）"}

存活的好人玩家：
{format_player_info(non_werewolves)}

游戏历史：
{format_game_history(game_state.get("history", []))}

请在狼人频道发言，与队友讨论今晚的攻击策略。发言应该：
1. 分析当前局势
2. 提出攻击建议
3. 与队友协调行动"""
    
    return system_prompt, user_prompt


def build_werewolf_vote_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any],
    werewolf_teammates: List[Any],
    werewolf_channel_messages: List[Dict[str, Any]]
) -> tuple[str, str]:
    """
    构建狼人投票决策的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    targets = [p for p in alive_players if p.role != "werewolf"]
    
    # 格式化狼人频道讨论
    channel_discussion = ""
    if werewolf_channel_messages:
        channel_lines = []
        for msg in werewolf_channel_messages:
            player_name = msg.get("player_name", "?")
            message = msg.get("message", "")
            channel_lines.append(f"{player_name}: {message}")
        channel_discussion = "\n".join(channel_lines)
    
    system_prompt = """你是狼人杀游戏中的狼人。在狼人频道讨论后，你需要投票决定今晚攻击哪个玩家。

投票规则：
- 每个狼人独立投票
- 得票最多的玩家被攻击
- 如果平票，则平安夜（无人被攻击）
- 需要根据讨论内容和游戏状态做出决策

请根据讨论和当前情况，决定投票攻击哪个玩家。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：狼人（玩家{agent_id} - {agent_name}）

狼人频道讨论：
{channel_discussion if channel_discussion else "暂无讨论"}

可攻击的目标玩家：
{format_player_info(targets)}

游戏历史：
{format_game_history(game_state.get("history", []))}

请根据讨论和当前情况，决定投票攻击哪个玩家。请返回你的决策，包括：
1. 推理过程
2. 目标玩家ID（如果不攻击则返回None）
3. 置信度（0-1）
4. 决策理由"""
    
    return system_prompt, user_prompt


def build_werewolf_explode_prompt(
    agent_id: int,
    agent_name: str,
    game_state: Dict[str, Any]
) -> tuple[str, str]:
    """
    构建狼人自爆决策的 prompt
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    
    system_prompt = """你是狼人杀游戏中的狼人。你可以在发言阶段自爆。

自爆规则：
- 自爆后立即出局
- 自爆后发言终止，直接进入黑夜
- 自爆通常用于：
  1. 身份即将暴露时，阻止好人投票
  2. 保护队友，牺牲自己
  3. 战术需要，打乱好人节奏

请根据当前情况，决定是否自爆。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：狼人（玩家{agent_id} - {agent_name}）

存活玩家：
{format_player_info(alive_players)}

游戏历史：
{format_game_history(game_state.get("history", []))}

当前发言阶段，请分析情况，决定是否自爆。请返回你的决策，包括：
1. 推理过程
2. 是否自爆（True/False）
3. 置信度（0-1）
4. 决策理由"""
    
    return system_prompt, user_prompt


def build_speak_prompt(
    agent_id: int,
    agent_name: str,
    agent_role: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any],
    context: str = "normal"  # "normal", "sheriff_campaign", "sheriff_pk"
) -> tuple[str, str]:
    """
    构建玩家发言的 prompt
    
    Args:
        agent_id: Agent ID
        agent_name: Agent 名称
        agent_role: Agent 角色
        game_state: 游戏状态
        observation: Agent 观察到的信息
        context: 发言上下文（normal=正常发言, sheriff_campaign=警长竞选, sheriff_pk=警长PK）
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    day_number = game_state.get("day_number", 1)
    
    role_cn = {
        "villager": "村民",
        "werewolf": "狼人",
        "seer": "预言家",
        "witch": "女巫",
        "guard": "守卫"
    }.get(agent_role, agent_role)
    
    # 根据上下文构建不同的 system prompt
    if context == "sheriff_campaign":
        system_prompt = f"""你是狼人杀游戏中的{role_cn}（玩家{agent_id} - {agent_name}）。你正在警长竞选阶段发言。

发言规则：
- 你需要说明为什么竞选警长，以及你的优势
- 可以分析当前局势，表达你的观点
- 发言后可以选择"退水"（退出竞选）或继续竞选
- 发言应该真实、有逻辑，符合你的角色身份

请根据当前情况，进行警长竞选发言。"""
    elif context == "sheriff_pk":
        system_prompt = f"""你是狼人杀游戏中的{role_cn}（玩家{agent_id} - {agent_name}）。你正在警长投票平票PK发言阶段。

发言规则：
- 你需要与平票的候选人进行PK发言
- 需要说明为什么你应该当选警长
- 可以分析对手的问题，表达你的优势
- 发言应该真实、有逻辑，符合你的角色身份

请根据当前情况，进行PK发言。"""
    else:
        system_prompt = f"""你是狼人杀游戏中的{role_cn}（玩家{agent_id} - {agent_name}）。你正在白天发言阶段。

发言规则：
- 你需要分析当前局势，表达你的观点
- 可以质疑其他玩家，为自己辩护
- 发言应该真实、有逻辑，符合你的角色身份
- 如果你是好人，需要帮助找出狼人
- 如果你是狼人，需要隐藏身份，误导好人

请根据当前情况，进行发言。"""
    
    # 获取最近的发言记录
    discussions = game_state.get("discussions", [])
    recent_discussions = discussions[-5:] if len(discussions) > 5 else discussions
    
    discussion_text = ""
    if recent_discussions:
        discussion_lines = []
        for d in recent_discussions:
            speaker_name = d.get("player_name", "?")
            content = d.get("content", "")
            discussion_lines.append(f"{speaker_name}: {content}")
        discussion_text = "\n".join(discussion_lines)
    
    user_prompt = f"""当前游戏状态：

你的身份：{role_cn}（玩家{agent_id} - {agent_name}）

存活玩家：
{format_player_info(alive_players)}

当前是第{day_number}天

最近的发言记录：
{discussion_text if discussion_text else "暂无发言记录"}

游戏历史：
{format_game_history(game_state.get("history", []))}

请根据当前情况，进行发言。发言应该：
1. 分析当前局势
2. 表达你的观点和推理
3. 符合你的角色身份
4. 真实、有逻辑

请返回你的发言内容。"""
    
    return system_prompt, user_prompt


def build_vote_prompt(
    agent_id: int,
    agent_name: str,
    agent_role: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any],
    vote_type: str = "exile",  # "exile", "sheriff"
    candidates: Optional[List[int]] = None
) -> tuple[str, str]:
    """
    构建玩家投票的 prompt
    
    Args:
        agent_id: Agent ID
        agent_name: Agent 名称
        agent_role: Agent 角色
        game_state: 游戏状态
        observation: Agent 观察到的信息
        vote_type: 投票类型（exile=放逐投票, sheriff=警长投票）
        candidates: 候选人列表（仅用于警长投票）
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    day_number = game_state.get("day_number", 1)
    
    role_cn = {
        "villager": "村民",
        "werewolf": "狼人",
        "seer": "预言家",
        "witch": "女巫",
        "guard": "守卫"
    }.get(agent_role, agent_role)
    
    if vote_type == "sheriff":
        # 警长投票
        if candidates:
            candidate_players = [p for p in alive_players if p.player_id in candidates]
        else:
            candidate_players = []
        
        system_prompt = f"""你是狼人杀游戏中的{role_cn}（玩家{agent_id} - {agent_name}）。你正在警长投票阶段。

投票规则：
- 你需要从候选人中选择一个作为警长
- 警长拥有1.5票的投票权，且可以选择发言顺序
- 需要根据候选人的发言和表现做出决策
- 不能投票给自己（如果你不是候选人）

请根据候选人的表现，决定投票给谁。"""
        
        user_prompt = f"""当前游戏状态：

你的身份：{role_cn}（玩家{agent_id} - {agent_name}）

警长候选人：
{format_player_info(candidate_players) if candidate_players else "无候选人"}

存活玩家：
{format_player_info(alive_players)}

当前是第{day_number}天

游戏历史：
{format_game_history(game_state.get("history", []))}

请根据候选人的发言和表现，决定投票给哪个候选人。请返回你的决策，包括：
1. 推理过程
2. 目标候选人ID（如果不投票则返回None）
3. 置信度（0-1）
4. 决策理由"""
    else:
        # 放逐投票
        tie_vote_round = game_state.get("tie_vote_round", 0)
        tied_players = game_state.get("tied_players", [])
        
        if tie_vote_round > 0 and tied_players:
            # 平票重议，只能投票给平票的玩家
            voting_targets = [p for p in alive_players if p.player_id in tied_players]
            vote_context = f"平票重议第{tie_vote_round}轮，只能投票给平票的玩家"
        else:
            # 正常投票
            voting_targets = [p for p in alive_players if p.player_id != agent_id]
            vote_context = "正常放逐投票"
        
        system_prompt = f"""你是狼人杀游戏中的{role_cn}（玩家{agent_id} - {agent_name}）。你正在放逐投票阶段。

投票规则：
- 你需要投票决定放逐哪个玩家
- 得票最多的玩家被放逐
- 需要根据发言和游戏表现做出决策
- 不能投票给自己

请根据当前情况，决定投票放逐哪个玩家。"""
        
        user_prompt = f"""当前游戏状态：

你的身份：{role_cn}（玩家{agent_id} - {agent_name}）

投票上下文：{vote_context}

可投票的目标玩家：
{format_player_info(voting_targets) if voting_targets else "无目标玩家"}

存活玩家：
{format_player_info(alive_players)}

当前是第{day_number}天

游戏历史：
{format_game_history(game_state.get("history", []))}

请根据发言和游戏表现，决定投票放逐哪个玩家。请返回你的决策，包括：
1. 推理过程
2. 目标玩家ID（如果不投票则返回None）
3. 置信度（0-1）
4. 决策理由"""
    
    return system_prompt, user_prompt


def build_last_words_prompt(
    agent_id: int,
    agent_name: str,
    agent_role: str,
    game_state: Dict[str, Any],
    observation: Dict[str, Any],
    death_reason: str  # "night_first" 或 "exile"
) -> tuple[str, str]:
    """
    构建遗言 prompt
    
    Args:
        agent_id: Agent ID
        agent_name: Agent 名称
        agent_role: Agent 角色
        game_state: 游戏状态
        observation: Agent 观察到的信息
        death_reason: 出局原因（"night_first"=第一天夜里出局, "exile"=被放逐）
    
    Returns:
        (system_prompt, user_prompt)
    """
    players = game_state.get("players", [])
    alive_players = [p for p in players if p.is_alive]
    day_number = game_state.get("day_number", 1)
    
    role_cn = {
        "villager": "村民",
        "werewolf": "狼人",
        "seer": "预言家",
        "witch": "女巫",
        "guard": "守卫"
    }.get(agent_role, agent_role)
    
    if death_reason == "night_first":
        context = "第一天夜里出局"
    else:
        context = "被放逐出局"
    
    system_prompt = f"""你是狼人杀游戏中的{role_cn}（玩家{agent_id} - {agent_name}）。你刚刚{context}，现在需要留下遗言。

遗言规则：
- 遗言是你最后一次向其他玩家传递信息的机会
- 可以分析局势，指出可疑的玩家
- 可以为自己辩护，或者为队友提供信息
- 遗言应该真实、有逻辑，符合你的角色身份
- 如果你是好人，可以帮助好人阵营找出狼人
- 如果你是狼人，可以误导好人，保护队友

请根据当前情况，留下你的遗言。"""
    
    user_prompt = f"""当前游戏状态：

你的身份：{role_cn}（玩家{agent_id} - {agent_name}）
出局原因：{context}
当前是第{day_number}天

存活玩家：
{format_player_info(alive_players)}

游戏历史：
{format_game_history(game_state.get("history", []))}

请根据当前情况，留下你的遗言。遗言应该：
1. 分析当前局势
2. 表达你的观点和推理
3. 符合你的角色身份
4. 真实、有逻辑

请返回你的遗言内容。"""
    
    return system_prompt, user_prompt

