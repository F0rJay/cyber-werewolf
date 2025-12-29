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
        
        # 构建 prompt
        from ...utils.prompt_builder import build_guard_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_guard_prompt(
            self.agent_id,
            self.name,
            game_state,
            observation,
            last_protected_id
        )
        
        # 定义守护决策的 Schema
        from pydantic import BaseModel, Field
        class GuardDecision(BaseModel):
            thought: str = Field(description="推理过程")
            target_id: Optional[int] = Field(default=None, description="目标玩家ID（如果不守护则返回None）")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(GuardDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            if decision.target_id:
                # 验证目标玩家是否存在且符合规则
                target_player = next(
                    (p for p in targets if p.player_id == decision.target_id),
                    None
                )
                if target_player:
                    return decision.target_id
            
            return None
        except Exception as e:
            # LLM 调用失败，随机选择
            print(f"⚠️  守卫 {self.name} 守护决策 LLM 调用失败: {e}")
            import random
            target = random.choice(targets)
            return target.player_id


async def create_guard_agent(agent_id: int, name: str, llm_client=None) -> GuardAgent:
    """创建守卫 Agent"""
    return GuardAgent(agent_id, name, llm_client)

