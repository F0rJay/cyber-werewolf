"""
Agent 测试
"""
import pytest
from src.agents.villager import VillagerAgent
from src.agents.werewolf import WerewolfAgent
from src.agents.roles.seer import SeerAgent
from src.agents.roles.witch import WitchAgent
from src.agents.roles.guard import GuardAgent
from src.utils.agent_factory import create_agent_by_role
from src.state.game_state import StateManager, Player


@pytest.mark.asyncio
async def test_villager_agent():
    """测试村民 Agent"""
    agent = VillagerAgent(agent_id=1, name="村民1")
    assert agent.role == "villager"
    assert agent.agent_id == 1
    assert agent.name == "村民1"


@pytest.mark.asyncio
async def test_werewolf_agent():
    """测试狼人 Agent"""
    agent = WerewolfAgent(agent_id=2, name="狼人1")
    assert agent.role == "werewolf"
    assert agent.agent_id == 2
    assert agent.name == "狼人1"


@pytest.mark.asyncio
async def test_seer_agent():
    """测试预言家 Agent"""
    agent = SeerAgent(agent_id=3, name="预言家1")
    assert agent.role == "seer"
    assert agent.agent_id == 3
    assert agent.name == "预言家1"
    assert agent.check_history == []


@pytest.mark.asyncio
async def test_witch_agent():
    """测试女巫 Agent"""
    agent = WitchAgent(agent_id=4, name="女巫1")
    assert agent.role == "witch"
    assert agent.agent_id == 4
    assert agent.name == "女巫1"
    assert agent.antidote_used == False
    assert agent.poison_used == False
    assert agent.first_night == True


@pytest.mark.asyncio
async def test_guard_agent():
    """测试守卫 Agent"""
    agent = GuardAgent(agent_id=5, name="守卫1")
    assert agent.role == "guard"
    assert agent.agent_id == 5
    assert agent.name == "守卫1"


@pytest.mark.asyncio
async def test_agent_factory():
    """测试 Agent 工厂"""
    # 测试所有角色
    roles = ["villager", "werewolf", "seer", "witch", "guard"]
    for i, role in enumerate(roles, 1):
        agent = create_agent_by_role(i, f"玩家{i}", role)
        assert agent.role == role
        assert agent.agent_id == i
        assert agent.name == f"玩家{i}"


@pytest.mark.asyncio
async def test_agent_observe():
    """测试 Agent 观察功能"""
    from src.state.game_state import StateManager
    
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    # 测试村民观察
    villager = VillagerAgent(agent_id=1, name="玩家1")
    observation = await villager.observe(state)
    assert "public_info" in observation
    assert "alive_players" in observation
    
    # 测试狼人观察
    werewolf = WerewolfAgent(agent_id=2, name="玩家2")
    observation = await werewolf.observe(state)
    assert "werewolf_channel" in observation


@pytest.mark.asyncio
async def test_seer_check_player():
    """测试预言家查验功能"""
    manager = StateManager()
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="werewolf"),
    ]
    state = manager.init_state(players)
    
    seer = SeerAgent(agent_id=3, name="预言家")
    # 查验村民
    result = await seer.check_player(state, 1)
    assert 1 in result
    assert result[1] == "好人"
    
    # 查验狼人
    result = await seer.check_player(state, 2)
    assert 2 in result
    assert result[2] == "狼人"
    
    # 查验不存在的玩家
    result = await seer.check_player(state, 999)
    assert result == {}

