"""
状态管理测试
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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


def test_state_manager_with_max_rounds():
    """测试状态管理器（带最大轮次）"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players, max_rounds=10)
    assert state["max_rounds"] == 10
    assert state["round_number"] == 1
    assert state["day_number"] == 1


def test_state_update():
    """测试状态更新"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 更新状态
    updates = {
        "round_number": 2,
        "day_number": 2,
    }
    updated_state = manager.update_state(updates)
    assert updated_state["round_number"] == 2
    assert updated_state["day_number"] == 2


def test_player_model():
    """测试玩家模型"""
    player = Player(
        player_id=1,
        name="玩家1",
        role="villager",
        is_alive=True,
        is_sheriff=False
    )
    assert player.player_id == 1
    assert player.name == "玩家1"
    assert player.role == "villager"
    assert player.is_alive == True
    assert player.is_sheriff == False


def test_sheriff_state():
    """测试警长状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager", is_sheriff=True),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    sheriff = next((p for p in state["players"] if p.is_sheriff), None)
    assert sheriff is not None
    assert sheriff.player_id == 1
    assert sheriff.is_sheriff == True


def test_vote_state():
    """测试投票状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始投票状态
    assert state["votes"] == {}
    assert state["vote_results"] == {}
    
    # 更新投票
    updates = {
        "votes": {1: 2, 2: 1},
        "vote_results": {1: 1, 2: 1}
    }
    updated_state = manager.update_state(updates)
    assert updated_state["votes"][1] == 2
    assert updated_state["vote_results"][1] == 1


def test_seer_checks_state():
    """测试预言家查验状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始查验状态
    assert state["seer_checks"] == {}
    
    # 更新查验结果
    updates = {
        "seer_checks": {1: "好人", 2: "狼人"}
    }
    updated_state = manager.update_state(updates)
    assert updated_state["seer_checks"][1] == "好人"
    assert updated_state["seer_checks"][2] == "狼人"


def test_witch_state():
    """测试女巫状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="witch"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始女巫状态
    assert state["witch_antidote_used"] == False
    assert state["witch_poison_used"] == False
    
    # 更新女巫状态
    updates = {
        "witch_antidote_used": True,
        "witch_poison_used": False
    }
    updated_state = manager.update_state(updates)
    assert updated_state["witch_antidote_used"] == True
    assert updated_state["witch_poison_used"] == False


def test_guard_state():
    """测试守卫状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="guard"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始守卫状态
    assert state["guard_protected"] is None
    assert state["guard_protected_tonight"] is None
    
    # 更新守卫状态
    updates = {
        "guard_protected_tonight": 2
    }
    updated_state = manager.update_state(updates)
    assert updated_state["guard_protected_tonight"] == 2


def test_last_words_state():
    """测试遗言状态"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 初始遗言状态
    assert state["last_words"] == {}
    
    # 更新遗言
    updates = {
        "last_words": {1: "我是好人"}
    }
    updated_state = manager.update_state(updates)
    assert updated_state["last_words"][1] == "我是好人"

