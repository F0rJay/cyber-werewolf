"""
Graph 测试
"""
import pytest
from src.graph.game_graph import create_game_graph


def test_create_game_graph():
    """测试创建游戏图"""
    graph = create_game_graph()
    assert graph is not None

