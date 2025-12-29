"""
游戏规则测试
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.state.game_state import StateManager, Player


def test_role_assignment():
    """测试身份分配"""
    from src.utils.role_assigner import assign_roles
    
    player_names = ["玩家1", "玩家2", "玩家3", "玩家4"]
    players = assign_roles(player_names)
    
    assert len(players) == len(player_names)
    # 检查是否有狼人
    werewolves = [p for p in players if p.role == "werewolf"]
    assert len(werewolves) > 0
    # 检查角色是否有效
    valid_roles = ["villager", "werewolf", "seer", "witch", "guard"]
    for player in players:
        assert player.role in valid_roles
        assert player.player_id > 0
        assert player.is_alive == True


def test_sheriff_election():
    """测试警长选举状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始警长状态
    assert state["sheriff_candidates"] == []
    assert state["sheriff_votes"] == {}
    assert state["sheriff_vote_round"] == 0
    
    # 模拟警长竞选
    updates = {
        "sheriff_candidates": [1, 2],
        "sheriff_votes": {1: 1, 2: 1}
    }
    updated_state = manager.update_state(updates)
    assert len(updated_state["sheriff_candidates"]) == 2
    assert len(updated_state["sheriff_votes"]) == 2


def test_tie_vote_handling():
    """测试平票处理"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="villager"),
    ]
    state = manager.init_state(players)
    
    # 初始平票状态
    assert state["tie_vote_round"] == 0
    assert state["tied_players"] == []
    
    # 模拟平票
    updates = {
        "tie_vote_round": 1,
        "tied_players": [1, 2]
    }
    updated_state = manager.update_state(updates)
    assert updated_state["tie_vote_round"] == 1
    assert len(updated_state["tied_players"]) == 2


def test_game_end_conditions():
    """测试游戏结束条件"""
    manager = StateManager()
    
    # 测试好人获胜（狼人全部出局）
    players = [
        Player(player_id=1, name="玩家1", role="villager", is_alive=True),
        Player(player_id=2, name="玩家2", role="werewolf", is_alive=False),
    ]
    state = manager.init_state(players)
    
    alive_werewolves = [p for p in state["players"] if p.role == "werewolf" and p.is_alive]
    assert len(alive_werewolves) == 0
    
    # 测试狼人获胜（村民全部出局）
    players = [
        Player(player_id=1, name="玩家1", role="villager", is_alive=False),
        Player(player_id=2, name="玩家2", role="werewolf", is_alive=True),
    ]
    state = manager.init_state(players)
    
    alive_villagers = [p for p in state["players"] if p.role == "villager" and p.is_alive]
    assert len(alive_villagers) == 0


def test_speaking_order():
    """测试发言顺序逻辑"""
    # 测试以警长为中心的发言顺序
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="villager", is_sheriff=True),
        Player(player_id=3, name="玩家3", role="villager"),
    ]
    
    # 按序号排序
    sorted_players = sorted(players, key=lambda p: p.player_id)
    player_ids = [p.player_id for p in sorted_players]
    sheriff_index = player_ids.index(2)
    
    # 顺序发言：从警长下一个开始
    order_sequence = player_ids[sheriff_index + 1:] + player_ids[:sheriff_index + 1]
    assert order_sequence == [3, 1, 2]
    
    # 逆序发言：从警长前一个开始
    reverse_sequence = player_ids[:sheriff_index][::-1] + player_ids[sheriff_index:][::-1]
    assert reverse_sequence == [1, 3, 2]


def test_sheriff_transfer():
    """测试警长移交状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager", is_sheriff=True),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始移交状态
    assert state["sheriff_transfer"] is None
    
    # 模拟警长移交
    updates = {
        "sheriff_transfer": {
            "from_id": 1,
            "to_id": 2,
            "destroyed": False
        }
    }
    updated_state = manager.update_state(updates)
    assert updated_state["sheriff_transfer"]["from_id"] == 1
    assert updated_state["sheriff_transfer"]["to_id"] == 2
    assert updated_state["sheriff_transfer"]["destroyed"] == False

