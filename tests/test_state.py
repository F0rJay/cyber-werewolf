"""
状态管理测试
"""
import pytest
from src.state.game_state import StateManager, Player


def test_state_manager():
    """测试状态管理器"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    assert state["game_status"] == "playing"
    assert len(state["players"]) == 2

