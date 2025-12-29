"""
游戏状态定义
"""
from typing import List, Dict, Any, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel


class Player(BaseModel):
    """玩家信息"""
    player_id: int
    name: str
    role: str
    is_alive: bool = True
    vote_target: Optional[int] = None


class GameState(TypedDict):
    """游戏全局状态"""
    players: List[Player]
    current_phase: Literal["day", "night"]
    round_number: int
    day_number: int
    game_status: Literal["playing", "ended"]
    winner: Optional[str]
    public_info: Dict[str, Any]
    werewolf_channel: Dict[str, Any]
    history: List[Dict[str, Any]]


class StateManager:
    """状态管理器"""
    
    def __init__(self):
        self.state: Optional[GameState] = None
    
    def init_state(self, players: List[Player]) -> GameState:
        """初始化游戏状态"""
        self.state = {
            "players": players,
            "current_phase": "day",
            "round_number": 1,
            "day_number": 1,
            "game_status": "playing",
            "winner": None,
            "public_info": {},
            "werewolf_channel": {},
            "history": [],
        }
        return self.state
    
    def update_state(self, updates: Dict[str, Any]) -> GameState:
        """更新游戏状态"""
        if self.state is None:
            raise ValueError("State not initialized")
        self.state.update(updates)
        return self.state
    
    def get_state(self) -> Optional[GameState]:
        """获取当前状态"""
        return self.state

