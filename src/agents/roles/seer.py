"""
预言家 Agent
"""
from typing import Dict, Any, List, Optional
from ..base_agent import BaseAgent
from ...schemas.actions import AgentAction


class SeerAgent(BaseAgent):
    """预言家角色 Agent"""
    
    def __init__(self, agent_id: int, name: str, llm_client=None):
        super().__init__(agent_id, "seer", name, llm_client)
        self.check_history = []  # 查验历史
    
    async def observe(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """预言家可以看到公共信息和自己的查验结果"""
        return {
            "public_info": game_state.get("public_info", {}),
            "alive_players": game_state.get("alive_players", []),
            "check_history": self.check_history,
            "seer_checks": game_state.get("seer_checks", {}),
        }
    
    async def think(self, observation: Dict[str, Any]) -> str:
        """预言家的推理逻辑"""
        # TODO: 使用 LLM 进行推理
        return "作为预言家，我需要通过查验找出狼人，并引导好人投票。"
    
    async def act(self, observation: Dict[str, Any]) -> AgentAction:
        """预言家的行动（查验）"""
        # 这个方法主要用于通用行动，实际查验通过 check_player 方法
        return AgentAction(
            thought="我需要查验一名可疑的玩家",
            action_type="check",
            target=None,
            confidence=0.5,
            reasoning="基于观察和推理"
        )
    
    async def decide_check_target(self, game_state: Dict[str, Any]) -> Optional[int]:
        """
        使用 LLM 决定查验目标
        
        Args:
            game_state: 游戏状态
        
        Returns:
            目标玩家ID，如果不查验则返回 None
        """
        observation = await self.observe(game_state)
        
        # 构建 prompt
        from ...utils.prompt_builder import build_seer_prompt
        system_prompt, user_prompt = build_seer_prompt(
            self.agent_id,
            self.name,
            game_state,
            observation
        )
        
        # 获取结构化输出的 LLM
        structured_llm = self.llm_client.get_structured_llm(AgentAction)
        
        try:
            # 调用 LLM（使用 LangChain 消息格式）
            from langchain_core.messages import SystemMessage, HumanMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            action = await structured_llm.ainvoke(messages)
            
            # 验证返回的 action
            if action.action_type == "check" and action.target:
                # 验证目标玩家是否存在且存活
                players = game_state.get("players", [])
                target_player = next(
                    (p for p in players if p.player_id == action.target and p.is_alive),
                    None
                )
                if target_player and target_player.player_id != self.agent_id:
                    return action.target
            
            return None
        except Exception as e:
            # LLM 调用失败，返回 None
            print(f"⚠️  预言家 {self.name} LLM 调用失败: {e}")
            return None
    
    async def check_player(self, game_state: Dict[str, Any], target_id: int) -> Dict[str, str]:
        """
        查验玩家身份
        
        Args:
            game_state: 游戏状态
            target_id: 目标玩家ID
        
        Returns:
            查验结果 {"target_id": "好人" 或 "狼人"}
        """
        players = game_state.get("players", [])
        target_player = next((p for p in players if p.player_id == target_id), None)
        
        if target_player:
            # 预言家只能知道是好人还是狼人，不能知道具体身份
            if target_player.role == "werewolf":
                result = {target_id: "狼人"}
            else:
                result = {target_id: "好人"}
            self.check_history.append(result)
            return result
        return {}


async def create_seer_agent(agent_id: int, name: str, llm_client=None) -> SeerAgent:
    """创建预言家 Agent"""
    return SeerAgent(agent_id, name, llm_client)

