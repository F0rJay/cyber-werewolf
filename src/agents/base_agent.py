"""
基础 Agent 类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from ..utils.llm_client import LLMClient
from ..schemas.actions import AgentAction


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(
        self, 
        agent_id: int, 
        role: str, 
        name: str,
        llm_client: Optional[LLMClient] = None
    ):
        """
        初始化 Agent
        
        Args:
            agent_id: Agent ID
            role: 角色名称
            name: Agent 名称
            llm_client: LLM 客户端（如果为 None，则创建默认的 DeepSeek 客户端）
        """
        self.agent_id = agent_id
        self.role = role
        self.name = name
        self.memory = []
        self.llm_client = llm_client or LLMClient(provider="deepseek")
    
    @abstractmethod
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """观察游戏状态，返回可见信息"""
        pass
    
    @abstractmethod
    async def think(self, observation: Dict[str, Any]) -> str:
        """推理过程"""
        pass
    
    @abstractmethod
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """执行行动，返回结构化指令"""
        pass
    
    async def speak(
        self,
        game_state: Dict[str, Any],
        context: str = "normal"
    ) -> str:
        """
        发言
        
        Args:
            game_state: 游戏状态
            context: 发言上下文（normal=正常发言, sheriff_campaign=警长竞选, sheriff_pk=警长PK）
        
        Returns:
            发言内容
        """
        # 构建 prompt
        from ..utils.prompt_builder import build_speak_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_speak_prompt(
            self.agent_id,
            self.name,
            self.role,
            game_state,
            observation,
            context
        )
        
        # 定义发言决策的 Schema
        from pydantic import BaseModel, Field
        class SpeakDecision(BaseModel):
            thought: str = Field(description="推理过程")
            content: str = Field(description="发言内容")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="发言理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(SpeakDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            return decision.content
        except Exception as e:
            # LLM 调用失败，返回默认发言
            print(f"⚠️  {self.name} 发言 LLM 调用失败: {e}")
            return f"{self.name} 的发言（LLM 调用失败，使用默认发言）"
    
    async def vote(
        self,
        game_state: Dict[str, Any],
        vote_type: str = "exile",  # "exile", "sheriff"
        candidates: Optional[List[int]] = None
    ) -> Optional[int]:
        """
        投票
        
        Args:
            game_state: 游戏状态
            vote_type: 投票类型（exile=放逐投票, sheriff=警长投票）
            candidates: 候选人列表（仅用于警长投票）
        
        Returns:
            目标玩家ID，如果不投票则返回 None
        """
        # 构建 prompt
        from ..utils.prompt_builder import build_vote_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_vote_prompt(
            self.agent_id,
            self.name,
            self.role,
            game_state,
            observation,
            vote_type,
            candidates
        )
        
        # 定义投票决策的 Schema
        from pydantic import BaseModel, Field
        from typing import Optional
        class VoteDecision(BaseModel):
            thought: str = Field(description="推理过程")
            target_id: Optional[int] = Field(default=None, description="目标玩家ID（如果不投票则返回None）")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(VoteDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            # 验证目标玩家是否存在
            if decision.target_id:
                players = game_state.get("players", [])
                alive_players = [p for p in players if p.is_alive]
                target_player = next(
                    (p for p in alive_players if p.player_id == decision.target_id),
                    None
                )
                if target_player:
                    # 如果是警长投票，验证目标是否在候选人中
                    if vote_type == "sheriff" and candidates:
                        if decision.target_id not in candidates:
                            return None
                    # 不能投票给自己
                    if decision.target_id == self.agent_id:
                        return None
                    return decision.target_id
            
            return None
        except Exception as e:
            # LLM 调用失败，随机投票
            print(f"⚠️  {self.name} 投票 LLM 调用失败: {e}")
            players = game_state.get("players", [])
            alive_players = [p for p in players if p.is_alive]
            other_players = [p for p in alive_players if p.player_id != self.agent_id]
            if vote_type == "sheriff" and candidates:
                other_players = [p for p in other_players if p.player_id in candidates]
            if other_players:
                import random
                return random.choice(other_players).player_id
            return None
    
    async def leave_last_words(
        self,
        game_state: Dict[str, Any],
        death_reason: str = "exile"  # "night_first" 或 "exile"
    ) -> str:
        """
        留下遗言
        
        Args:
            game_state: 游戏状态
            death_reason: 出局原因（"night_first"=第一天夜里出局, "exile"=被放逐）
        
        Returns:
            遗言内容
        """
        # 构建 prompt
        from ..utils.prompt_builder import build_last_words_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_last_words_prompt(
            self.agent_id,
            self.name,
            self.role,
            game_state,
            observation,
            death_reason
        )
        
        # 定义遗言的 Schema
        from pydantic import BaseModel, Field
        class LastWordsDecision(BaseModel):
            thought: str = Field(description="推理过程")
            content: str = Field(description="遗言内容")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="遗言理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(LastWordsDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            return decision.content
        except Exception as e:
            # LLM 调用失败，返回默认遗言
            print(f"⚠️  {self.name} 遗言 LLM 调用失败: {e}")
            return f"{self.name} 的遗言（LLM 调用失败，使用默认遗言）"
    
    async def decide_sheriff_transfer(
        self,
        game_state: Dict[str, Any]
    ) -> Optional[int]:
        """
        决定警长移交（仅警长可以调用）
        
        Args:
            game_state: 游戏状态
        
        Returns:
            目标玩家ID（如果移交），None（如果销毁警徽）
        """
        # 检查是否是警长
        players = game_state.get("players", [])
        current_player = next((p for p in players if p.player_id == self.agent_id), None)
        if not current_player or not current_player.is_sheriff:
            # 不是警长，不能移交
            return None
        
        # 构建 prompt
        from ..utils.prompt_builder import build_sheriff_transfer_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_sheriff_transfer_prompt(
            self.agent_id,
            self.name,
            self.role,
            game_state,
            observation
        )
        
        # 定义警长移交决策的 Schema
        from pydantic import BaseModel, Field
        from typing import Optional
        class SheriffTransferDecision(BaseModel):
            thought: str = Field(description="推理过程")
            should_transfer: bool = Field(description="是否移交警徽（True=移交，False=销毁）")
            target_id: Optional[int] = Field(default=None, description="目标玩家ID（如果移交），None（如果销毁）")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(SheriffTransferDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            # 验证决策
            if decision.should_transfer and decision.target_id:
                # 验证目标玩家是否存在且存活
                alive_players = [p for p in players if p.is_alive]
                target_player = next(
                    (p for p in alive_players if p.player_id == decision.target_id),
                    None
                )
                if target_player and target_player.player_id != self.agent_id:
                    return decision.target_id
            
            # 不移交或无效目标，返回 None（销毁警徽）
            return None
        except Exception as e:
            # LLM 调用失败，默认销毁警徽
            print(f"⚠️  警长 {self.name} 移交决策 LLM 调用失败: {e}")
            return None
    
    async def decide_speaking_order(
        self,
        game_state: Dict[str, Any],
        alive_players: List[Any]
    ) -> bool:
        """
        决定发言顺序（仅警长可以调用）
        
        Args:
            game_state: 游戏状态
            alive_players: 存活玩家列表
        
        Returns:
            True=顺序发言，False=逆序发言
        """
        # 检查是否是警长
        players = game_state.get("players", [])
        current_player = next((p for p in players if p.player_id == self.agent_id), None)
        if not current_player or not current_player.is_sheriff:
            # 不是警长，默认顺序
            return True
        
        # 构建 prompt
        from ..utils.prompt_builder import build_speaking_order_prompt
        observation = await self.observe(game_state)
        system_prompt, user_prompt = build_speaking_order_prompt(
            self.agent_id,
            self.name,
            self.role,
            game_state,
            observation,
            alive_players
        )
        
        # 定义发言顺序决策的 Schema
        from pydantic import BaseModel, Field
        class SpeakingOrderDecision(BaseModel):
            thought: str = Field(description="推理过程")
            use_order: bool = Field(description="是否顺序发言（True=顺序，False=逆序）")
            confidence: float = Field(description="置信度（0-1）", ge=0.0, le=1.0)
            reasoning: str = Field(description="决策理由")
        
        try:
            # 获取结构化输出的 LLM
            structured_llm = self.llm_client.get_structured_llm(SpeakingOrderDecision)
            
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            decision = await structured_llm.ainvoke(messages)
            
            return decision.use_order
        except Exception as e:
            # LLM 调用失败，默认顺序发言
            print(f"⚠️  警长 {self.name} 发言顺序决策 LLM 调用失败: {e}")
            return True

