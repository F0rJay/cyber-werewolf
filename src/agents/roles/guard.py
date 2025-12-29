"""
守卫 Agent
"""
from typing import Dict, Any, Optional
from ..base_agent import BaseAgent
from ...schemas.actions import AgentAction


class GuardAgent(BaseAgent):
    """守卫角色 Agent"""
    
    def __init__(self, agent_id: int, name: str, llm_client=None):
        super().__init__(agent_id, "guard", name, llm_client)
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """守卫可以看到公共信息"""
        return {
            "public_info": game_state.get("public_info", {}),
            "alive_players": game_state.get("alive_players", []),
            "guard_protected": game_state.get("guard_protected"),  # 上一晚守护的玩家
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """守卫的推理逻辑"""
        # TODO: 使用 LLM 进行推理
        return "作为守卫，我需要守护重要的玩家，但不能连续两晚守护同一人。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """守卫的行动（守护）"""
        # TODO: 使用 LLM 决定守护目标
        return AgentAction(
            thought="我需要选择一名玩家进行守护",
            action_type="guard",
            target=None,
            confidence=0.5,
            reasoning="基于观察和推理"
        )
    
    async def decide_protect(self, game_state: Dict[str, Any], last_protected_id: Optional[int]) -> Optional[int]:
        """
        决定守护哪个玩家
        
        Args:
            game_state: 游戏状态
            last_protected_id: 上一晚守护的玩家ID（不能连续两晚守护同一人）
        
        Returns:
            目标玩家ID，如果不守护则返回 None
        """
        alive_players = [p for p in game_state.get("players", []) if p.is_alive]
        
        # 不能守护自己，不能连续两晚守护同一人
        targets = [p for p in alive_players 
                   if p.player_id != self.agent_id and p.player_id != last_protected_id]
        
        if not targets:
            return None
        
        # TODO: 调用 LLM 决定守护目标
        # 目前模拟：随机选择
        import random
        target = random.choice(targets)
        return target.player_id


async def create_guard_agent(agent_id: int, name: str, llm_client=None) -> GuardAgent:
    """创建守卫 Agent"""
    return GuardAgent(agent_id, name, llm_client)

