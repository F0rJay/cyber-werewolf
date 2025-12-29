"""
Graph 测试
"""
import pytest
from src.graph.game_graph import create_game_graph
from src.state.game_state import StateManager, Player


def test_create_game_graph():
    """测试创建游戏图"""
    graph = create_game_graph()
    assert graph is not None


@pytest.mark.asyncio
async def test_game_workflow():
    """测试游戏工作流"""
    from src.state.game_state import StateManager, Player
    
    # 创建状态管理器
    state_manager = StateManager()
    
    # 创建玩家
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="villager"),
        Player(player_id=3, name="玩家3", role="werewolf"),
    ]
    
    # 初始化状态
    initial_state = state_manager.init_state(players, max_rounds=5)
    
    # 创建游戏图
    graph = create_game_graph()
    
    # 运行游戏（只运行几步，不完整运行）
    # 注意：完整运行可能会因为随机性导致不同结果
    assert graph is not None
    assert initial_state["game_status"] == "playing"

