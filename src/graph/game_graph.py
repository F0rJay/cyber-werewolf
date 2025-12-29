"""
游戏主图：完整游戏流程
"""
from typing import Literal
from langgraph.graph import StateGraph, END
from ..state.game_state import GameState
from .nodes import (
    role_assignment_node,
    night_phase_node,
    announce_death_node,
    sheriff_campaign_node,
    sheriff_voting_node,
    discussion_node,
    exile_voting_node,
    judgment_node,
)


def check_game_end(state: GameState) -> Literal["end", "continue"]:
    """检查游戏是否结束（屠边规则）"""
    game_status = state.get("game_status", "playing")
    if game_status == "ended":
        return "end"
    
    alive_players = [p for p in state["players"] if p.is_alive]
    werewolves = [p for p in alive_players if p.role == "werewolf"]
    villagers = [p for p in alive_players if p.role == "villager"]
    gods = [p for p in alive_players if p.role in ["seer", "witch", "guard"]]
    
    # 屠边规则
    if len(werewolves) == 0 or len(villagers) == 0 or len(gods) == 0:
        return "end"
    
    return "continue"


def route_after_exile_voting(state: GameState) -> Literal["judgment", "night", "replay"]:
    """放逐投票后的路由"""
    if check_game_end(state) == "end":
        return "judgment"
    
    # 检查是否平票
    tie_vote_round = state.get("tie_vote_round", 0)
    if tie_vote_round == 1:
        # 第一轮平票：重议
        return "replay"
    elif tie_vote_round == 2:
        # 第二轮平票：直接进入黑夜
        return "night"
    
    # 检查是否有自爆
    if state.get("self_exploded"):
        return "night"
    
    # 正常流程：进入黑夜
    return "night"


def route_after_night(state: GameState) -> Literal["judgment", "day"]:
    """夜晚后的路由"""
    if check_game_end(state) == "end":
        return "judgment"
    
    # 进入新的一天
    day_number = state.get("day_number", 1)
    return "day"


# route_after_sheriff_voting 已在上面重新定义


def route_after_announce_death(state: GameState) -> Literal["discussion", "night"]:
    """公布出局玩家后的路由"""
    # 检查是否有自爆
    if state.get("self_exploded"):
        return "night"
    
    # 正常流程：进入发言
    return "discussion"


def create_game_graph() -> StateGraph:
    """
    创建完整游戏工作流图
    
    游戏流程：
    1. 身份分配
    2. 夜晚阶段（狼人、预言家、守卫、女巫）
    3. 第一天：警长竞选 → 警长投票 → 公布出局 → 发言 → 放逐投票
    4. 其他天：公布出局 → 发言 → 放逐投票
    5. 循环直到游戏结束（屠边规则）
    """
    graph = StateGraph(GameState)
    
    # 添加节点
    graph.add_node("role_assignment", role_assignment_node)
    graph.add_node("night", night_phase_node)
    graph.add_node("announce_death", announce_death_node)
    graph.add_node("sheriff_campaign", sheriff_campaign_node)
    graph.add_node("sheriff_voting", sheriff_voting_node)
    graph.add_node("discussion", discussion_node)
    graph.add_node("exile_voting", exile_voting_node)
    graph.add_node("judgment", judgment_node)
    
    # 设置入口点
    graph.set_entry_point("role_assignment")
    
    # 身份分配后进入第一夜
    graph.add_edge("role_assignment", "night")
    
    # 夜晚后的路由：第一天进入警长竞选，其他天公布出局
    def route_after_night_first_day(state: GameState) -> Literal["sheriff_campaign", "announce_death"]:
        day_number = state.get("day_number", 1)
        if day_number == 1:
            return "sheriff_campaign"
        return "announce_death"
    
    graph.add_conditional_edges(
        "night",
        route_after_night_first_day,
        {
            "sheriff_campaign": "sheriff_campaign",
            "announce_death": "announce_death",
        }
    )
    
    # 警长竞选后的路由：正常竞选后投票，PK发言后也投票，没有候选人时直接公布出局
    def route_after_sheriff_campaign(state: GameState) -> Literal["sheriff_voting", "announce_death"]:
        # 检查是否是PK发言阶段（PK发言后应该进入第二轮投票）
        sheriff_vote_round = state.get("sheriff_vote_round", 0)
        sheriff_tied_candidates = state.get("sheriff_tied_candidates", [])
        if sheriff_vote_round == 1 and sheriff_tied_candidates:
            # PK发言后，进入第二轮投票
            return "sheriff_voting"
        
        # 检查是否有候选人
        candidates = state.get("sheriff_candidates", [])
        if not candidates:
            # 没有候选人，直接进入公布出局
            return "announce_death"
        # 有候选人，进入投票
        return "sheriff_voting"
    
    graph.add_conditional_edges(
        "sheriff_campaign",
        route_after_sheriff_campaign,
        {
            "sheriff_voting": "sheriff_voting",
            "announce_death": "announce_death",
        }
    )
    
    # 警长投票后的路由
    def route_after_sheriff_voting(state: GameState) -> Literal["announce_death", "sheriff_pk", "discussion"]:
        # 检查是否有候选人（如果没有候选人，直接进入下一阶段）
        candidates = state.get("sheriff_candidates", [])
        sheriff_tied_candidates = state.get("sheriff_tied_candidates", [])
        
        # 如果既没有候选人也没有平票候选人，说明投票已完成或没有进行投票
        if not candidates and not sheriff_tied_candidates:
            day_number = state.get("day_number", 1)
            if day_number == 1:
                return "announce_death"
            return "discussion"
        
        day_number = state.get("day_number", 1)
        if day_number == 1:
            # 检查是否平票（检查是否有平票候选人，说明刚完成第一轮投票且平票）
            sheriff_vote_round = state.get("sheriff_vote_round", 0)
            
            # 如果刚设置平票候选人（第一轮平票），进入PK发言
            if sheriff_tied_candidates and sheriff_vote_round == 1:
                return "sheriff_pk"
            else:
                # 正常流程：公布出局玩家
                return "announce_death"
        return "discussion"
    
    graph.add_conditional_edges(
        "sheriff_voting",
        route_after_sheriff_voting,
        {
            "announce_death": "announce_death",
            "sheriff_pk": "sheriff_campaign",  # PK发言复用竞选节点
            "discussion": "discussion",
        }
    )
    
    # 注意：PK发言复用sheriff_campaign节点
    # sheriff_campaign节点会检测是否是PK阶段（通过sheriff_vote_round和sheriff_tied_candidates）
    # PK发言后，route_after_sheriff_campaign会检测到有候选人，路由到sheriff_voting进行第二轮投票
    
    # 公布出局玩家后的路由
    graph.add_conditional_edges(
        "announce_death",
        route_after_announce_death,
        {
            "discussion": "discussion",
            "night": "night",  # 自爆情况
        }
    )
    
    # 发言后的路由：检查是否有自爆
    def route_after_discussion(state: GameState) -> Literal["exile_voting", "night"]:
        """发言后的路由：如果有自爆，直接进入黑夜"""
        if state.get("self_exploded"):
            return "night"
        return "exile_voting"
    
    graph.add_conditional_edges(
        "discussion",
        route_after_discussion,
        {
            "exile_voting": "exile_voting",
            "night": "night",  # 自爆情况
        }
    )
    
    # 放逐投票后的路由
    graph.add_conditional_edges(
        "exile_voting",
        route_after_exile_voting,
        {
            "judgment": "judgment",
            "night": "night",
            "replay": "discussion",  # 平票重议
        }
    )
    
    # 夜晚后的路由（进入新的一天）
    graph.add_conditional_edges(
        "night",
        route_after_night,
        {
            "judgment": "judgment",
            "day": "announce_death",  # 进入新的一天，先公布出局
        }
    )
    
    # 结果判定后结束
    graph.add_edge("judgment", END)
    
    return graph.compile()

