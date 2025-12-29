"""
狼人 Agent
"""
from typing import Dict, Any
from .base_agent import BaseAgent, AgentAction


class WerewolfAgent(BaseAgent):
    """狼人角色 Agent"""
    
    def __init__(self, agent_id: int, name: str):
        super().__init__(agent_id, "werewolf", name)
        self.werewolf_team = []  # 狼人团队
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """狼人可以看到公共信息和狼人频道信息"""
        return {
            "public_info": game_state.get("public_info", {}),
            "werewolf_channel": game_state.get("werewolf_channel", {}),
            "alive_players": game_state.get("alive_players", []),
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """狼人的推理逻辑"""
        # TODO: 实现推理逻辑
        return "作为狼人，我需要隐藏身份并淘汰村民。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """狼人的行动（夜晚杀人、白天投票）"""
        # TODO: 实现行动逻辑
        return AgentAction(
            thought="我需要选择目标进行攻击",
            action_type="kill",
            target=None,
            confidence=0.6,
            reasoning="基于团队策略"
        )

