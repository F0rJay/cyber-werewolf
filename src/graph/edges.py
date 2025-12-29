"""
LangGraph 条件边实现
"""
from typing import Literal
from ..state.game_state import GameState


def check_game_end(state: GameState) -> Literal["end", "continue"]:
    """检查游戏是否结束"""
    game_status = state.get("game_status", "playing")
    
    if game_status == "ended":
        return "end"
    
    # 检查存活玩家数量
    alive_players = [p for p in state["players"] if p.is_alive]
    werewolves = [p for p in alive_players if p.role == "werewolf"]
    villagers = [p for p in alive_players if p.role != "werewolf"]
    
    # 游戏结束条件
    if len(werewolves) == 0 or len(werewolves) >= len(villagers):
        return "end"
    
    return "continue"


def check_tie_vote(state: GameState) -> Literal["replay", "continue", "night"]:
    """检查是否平票，决定是否重议
    
    规则：
    - 第一轮平票：平票玩家进行第二轮发言和投票
    - 第二轮依然平票：直接进入黑夜，无人出局
    """
    vote_results = state.get("vote_results", {})
    tie_vote_round = state.get("tie_vote_round", 0)
    
    if not vote_results:
        return "continue"
    
    # 找出最高票数
    max_votes = max(vote_results.values()) if vote_results else 0
    if max_votes == 0:
        return "continue"
    
    # 统计得最高票的玩家数量
    top_voted_count = sum(1 for v in vote_results.values() if v == max_votes)
    
    # 如果有多人得最高票，则为平票
    if top_voted_count > 1:
        if tie_vote_round == 0:
            # 第一轮平票：进入重议
            return "replay"
        elif tie_vote_round == 1:
            # 第二轮依然平票：直接进入黑夜
            return "night"
    
    # 正常情况，继续流程
    return "continue"


def check_phase(state: GameState) -> Literal["day", "night"]:
    """检查当前阶段"""
    current_phase = state.get("current_phase", "day")
    return current_phase


def route_after_voting(state: GameState) -> Literal["judgment", "night", "replay"]:
    """投票后的路由：判断是进入夜晚、重议还是判定结果"""
    # 先检查游戏是否结束
    if check_game_end(state) == "end":
        return "judgment"
    
    # 检查是否平票
    tie_result = check_tie_vote(state)
    if tie_result == "replay":
        # 第一轮平票：进入重议（第二轮发言）
        return "replay"
    elif tie_result == "night":
        # 第二轮依然平票：直接进入黑夜
        return "night"
    
    # 正常流程：进入夜晚
    return "night"


def route_after_night(state: GameState) -> Literal["judgment", "day"]:
    """夜晚后的路由：判断是进入白天还是判定结果"""
    # 检查游戏是否结束
    if check_game_end(state) == "end":
        return "judgment"
    
    # 进入新的一天
    return "day"
