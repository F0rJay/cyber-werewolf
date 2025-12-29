"""
记忆过滤函数：防止信息泄露
"""
from typing import List
from .memory_manager import Memory, MemoryLevel


def filter_memory_for_agent(agent_id: int, role: str, all_memories: List[Memory]) -> List[Memory]:
    """
    根据角色过滤可见信息
    
    Args:
        agent_id: Agent ID
        role: Agent 角色
        all_memories: 所有记忆
    
    Returns:
        过滤后的记忆列表
    """
    visible_memories = []
    
    for memory in all_memories:
        # 公共记忆：所有角色可见
        if memory.level == MemoryLevel.PUBLIC:
            visible_memories.append(memory)
        
        # 角色记忆：特定角色可见
        elif memory.level == MemoryLevel.ROLE:
            if memory.metadata.get("role") == role:
                visible_memories.append(memory)
        
        # 私有记忆：仅特定 Agent 可见
        elif memory.level == MemoryLevel.PRIVATE:
            if memory.metadata.get("agent_id") == agent_id:
                visible_memories.append(memory)
        
        # 狼人频道：仅狼人可见
        elif memory.level == MemoryLevel.ROLE and memory.metadata.get("channel") == "werewolf":
            if role == "werewolf":
                visible_memories.append(memory)
    
    return visible_memories

