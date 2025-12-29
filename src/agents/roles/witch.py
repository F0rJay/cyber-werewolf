"""
女巫 Agent
"""
from typing import Dict, Any, Optional
from ..base_agent import BaseAgent
from ...schemas.actions import AgentAction


class WitchAgent(BaseAgent):
    """女巫角色 Agent"""
    
    def __init__(self, agent_id: int, name: str, llm_client=None):
        super().__init__(agent_id, "witch", name, llm_client)
        self.antidote_used = False  # 解药是否已使用
        self.poison_used = False    # 毒药是否已使用
        self.first_night = True     # 是否第一夜
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """女巫可以看到公共信息和夜晚行动信息"""
        return {
            "public_info": game_state.get("public_info", {}),
            "alive_players": game_state.get("alive_players", []),
            "night_actions": game_state.get("night_actions", {}),
            "antidote_used": self.antidote_used,
            "poison_used": self.poison_used,
            "first_night": self.first_night,
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """女巫的推理逻辑"""
        # TODO: 使用 LLM 进行推理
        return "作为女巫，我需要判断是否使用解药救人，以及是否使用毒药淘汰可疑玩家。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """女巫的行动（使用解药或毒药）"""
        # TODO: 使用 LLM 决定行动
        return AgentAction(
            thought="我需要决定是否使用解药或毒药",
            action_type="skip",
            target=None,
            confidence=0.5,
            reasoning="基于观察和推理"
        )
    
    async def decide_antidote(self, game_state: Dict[str, Any], killed_player_id: Optional[int]) -> bool:
        """
        决定是否使用解药
        
        Args:
            game_state: 游戏状态
            killed_player_id: 被杀的玩家ID（如果有）
        
        Returns:
            是否使用解药
        """
        if self.antidote_used or killed_player_id is None:
            return False
        
        # TODO: 调用 LLM 决定
        # 目前模拟逻辑：第一夜救自己，其他夜随机
        if self.first_night and killed_player_id == self.agent_id:
            return True
        
        # 模拟：随机决定
        import random
        return random.choice([True, False])
    
    async def decide_poison(self, game_state: Dict[str, Any]) -> Optional[int]:
        """
        决定是否使用毒药，以及毒谁
        
        Args:
            game_state: 游戏状态
        
        Returns:
            目标玩家ID，如果不用毒药则返回 None
        """
        if self.poison_used:
            return None
        
        # TODO: 调用 LLM 决定
        # 毒药不能给自己用
        alive_players = [p for p in game_state.get("players", []) if p.is_alive]
        targets = [p for p in alive_players if p.player_id != self.agent_id]
        
        if not targets:
            return None
        
        # 模拟：随机决定（暂时不用毒药）
        import random
        use_poison = random.choice([False])  # 暂时不用
        if use_poison:
            target = random.choice(targets)
            return target.player_id
        
        return None


async def create_witch_agent(agent_id: int, name: str, llm_client=None) -> WitchAgent:
    """创建女巫 Agent"""
    return WitchAgent(agent_id, name, llm_client)

