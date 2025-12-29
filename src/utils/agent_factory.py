"""
Agent 工厂：根据角色创建对应的 Agent
"""
from typing import Dict, Optional
from ..agents.base_agent import BaseAgent
from ..agents.villager import VillagerAgent
from ..agents.werewolf import WerewolfAgent
from ..agents.roles.seer import SeerAgent
from ..agents.roles.witch import WitchAgent
from ..agents.roles.guard import GuardAgent
from ..utils.llm_client import LLMClient


def create_agent_by_role(
    agent_id: int,
    name: str,
    role: str,
    llm_client: Optional[LLMClient] = None
) -> BaseAgent:
    """
    根据角色创建对应的 Agent
    
    Args:
        agent_id: Agent ID
        name: Agent 名称
        role: 角色名称
        llm_client: LLM 客户端
    
    Returns:
        对应的 Agent 实例
    """
    if llm_client is None:
        llm_client = LLMClient(provider="deepseek")
    
    role_map = {
        "villager": VillagerAgent,
        "werewolf": WerewolfAgent,
        "seer": SeerAgent,
        "witch": WitchAgent,
        "guard": GuardAgent,
    }
    
    agent_class = role_map.get(role)
    if agent_class is None:
        raise ValueError(f"Unknown role: {role}")
    
    return agent_class(agent_id, name, llm_client)


def create_agents_from_players(
    players: list,
    llm_client: Optional[LLMClient] = None
) -> Dict[int, BaseAgent]:
    """
    从玩家列表创建 Agent 字典
    
    Args:
        players: 玩家列表
        llm_client: LLM 客户端
    
    Returns:
        {player_id: Agent} 字典
    """
    agents = {}
    for player in players:
        agent = create_agent_by_role(
            agent_id=player.player_id,
            name=player.name,
            role=player.role,
            llm_client=llm_client
        )
        agents[player.player_id] = agent
    
    return agents

