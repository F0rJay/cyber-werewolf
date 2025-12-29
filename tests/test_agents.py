"""
Agent 测试
"""
import pytest
from src.agents.villager import VillagerAgent
from src.agents.werewolf import WerewolfAgent


@pytest.mark.asyncio
async def test_villager_agent():
    """测试村民 Agent"""
    agent = VillagerAgent(agent_id=1, name="村民1")
    assert agent.role == "villager"
    assert agent.agent_id == 1


@pytest.mark.asyncio
async def test_werewolf_agent():
    """测试狼人 Agent"""
    agent = WerewolfAgent(agent_id=2, name="狼人1")
    assert agent.role == "werewolf"
    assert agent.agent_id == 2

