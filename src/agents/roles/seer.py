"""
预言家 Agent
"""
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from ...schemas.actions import AgentAction


class SeerAgent(BaseAgent):
    """预言家角色 Agent"""
    
    def __init__(self, agent_id: int, name: str, llm_client=None):
        super().__init__(agent_id, "seer", name, llm_client)
        self.check_history = []  # 查验历史
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """预言家可以看到公共信息和自己的查验结果"""
        return {
            "public_info": game_state.get("public_info", {}),
            "alive_players": game_state.get("alive_players", []),
            "check_history": self.check_history,
            "seer_checks": game_state.get("seer_checks", {}),
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """预言家的推理逻辑"""
        # TODO: 使用 LLM 进行推理
        return "作为预言家，我需要通过查验找出狼人，并引导好人投票。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """预言家的行动（查验）"""
        # TODO: 使用 LLM 决定查验目标
        return AgentAction(
            thought="我需要查验一名可疑的玩家",
            action_type="check",
            target=None,
            confidence=0.5,
            reasoning="基于观察和推理"
        )
    
    async def check_player(self, game_state: Dict[str, Any], target_id: int) -> Dict[str, str]:
        """
        查验玩家身份
        
        Args:
            game_state: 游戏状态
            target_id: 目标玩家ID
        
        Returns:
            查验结果 {"target_id": "role"}
        """
        players = game_state.get("players", [])
        target_player = next((p for p in players if p.player_id == target_id), None)
        
        if target_player:
            result = {target_id: target_player.role}
            self.check_history.append(result)
            return result
        return {}


async def create_seer_agent(agent_id: int, name: str, llm_client=None) -> SeerAgent:
    """创建预言家 Agent"""
    return SeerAgent(agent_id, name, llm_client)

