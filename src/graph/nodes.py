"""
LangGraph 节点实现 - 完整游戏流程
"""
from typing import Dict, Any, List, Optional
from ..state.game_state import GameState, Player
import asyncio
import random


async def role_assignment_node(state: GameState) -> Dict[str, Any]:
    """身份分配节点"""
    print("🎲 随机分配身份...")
    
    # 如果玩家已经有身份，跳过
    if state.get("players") and any(p.role for p in state["players"]):
        return {}
    
    # TODO: 这里应该从配置或输入获取玩家名称
    # 目前使用占位符
    player_names = [f"玩家{i}" for i in range(1, len(state.get("players", [])) + 1)]
    
    from ..utils.role_assigner import assign_roles
    players = assign_roles(player_names)
    
    print("✅ 身份分配完成：")
    for p in players:
        role_cn = {"villager": "村民", "werewolf": "狼人", "seer": "预言家", 
                  "witch": "女巫", "guard": "守卫"}.get(p.role, p.role)
        print(f"  {p.name}: {role_cn}")
    
    return {"players": players}


async def night_phase_node(state: GameState) -> Dict[str, Any]:
    """夜晚阶段节点"""
    day_number = state.get("day_number", 1)
    print(f"\n🌙 夜晚阶段 - 第 {day_number} 天")
    print("=" * 60)
    
    alive_players = [p for p in state["players"] if p.is_alive]
    night_actions = {}
    killed_players = []
    
    # 按角色分组
    werewolves = [p for p in alive_players if p.role == "werewolf"]
    seers = [p for p in alive_players if p.role == "seer"]
    witches = [p for p in alive_players if p.role == "witch"]
    guards = [p for p in alive_players if p.role == "guard"]
    
    # 1. 狼人和预言家先行动
    print("\n📋 第一阶段：狼人和预言家行动")
    
    # 狼人行动（天黑发言 + 投票杀人）
    if werewolves:
        print(f"  🐺 狼人团队行动（{len(werewolves)}人）")
        
        # 1. 狼人频道发言（天黑讨论）
        print(f"    💬 狼人频道讨论：")
        werewolf_channel_messages = []
        werewolf_agents = {}
        
        from ..utils.agent_factory import create_agent_by_role
        
        for wolf in werewolves:
            # 创建狼人 Agent
            wolf_agent = create_agent_by_role(wolf.player_id, wolf.name, "werewolf")
            werewolf_agents[wolf.player_id] = wolf_agent
            
            # 获取可见信息
            observation = await wolf_agent.observe(state)
            werewolf_teammates = observation.get("werewolf_teammates", [])
            
            # 在狼人频道发言
            message = await wolf_agent.discuss_in_werewolf_channel(
                state, 
                werewolf_teammates
            )
            werewolf_channel_messages.append({
                "player_id": wolf.player_id,
                "player_name": wolf.name,
                "message": message
            })
            print(f"      {wolf.name}: {message}")
            await asyncio.sleep(0.1)
        
    # 狼人频道信息将在返回时更新到游戏状态
        
        # 2. 狼人投票决定攻击目标
        print(f"    🗳️  狼人投票决定攻击目标：")
        werewolf_votes = {}
        
        for wolf in werewolves:
            wolf_agent = werewolf_agents[wolf.player_id]
            observation = await wolf_agent.observe(state)
            werewolf_teammates = observation.get("werewolf_teammates", [])
            
            # 投票决定攻击目标
            target_id = await wolf_agent.vote_to_kill(
                state,
                werewolf_teammates,
                werewolf_channel_messages
            )
            
            if target_id:
                werewolf_votes[wolf.player_id] = target_id
                target_player = next((p for p in alive_players if p.player_id == target_id), None)
                if target_player:
                    print(f"      {wolf.name} 投票攻击: {target_player.name} (玩家{target_id})")
        
        # 统计狼人投票结果
        if werewolf_votes:
            vote_counts = {}
            for target_id in werewolf_votes.values():
                vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
            
            # 得票最多的被攻击（平票则从平票玩家中随机选一人攻击）
            if vote_counts:
                max_votes = max(vote_counts.values())
                attacked_players = [pid for pid, votes in vote_counts.items() if votes == max_votes]
                
                if len(attacked_players) == 1:
                    attacked_id = attacked_players[0]
                else:
                    # 平票：从平票玩家中随机选一人攻击
                    attacked_id = random.choice(attacked_players)
                    print(f"    ⚠️  狼人投票平票，从平票玩家中随机选择: {attacked_players}")
                
                attacked_player = next((p for p in alive_players if p.player_id == attacked_id), None)
                if attacked_player:
                    night_actions["werewolf"] = {
                        "target": attacked_id,
                        "votes": werewolf_votes,
                        "vote_counts": vote_counts
                    }
                    killed_players.append(attacked_id)
                    print(f"    ✅ 狼人团队决定攻击: {attacked_player.name} (玩家{attacked_id})")
        else:
            print(f"    ⚠️  狼人未选择攻击目标，平安夜")
    
    # 预言家行动（查验）
    if seers:
        seer = seers[0]
        print(f"  🔮 预言家行动: {seer.name}")
        
        # 创建预言家 Agent（如果还没有）
        from ..utils.agent_factory import create_agent_by_role
        seer_agent = create_agent_by_role(seer.player_id, seer.name, "seer")
        
        # 获取可见信息
        observation = await seer_agent.observe(state)
        
        # 调用 Agent 决定查验目标（使用 LLM）
        target_id = await seer_agent.decide_check_target(state)
        
        if target_id:
            target_player = next((p for p in alive_players if p.player_id == target_id), None)
            
            if target_player:
                # 执行查验
                check_result = await seer_agent.check_player(state, target_id)
                check_result_value = check_result.get(target_id, "未知")
                
                # 更新查验历史
                seer_checks = state.get("seer_checks", {})
                seer_checks.update(check_result)
                
                night_actions["seer"] = {
                    "target": target_id,
                    "result": check_result_value,  # "好人" 或 "狼人"
                    "agent_id": seer.player_id
                }
                print(f"    预言家查验: {target_player.name} (玩家{target_id}) - {check_result_value}")
                
                # 更新查验历史（不提前返回，继续执行守卫和女巫）
                state["seer_checks"] = seer_checks
        else:
            # 预言家选择不查验或无效目标
            print(f"    预言家选择不查验")
    
    # 2. 守卫行动（在女巫之前）
    if guards:
        guard = guards[0]
        print(f"\n🛡️  守卫行动: {guard.name}")
        
        # 创建守卫 Agent
        from ..utils.agent_factory import create_agent_by_role
        guard_agent = create_agent_by_role(guard.player_id, guard.name, "guard")
        
        # 获取上一晚守护的玩家
        last_protected = state.get("guard_protected")
        
        # 获取可见信息
        observation = await guard_agent.observe(state)
        
        # 调用 Agent 决定守护目标
        protect_target_id = await guard_agent.decide_protect(state, last_protected)
        
        if protect_target_id:
            target_player = next((p for p in alive_players if p.player_id == protect_target_id), None)
            if target_player:
                night_actions["guard"] = {
                    "target": protect_target_id,
                    "agent_id": guard.player_id
                }
                print(f"    守卫守护: {target_player.name} (玩家{protect_target_id})")
        else:
            print(f"    守卫选择不守护")
    
    # 3. 女巫后行动
    if witches:
        witch = witches[0]
        print(f"\n🧪 女巫行动: {witch.name}")
        
        # 创建女巫 Agent
        from ..utils.agent_factory import create_agent_by_role
        witch_agent = create_agent_by_role(witch.player_id, witch.name, "witch")
        
        # 检查是否有人被杀
        someone_killed = len(killed_players) > 0
        killed_player_id = killed_players[0] if killed_players else None
        antidote_used = state.get("witch_antidote_used", False)
        poison_used = state.get("witch_poison_used", False)
        
        # 更新女巫 Agent 状态
        witch_agent.antidote_used = antidote_used
        witch_agent.poison_used = poison_used
        witch_agent.first_night = (day_number == 1)
        
        # 获取可见信息
        observation = await witch_agent.observe(state)
        
        # 决定是否使用解药
        if someone_killed and not antidote_used:
            use_antidote = await witch_agent.decide_antidote(state, killed_player_id)
            if use_antidote:
                # 解药救人：从被杀列表中移除
                if killed_player_id in killed_players:
                    killed_players.remove(killed_player_id)
                night_actions["witch"] = {
                    "antidote": True,
                    "target": killed_player_id,
                    "agent_id": witch.player_id
                }
                witch_agent.antidote_used = True
                print(f"    女巫使用解药救: 玩家{killed_player_id}")
        
        # 决定是否使用毒药（不能给自己用）
        if not poison_used:
            poison_target_id = await witch_agent.decide_poison(state)
            if poison_target_id:
                # 毒药不能给自己用（已在 decide_poison 中处理）
                killed_players.append(poison_target_id)
                night_actions.setdefault("witch", {})["poison"] = True
                night_actions.setdefault("witch", {})["poison_target"] = poison_target_id
                night_actions.setdefault("witch", {})["agent_id"] = witch.player_id
                witch_agent.poison_used = True
                target_player = next((p for p in alive_players if p.player_id == poison_target_id), None)
                if target_player:
                    print(f"    女巫使用毒药: {target_player.name} (玩家{poison_target_id})")
        
        # 更新状态中的女巫技能使用情况（不提前返回，继续执行夜晚结果处理）
        if witch_agent.antidote_used:
            state["witch_antidote_used"] = True
        if witch_agent.poison_used:
            state["witch_poison_used"] = True
    
    # 处理守卫守护效果：如果被守护的玩家被狼人攻击，则不受伤害
    guard_protected_tonight = night_actions.get("guard", {}).get("target")
    werewolf_target = night_actions.get("werewolf", {}).get("target")
    
    # 如果守卫守护了被狼人攻击的目标，则抵消伤害
    if guard_protected_tonight and werewolf_target == guard_protected_tonight:
        if werewolf_target in killed_players:
            killed_players.remove(werewolf_target)
            print(f"    🛡️  守卫成功守护了玩家{werewolf_target}，抵消了狼人攻击")
    
    # 处理女巫解药和毒药效果（已在女巫行动中处理）
    # 注意：守卫不能防御女巫毒药
    
    # 执行夜晚结果：淘汰被杀的玩家
    updated_players = []
    for p in state["players"]:
        if p.player_id in killed_players:
            updated_p = Player(
                player_id=p.player_id,
                name=p.name,
                role=p.role,
                is_alive=False,
                vote_target=p.vote_target,
                is_sheriff=p.is_sheriff
            )
            updated_players.append(updated_p)
        else:
            updated_players.append(p)
    
    # 记录夜晚行动
    history_entry = {
        "type": "night_action",
        "day": day_number,
        "actions": night_actions,
        "killed": killed_players,
        "guard_protected": guard_protected_tonight,
    }
    
    current_history = state.get("history", [])
    current_history.append(history_entry)
    
    # 准备返回的更新
    updates = {
        "night_actions": night_actions,
        "history": current_history,
        "players": updated_players,
        "current_phase": "day",
        "guard_protected": state.get("guard_protected_tonight"),  # 更新为上一晚
        "guard_protected_tonight": guard_protected_tonight,  # 今晚守护的
    }
    
    # 更新女巫技能使用状态
    if state.get("witch_antidote_used"):
        updates["witch_antidote_used"] = True
    if state.get("witch_poison_used"):
        updates["witch_poison_used"] = True
    
    # 更新预言家查验历史
    if state.get("seer_checks"):
        updates["seer_checks"] = state["seer_checks"]
    
    # 更新狼人频道信息（如果有狼人发言）
    if werewolves:
        # 从局部变量获取狼人频道消息（如果存在）
        if "werewolf_channel_messages" in locals():
            current_werewolf_channel = state.get("werewolf_channel", {})
            current_werewolf_channel[f"night_{day_number}"] = werewolf_channel_messages
            updates["werewolf_channel"] = current_werewolf_channel
    
    return updates


async def announce_death_node(state: GameState) -> Dict[str, Any]:
    """公布出局玩家节点"""
    day_number = state.get("day_number", 1)
    print(f"\n📢 公布出局玩家 - 第 {day_number} 天")
    
    # 找出昨晚出局的玩家
    last_night_action = None
    for entry in reversed(state.get("history", [])):
        if entry.get("type") == "night_action":
            last_night_action = entry
            break
    
    killed_players = []
    if last_night_action:
        killed_players = last_night_action.get("killed", [])
    
    if killed_players:
        print("  出局玩家：")
        for pid in killed_players:
            player = next((p for p in state["players"] if p.player_id == pid), None)
            if player:
                print(f"    ❌ {player.name} (玩家{pid}) - {player.role}")
                # TODO: 选择发动技能、留下遗言
    else:
        print("  ✅ 平安夜（无人出局）")
    
    return {}


async def sheriff_campaign_node(state: GameState) -> Dict[str, Any]:
    """警长竞选节点（第一天）"""
    day_number = state.get("day_number", 1)
    sheriff_vote_round = state.get("sheriff_vote_round", 0)
    sheriff_tied_candidates = state.get("sheriff_tied_candidates", [])
    sheriff_withdrawn = state.get("sheriff_withdrawn", [])
    
    # 只在第一天进行警长竞选
    if day_number > 1:
        return {}
    
    # 如果是PK发言阶段
    if sheriff_vote_round == 1 and sheriff_tied_candidates:
        print(f"\n👮 警长投票平票PK发言阶段")
        print("=" * 60)
        print(f"  平票候选人: {[f'玩家{pid}' for pid in sheriff_tied_candidates]}")
        
        alive_players = [p for p in state["players"] if p.is_alive]
        pk_candidates = [p for p in alive_players if p.player_id in sheriff_tied_candidates]
        
        # PK发言
        print(f"\n  PK发言（{len(pk_candidates)}人）：")
        random.shuffle(pk_candidates)
        from ..utils.agent_factory import create_agent_by_role
        for candidate in pk_candidates:
            print(f"    {candidate.name} (玩家{candidate.player_id}) 正在PK发言...")
            # 调用 Agent 发言逻辑
            agent = create_agent_by_role(candidate.player_id, candidate.name, candidate.role)
            content = await agent.speak(state, context="sheriff_pk")
            print(f"      💬 {content}")
            await asyncio.sleep(0.1)
        
        return {}
    
    # 正常警长竞选阶段
    print(f"\n👮 警长竞选阶段")
    print("=" * 60)
    
    alive_players = [p for p in state["players"] if p.is_alive]
    
    # 玩家选择是否竞选警长
    print("  玩家选择是否竞选警长：")
    candidates = []
    for player in alive_players:
        # TODO: 调用 Agent 决定是否竞选
        # 目前随机决定
        will_campaign = random.choice([True, False])
        if will_campaign:
            candidates.append(player.player_id)
            print(f"    ✅ {player.name} (玩家{player.player_id}) 选择竞选")
        else:
            print(f"    ❌ {player.name} (玩家{player.player_id}) 不竞选")
    
    # 如果全部玩家上警，则本局失去警徽
    if len(candidates) == len(alive_players):
        print(f"\n  ⚠️  全部玩家上警竞选，本局失去警徽，没有警长")
        return {
            "sheriff_candidates": [],
            "sheriff_votes": {},
        }
    
    if not candidates:
        print("  ⚠️  无人竞选警长，本局没有警长")
        return {
            "sheriff_candidates": [],
            "sheriff_votes": {},
        }
    
    # 竞选者发言（随机顺序），支持退水
    print(f"\n  竞选者发言（{len(candidates)}人，可退水）：")
    random.shuffle(candidates)
    final_candidates = []
    
    for candidate_id in candidates:
        candidate = next((p for p in alive_players if p.player_id == candidate_id), None)
        if candidate:
            print(f"    {candidate.name} (玩家{candidate_id}) 正在发言...")
            # 调用 Agent 发言逻辑
            from ..utils.agent_factory import create_agent_by_role
            agent = create_agent_by_role(candidate.player_id, candidate.name, candidate.role)
            content = await agent.speak(state, context="sheriff_campaign")
            print(f"      💬 {content}")
            
            # 退水操作（随机模拟，TODO: 可以集成到 LLM 决策中）
            will_withdraw = random.choice([False])  # 模拟（暂时不退水）
            if will_withdraw:
                sheriff_withdrawn.append(candidate_id)
                print(f"      💧 {candidate.name} 退水")
            else:
                final_candidates.append(candidate_id)
            
            await asyncio.sleep(0.1)
    
    # 如果全部退水，则没有警长
    if len(final_candidates) == 0:
        print(f"\n  ⚠️  全部竞选者退水，本局没有警长")
        return {
            "sheriff_candidates": [],
            "sheriff_votes": {},
            "sheriff_withdrawn": sheriff_withdrawn,
        }
    
    return {
        "sheriff_candidates": final_candidates,
        "sheriff_withdrawn": sheriff_withdrawn,
    }


async def sheriff_voting_node(state: GameState) -> Dict[str, Any]:
    """警长投票节点"""
    candidates = state.get("sheriff_candidates", [])
    sheriff_vote_round = state.get("sheriff_vote_round", 0)
    sheriff_tied_candidates = state.get("sheriff_tied_candidates", [])
    
    # 如果是第二轮投票，使用平票候选人
    if sheriff_vote_round == 1 and sheriff_tied_candidates:
        candidates = sheriff_tied_candidates
    
    if not candidates:
        return {}
    
    if sheriff_vote_round == 0:
        print(f"\n🗳️  警长投票阶段（第一轮）")
    else:
        print(f"\n🗳️  警长投票阶段（第二轮）")
    
    print(f"  候选人: {[f'玩家{pid}' for pid in candidates]}")
    
    alive_players = [p for p in state["players"] if p.is_alive]
    sheriff_votes = {}
    
    # 所有玩家投票
    from ..utils.agent_factory import create_agent_by_role
    for player in alive_players:
        # 调用 Agent 投票逻辑
        agent = create_agent_by_role(player.player_id, player.name, player.role)
        target = await agent.vote(state, vote_type="sheriff", candidates=candidates)
        if target:
            sheriff_votes[player.player_id] = target
            candidate_name = next((p.name for p in alive_players if p.player_id == target), f"玩家{target}")
            print(f"    {player.name} 投票给 {candidate_name}")
        else:
            print(f"    {player.name} 弃权")
    
    # 统计投票结果
    vote_counts = {}
    for candidate_id in sheriff_votes.values():
        vote_counts[candidate_id] = vote_counts.get(candidate_id, 0) + 1
    
    # 找出得票最多的候选人
    if vote_counts:
        max_votes = max(vote_counts.values())
        winners = [cid for cid, votes in vote_counts.items() if votes == max_votes]
        
        if len(winners) == 1:
            sheriff_id = winners[0]
            # 更新玩家状态，设置警长
            updated_players = []
            for p in state["players"]:
                if p.player_id == sheriff_id:
                    updated_p = Player(
                        player_id=p.player_id,
                        name=p.name,
                        role=p.role,
                        is_alive=p.is_alive,
                        vote_target=p.vote_target,
                        is_sheriff=True
                    )
                    updated_players.append(updated_p)
                    print(f"\n  ✅ {p.name} (玩家{sheriff_id}) 当选警长！")
                else:
                    updated_players.append(p)
            
            return {
                "players": updated_players,
                "sheriff_votes": sheriff_votes,
                "sheriff_vote_round": 0,  # 重置
                "sheriff_tied_candidates": [],
            }
        else:
            # 平票情况
            if sheriff_vote_round == 0:
                # 第一轮平票：进入PK发言
                print(f"\n  ⚠️  警长投票平票！平票候选人: {winners}")
                print(f"  进入PK发言阶段...")
                return {
                    "sheriff_votes": sheriff_votes,
                    "sheriff_vote_round": 1,
                    "sheriff_tied_candidates": winners,
                }
            else:
                # 第二轮依然平票：警徽流失
                print(f"\n  ⚠️  第二轮投票依然平票！本局没有警长，警徽流失")
                return {
                    "sheriff_votes": sheriff_votes,
                    "sheriff_vote_round": 0,
                    "sheriff_tied_candidates": [],
                    "sheriff_candidates": [],  # 清空候选人
                }
    
    return {"sheriff_votes": sheriff_votes}



async def discussion_node(state: GameState) -> Dict[str, Any]:
    """发言阶段节点（支持警长选择顺序、自爆）"""
    day_number = state.get("day_number", 1)
    print(f"\n💬 发言阶段 - 第 {day_number} 天")
    print("=" * 60)
    
    alive_players = [p for p in state["players"] if p.is_alive]
    
    # 检查是否有警长，如果有则警长选择发言顺序
    sheriff = next((p for p in alive_players if p.is_sheriff), None)
    if sheriff:
        print(f"  👮 警长 {sheriff.name} 选择发言顺序")
        # TODO: 调用警长 Agent 选择发言顺序
        # 目前随机顺序
        random.shuffle(alive_players)
        # 警长可以选择自爆
        # TODO: 调用警长 Agent 决定是否自爆
    else:
        # 无警长，随机顺序
        random.shuffle(alive_players)
    
    discussions = []
    
    # 按顺序发言
    from ..utils.agent_factory import create_agent_by_role
    
    for player in alive_players:
        # 检查是否有狼人自爆（之前已经自爆）
        if state.get("self_exploded"):
            exploded_id = state["self_exploded"]
            exploded_player = next((p for p in alive_players if p.player_id == exploded_id), None)
            if exploded_player:
                print(f"\n  💥 {exploded_player.name} (玩家{exploded_id}) 自爆！发言终止，直接进入黑夜")
            break
        
        # 创建对应角色的 Agent
        agent = create_agent_by_role(player.player_id, player.name, player.role)
        
        # 狼人可以随时自爆
        if player.role == "werewolf":
            # 调用狼人 Agent 决定是否自爆
            will_explode = await agent.decide_self_explode(state, player.player_id)
            if will_explode:
                print(f"\n  💥 {player.name} (狼人) 自爆！发言终止，直接进入黑夜")
                
                # 更新玩家状态：自爆的狼人立即出局
                updated_players = []
                for p in state["players"]:
                    if p.player_id == player.player_id:
                        updated_p = Player(
                            player_id=p.player_id,
                            name=p.name,
                            role=p.role,
                            is_alive=False,  # 自爆后立即出局
                            vote_target=p.vote_target,
                            is_sheriff=p.is_sheriff
                        )
                        updated_players.append(updated_p)
                    else:
                        updated_players.append(p)
                
                # 记录历史
                history_entry = {
                    "type": "self_explode",
                    "day": day_number,
                    "player_id": player.player_id,
                    "player_name": player.name,
                    "role": player.role,
                }
                current_history = state.get("history", [])
                current_history.append(history_entry)
                
                return {
                    "self_exploded": player.player_id,
                    "players": updated_players,
                    "history": current_history,
                    "current_phase": "night",  # 自爆后直接进入黑夜
                }
        
        print(f"  {player.name} (玩家{player.player_id}) 正在发言...")
        
        # 调用 Agent 发言逻辑
        content = await agent.speak(state, context="normal")
        print(f"    💬 {content}")
        
        discussion = {
            "player_id": player.player_id,
            "player_name": player.name,
            "role": player.role,
            "content": content,
            "day": day_number,
        }
        discussions.append(discussion)
        await asyncio.sleep(0.1)
    
    current_discussions = state.get("discussions", [])
    current_discussions.extend(discussions)
    
    history_entry = {
        "type": "discussion",
        "day": day_number,
        "discussions": discussions,
    }
    
    current_history = state.get("history", [])
    current_history.append(history_entry)
    
    return {
        "discussions": current_discussions,
        "history": current_history,
    }


async def exile_voting_node(state: GameState) -> Dict[str, Any]:
    """放逐投票节点"""
    day_number = state.get("day_number", 1)
    tie_vote_round = state.get("tie_vote_round", 0)
    tied_players = state.get("tied_players", [])
    
    if tie_vote_round > 0:
        print(f"\n🗳️  放逐投票（平票重议第{tie_vote_round}轮）- 第 {day_number} 天")
    else:
        print(f"\n🗳️  放逐投票 - 第 {day_number} 天")
    
    alive_players = [p for p in state["players"] if p.is_alive]
    
    # 如果是平票重议，只能投票给平票的玩家
    if tie_vote_round > 0 and tied_players:
        voting_targets = [p for p in alive_players if p.player_id in tied_players]
    else:
        voting_targets = [p for p in alive_players]
    
    votes = {}
    
    # 收集投票
    from ..utils.agent_factory import create_agent_by_role
    for player in alive_players:
        # 调用 Agent 投票逻辑
        agent = create_agent_by_role(player.player_id, player.name, player.role)
        target = await agent.vote(state, vote_type="exile")
        if target:
            votes[player.player_id] = target
            target_name = next((p.name for p in alive_players if p.player_id == target), f"玩家{target}")
            print(f"  {player.name} 投票给 {target_name}")
        else:
            print(f"  {player.name} 弃权")
    
    # 统计投票结果
    vote_results = {}
    for target_id in votes.values():
        vote_results[target_id] = vote_results.get(target_id, 0) + 1
    
    # 找出得票最多的玩家
    if vote_results:
        max_votes = max(vote_results.values())
        eliminated_players = [pid for pid, votes in vote_results.items() if votes == max_votes]
        
        history_entry = {
            "type": "exile_voting",
            "day": day_number,
            "votes": votes,
            "vote_results": vote_results,
            "eliminated": eliminated_players if len(eliminated_players) == 1 else None,
            "tie": len(eliminated_players) > 1,
            "tie_vote_round": tie_vote_round,
        }
        
        current_history = state.get("history", [])
        current_history.append(history_entry)
        
        updates = {
            "votes": votes,
            "vote_results": vote_results,
            "history": current_history,
        }
        
        if len(eliminated_players) == 1:
            eliminated_id = eliminated_players[0]
            eliminated_player = next((p for p in alive_players if p.player_id == eliminated_id), None)
            
            # 更新玩家状态
            updated_players = []
            for p in state["players"]:
                if p.player_id == eliminated_id:
                    updated_p = Player(
                        player_id=p.player_id,
                        name=p.name,
                        role=p.role,
                        is_alive=False,
                        vote_target=p.vote_target,
                        is_sheriff=p.is_sheriff
                    )
                    updated_players.append(updated_p)
                    print(f"\n  ❌ {p.name} (玩家{eliminated_id}) 被放逐")
                    # TODO: 选择发动技能、留下遗言
                else:
                    updated_players.append(p)
            
            updates["players"] = updated_players
            updates["consecutive_ties"] = 0
            updates["tie_vote_round"] = 0
            updates["tied_players"] = []
        elif len(eliminated_players) > 1:
            # 平票情况
            if tie_vote_round == 0:
                # 第一轮平票：进入重议
                updates["tie_vote_round"] = 1
                updates["tied_players"] = eliminated_players
                print(f"  ⚠️  第一轮投票平票！平票玩家: {eliminated_players}")
            elif tie_vote_round == 1:
                # 第二轮依然平票：直接进入黑夜，无人出局
                updates["tie_vote_round"] = 2
                updates["tied_players"] = []
                print(f"  ⚠️  第二轮投票依然平票！无人出局，直接进入黑夜")
        
        return updates
    
    return {"votes": votes, "vote_results": vote_results}


async def judgment_node(state: GameState) -> Dict[str, Any]:
    """结果判定节点：屠边规则"""
    print(f"\n⚖️  结果判定")
    print("=" * 60)
    
    alive_players = [p for p in state["players"] if p.is_alive]
    werewolves = [p for p in alive_players if p.role == "werewolf"]
    villagers = [p for p in alive_players if p.role == "villager"]
    gods = [p for p in alive_players if p.role in ["seer", "witch", "guard"]]
    
    winner = None
    game_status = "playing"
    
    # 屠边规则判断
    if len(werewolves) == 0:
        # 狼人全部出局，好人获胜
        winner = "villagers"
        game_status = "ended"
        print(f"  ✅ 好人获胜！（狼人全部出局）")
    elif len(villagers) == 0:
        # 平民全部出局，狼人获胜
        winner = "werewolves"
        game_status = "ended"
        print(f"  ✅ 狼人获胜！（平民全部出局）")
    elif len(gods) == 0:
        # 神职全部出局，狼人获胜
        winner = "werewolves"
        game_status = "ended"
        print(f"  ✅ 狼人获胜！（神职全部出局）")
    
    # 记录结果
    if game_status == "ended":
        history_entry = {
            "type": "game_end",
            "winner": winner,
            "day": state.get("day_number", 1),
            "round": state.get("round_number", 1),
            "alive_werewolves": len(werewolves),
            "alive_villagers": len(villagers),
            "alive_gods": len(gods),
        }
        current_history = state.get("history", [])
        current_history.append(history_entry)
        return {
            "game_status": game_status,
            "winner": winner,
            "history": current_history,
        }
    
    return {}
