"""
狼人 Agent
"""
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from ..schemas.actions import AgentAction


class WerewolfAgent(BaseAgent):
    """狼人角色 Agent"""
    
    def __init__(self, agent_id: int, name: str, llm_client=None):
        super().__init__(agent_id, "werewolf", name, llm_client)
        self.werewolf_team = []  # 狼人团队
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """狼人可以看到公共信息和狼人频道信息"""
        players = game_state.get("players", [])
        alive_players = [p for p in players if p.is_alive]
        
        # 识别狼人队友
        werewolf_teammates = [
            p for p in alive_players 
            if p.role == "werewolf" and p.player_id != self.agent_id
        ]
        
        return {
            "public_info": game_state.get("public_info", {}),
            "werewolf_channel": game_state.get("werewolf_channel", {}),
            "alive_players": alive_players,
            "werewolf_teammates": werewolf_teammates,
            "night_actions": game_state.get("night_actions", {}),
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """狼人的推理逻辑"""
        # TODO: 使用 LLM 进行推理
        return "作为狼人，我需要隐藏身份并淘汰村民，与队友协调行动。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """狼人的行动（夜晚杀人、白天投票）"""
        # TODO: 使用 LLM 决定行动
        return AgentAction(
            thought="我需要选择目标进行攻击",
            action_type="kill",
            target=None,
            confidence=0.6,
            reasoning="基于团队策略"
        )
    
    async def discuss_in_werewolf_channel(
        self, 
        game_state: Dict[str, Any],
        werewolf_teammates: List[Dict[str, Any]]
    ) -> str:
        """
        在狼人频道发言（天黑时）
        
        Args:
            game_state: 游戏状态
            werewolf_teammates: 狼人队友列表
        
        Returns:
            发言内容
        """
        # TODO: 调用 LLM 生成发言内容
        # 目前模拟：基于游戏状态生成策略性发言
        alive_players = [p for p in game_state.get("players", []) if p.is_alive]
        non_werewolves = [p for p in alive_players if p.role != "werewolf"]
        
        if not non_werewolves:
            return "所有非狼人玩家已出局，我们即将获胜。"
        
        # 模拟发言
        import random
        strategies = [
            "我们应该优先攻击疑似神职的玩家",
            "今晚我建议攻击玩家X，他可能是预言家",
            "我们需要保持低调，不要暴露身份",
        ]
        return random.choice(strategies)
    
    async def vote_to_kill(
        self, 
        game_state: Dict[str, Any],
        werewolf_teammates: List[Dict[str, Any]],
        werewolf_channel_messages: List[str]
    ) -> Optional[int]:
        """
        投票决定攻击目标
        
        Args:
            game_state: 游戏状态
            werewolf_teammates: 狼人队友列表
            werewolf_channel_messages: 狼人频道发言记录
        
        Returns:
            目标玩家ID，如果不攻击则返回 None
        """
        alive_players = [p for p in game_state.get("players", []) if p.is_alive]
        targets = [p for p in alive_players if p.role != "werewolf"]
        
        if not targets:
            return None
        
        # TODO: 调用 LLM 基于讨论和游戏状态决定攻击目标
        # 目前模拟：随机选择
        import random
        target = random.choice(targets)
        return target.player_id
    
    async def decide_self_explode(
        self,
        game_state: Dict[str, Any],
        current_speaker_id: Optional[int] = None
    ) -> bool:
        """
        决定是否自爆
        
        Args:
            game_state: 游戏状态
            current_speaker_id: 当前发言玩家ID（如果是自己发言时）
        
        Returns:
            是否自爆
        """
        # 自爆条件：
        # 1. 可以在发言阶段随时自爆
        # 2. 自爆后立即进入黑夜，终止发言
        
        # TODO: 调用 LLM 决定是否自爆
        # 目前模拟：随机决定（概率较低）
        import random
        return random.choice([False, False, False, False, False])  # 20% 概率
        
        # 实际策略可能包括：
        # - 当身份即将暴露时自爆
        # - 为了阻止好人投票而自爆
        # - 为了保护队友而自爆

