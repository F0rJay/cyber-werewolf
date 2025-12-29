"""
游戏主图：LangGraph 工作流定义
"""
from langgraph.graph import StateGraph
from typing import Dict, Any
from ..state.game_state import GameState


def create_game_graph() -> StateGraph:
    """
    创建游戏工作流图
    
    Returns:
        StateGraph: LangGraph 状态图
    """
    # TODO: 实现 LangGraph 工作流
    graph = StateGraph(GameState)
    
    # 添加节点
    # graph.add_node("init", init_node)
    # graph.add_node("discussion", discussion_node)
    # graph.add_node("voting", voting_node)
    # graph.add_node("night", night_node)
    
    # 添加边
    # graph.set_entry_point("init")
    # graph.add_edge("init", "discussion")
    
    return graph

