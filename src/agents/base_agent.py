"""
基础 Agent 类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
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

