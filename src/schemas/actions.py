"""
Agent 行动指令 Schema
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    """Agent 行动指令（结构化输出）"""
    thought: str = Field(description="推理过程")
    action_type: Literal["vote", "kill", "check", "save", "guard", "explode", "skip"] = Field(
        description="行动类型"
    )
    target: Optional[int] = Field(
        default=None,
        description="目标玩家ID（如果适用）"
    )
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="置信度（0-1）"
    )
    reasoning: str = Field(
        default="",
        description="决策理由"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "thought": "我认为玩家3的行为可疑，可能是狼人",
                "action_type": "vote",
                "target": 3,
                "confidence": 0.75,
                "reasoning": "玩家3在发言时逻辑矛盾，且投票行为异常"
            }
        }

