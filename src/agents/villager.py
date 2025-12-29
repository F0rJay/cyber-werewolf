"""
村民 Agent
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentAction


class VillagerAgent(BaseAgent):
    """村民角色 Agent"""
    
    def __init__(self, agent_id: int, name: str):
        super().__init__(agent_id, "villager", name)
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """村民只能看到公共信息"""
        return {
            "public_info": game_state.get("public_info", {}),
            "alive_players": game_state.get("alive_players", []),
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """村民的推理逻辑"""
        # TODO: 实现推理逻辑
        return "作为村民，我需要通过观察和分析找出狼人。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """村民的行动（主要是投票）"""
        # TODO: 实现行动逻辑
        return AgentAction(
            thought="我需要投票淘汰可疑的玩家",
            action_type="vote",
            target=None,
            confidence=0.5,
            reasoning="基于观察和推理"
        )

