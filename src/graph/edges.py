"""
LangGraph 条件边实现
"""
from typing import Literal
from ..state.game_state import GameState


def check_game_end(state: GameState) -> Literal["continue", "end"]:
    """检查游戏是否结束"""
    # TODO: 实现游戏结束判断
    return "continue"


def check_tie_vote(state: GameState) -> Literal["replay", "continue"]:
    """检查是否平票，决定是否重议"""
    # TODO: 实现平票检测
    return "continue"


def check_phase(state: GameState) -> Literal["day", "night"]:
    """检查当前阶段"""
    # TODO: 实现阶段判断
    return "day"

