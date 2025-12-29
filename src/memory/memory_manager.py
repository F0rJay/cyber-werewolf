"""
记忆管理器：分级记忆系统
"""
from typing import List, Dict, Any
from enum import Enum


class MemoryLevel(Enum):
    """记忆级别"""
    PUBLIC = "public"      # 公共记忆
    ROLE = "role"          # 角色记忆
    PRIVATE = "private"    # 私有记忆


class Memory:
    """记忆单元"""
    def __init__(self, content: str, level: MemoryLevel, metadata: Dict[str, Any] = None):
        self.content = content
        self.level = level
        self.metadata = metadata or {}


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self):
        self.memories: List[Memory] = []
    
    def add_memory(self, content: str, level: MemoryLevel, metadata: Dict[str, Any] = None):
        """添加记忆"""
        memory = Memory(content, level, metadata)
        self.memories.append(memory)
    
    def get_memories_for_agent(self, agent_id: int, role: str) -> List[Memory]:
        """根据 Agent 角色获取可见记忆"""
        from .filters import filter_memory_for_agent
        return filter_memory_for_agent(agent_id, role, self.memories)

