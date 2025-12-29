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
        # 构建 prompt
        from ...utils.prompt_builder import build_werewolf_discuss_prompt
        system_prompt, user_prompt = build_werewolf_discuss_prompt(
            self.agent_id,
            self.name,
            game_state,
            werewolf_teammates
        )
        
        try:
            # 调用 LLM 生成发言内容
            response = await self.llm_client.call(system_prompt, user_prompt)
            return response.strip()
        except Exception as e:
            # LLM 调用失败，返回默认发言
            print(f"⚠️  狼人 {self.name} 频道发言 LLM 调用失败: {e}")
            return "我们需要讨论今晚的攻击策略。"
    
    async def vote_to_kill(
        self, 
        game_state: Dict[str, Any],
        werewolf_teammates: List[Dict[str, Any]],
        werewolf_channel_messages: List[Dict[str, Any]]
    ) -> Optional[int]:
        """
        投票决定攻击目标
        
        Args:
            game_state: 游戏状态
            werewolf_teammates: 狼人队友列表
            werewolf_channel_messages: 狼人频道发言记录（字典列表）
        
        Returns:
            目标玩家ID，如果不攻击则返回 None
        """
        alive_players = [p for p in game_state.get("players", []) if p.is_alive]
        targets = [p for p in alive_players if p.role != "werewolf"]
        
        if not targets:
            return None
        
        # 构建 prompt
        from ...utils.prompt_builder import build_werewolf_vote_prompt
        system_prompt, user_prompt = build_werewolf_vote_prompt(
            self.agent_id,
            self.name,
            game_state,
            werewolf_teammates,
            werewolf_channel_messages
        )
        
        # 定义投票决策的 Schema
        from pydantic import BaseModel, Field
        from typing import Optional
        class KillVoteDecision(BaseModel):
            thought: str = Field(description="推理过程")
            target_id: Optional[int] = Field(default=None, description="目标玩家ID（如果不攻击则返回None）")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(KillVoteDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            if decision.target_id:
                # 验证目标玩家是否存在
                target_player = next(
                    (p for p in targets if p.player_id == decision.target_id),
                    None
                )
                if target_player:
                    return decision.target_id
            
            return None
        except Exception as e:
            # LLM 调用失败，随机选择
            print(f"⚠️  狼人 {self.name} 投票决策 LLM 调用失败: {e}")
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
        # 构建 prompt
        from ...utils.prompt_builder import build_werewolf_explode_prompt
        system_prompt, user_prompt = build_werewolf_explode_prompt(
            self.agent_id,
            self.name,
            game_state
        )
        
        # 定义自爆决策的 Schema
        from pydantic import BaseModel, Field
        class ExplodeDecision(BaseModel):
            thought: str = Field(description="推理过程")
            should_explode: bool = Field(description="是否自爆")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(ExplodeDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            return decision.should_explode
        except Exception as e:
            # LLM 调用失败，默认不自爆
            print(f"⚠️  狼人 {self.name} 自爆决策 LLM 调用失败: {e}")
            return False

