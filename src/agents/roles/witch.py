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
        
        # 构建 prompt
        from ...utils.prompt_builder import build_witch_antidote_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_witch_antidote_prompt(
            self.agent_id,
            self.name,
            game_state,
            observation,
            killed_player_id
        )
        
        # 定义解药决策的 Schema
        from pydantic import BaseModel, Field
        class AntidoteDecision(BaseModel):
            thought: str = Field(description="推理过程")
            use_antidote: bool = Field(description="是否使用解药")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(AntidoteDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            return decision.use_antidote
        except Exception as e:
            # LLM 调用失败，使用默认逻辑
            print(f"⚠️  女巫 {self.name} 解药决策 LLM 调用失败: {e}")
            # 默认逻辑：第一夜救自己
            if self.first_night and killed_player_id == self.agent_id:
                return True
            return False
    
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
        
        # 毒药不能给自己用
        alive_players = [p for p in game_state.get("players", []) if p.is_alive]
        targets = [p for p in alive_players if p.player_id != self.agent_id]
        
        if not targets:
            return None
        
        # 构建 prompt
        from ...utils.prompt_builder import build_witch_poison_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_witch_poison_prompt(
            self.agent_id,
            self.name,
            game_state,
            observation
        )
        
        # 定义毒药决策的 Schema
        from pydantic import BaseModel, Field
        class PoisonDecision(BaseModel):
            thought: str = Field(description="推理过程")
            use_poison: bool = Field(description="是否使用毒药")
            target_id: Optional[int] = Field(default=None, description="目标玩家ID（如果使用毒药）")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(PoisonDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            if decision.use_poison and decision.target_id:
                # 验证目标玩家是否存在且不是自己
                target_player = next(
                    (p for p in targets if p.player_id == decision.target_id),
                    None
                )
                if target_player:
                    return decision.target_id
            
            return None
        except Exception as e:
            # LLM 调用失败，返回 None（不使用毒药）
            print(f"⚠️  女巫 {self.name} 毒药决策 LLM 调用失败: {e}")
            return None


async def create_witch_agent(agent_id: int, name: str, llm_client=None) -> WitchAgent:
    """创建女巫 Agent"""
    return WitchAgent(agent_id, name, llm_client)

