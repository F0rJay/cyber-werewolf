"""
游戏状态定义
"""
from typing import List, Dict, Any, Optional, Literal, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel
import operator


class Player(BaseModel):
    """玩家信息"""
    player_id: int
    name: str
    role: str
    is_alive: bool = True
    vote_target: Optional[int] = None
    is_sheriff: bool = False  # 是否为警长


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
    history: Annotated[List[Dict[str, Any]], operator.add]  # 允许多个节点追加历史记录
    # 投票相关
    votes: Dict[int, int]  # {voter_id: target_id}
    vote_results: Dict[int, int]  # {target_id: vote_count}
    # 发言相关
    discussions: List[Dict[str, Any]]  # 发言记录
    current_speaker: Optional[int]  # 当前发言玩家ID
    # 夜晚行动相关
    night_actions: Dict[str, Dict[str, Any]]  # {role: {agent_id: target_id}}
    # 熔断机制
    max_rounds: int  # 最大轮次限制
    consecutive_ties: int  # 连续平票次数
    # 平票重议相关
    tie_vote_round: int  # 平票重议轮次（1=第一轮，2=第二轮）
    tied_players: List[int]  # 平票的玩家ID列表
    # 警长相关
    sheriff_candidates: List[int]  # 警长竞选者ID列表
    sheriff_votes: Dict[int, int]  # 警长投票 {voter_id: candidate_id}
    sheriff_vote_round: int  # 警长投票轮次（1=第一轮，2=第二轮）
    sheriff_tied_candidates: List[int]  # 警长投票平票的候选人ID列表
    sheriff_withdrawn: List[int]  # 退水的玩家ID列表
    sheriff_transfer: Optional[Dict[str, Any]]  # 警长移交信息 {from_id: int, to_id: Optional[int], destroyed: bool}
    # 角色特殊能力相关
    seer_checks: Dict[int, str]  # 预言家查验结果 {target_id: "好人" 或 "狼人"}
    witch_antidote_used: bool  # 女巫解药是否已使用
    witch_poison_used: bool  # 女巫毒药是否已使用
    guard_protected: Optional[int]  # 守卫守护的玩家ID（上一晚）
    guard_protected_tonight: Optional[int]  # 守卫今晚守护的玩家ID
    # 自爆相关
    self_exploded: Optional[int]  # 自爆的玩家ID
    # 遗言相关
    last_words: Dict[int, str]  # 遗言 {player_id: last_word}
    # 初始角色统计（用于游戏结束判定）
    initial_gods_count: int  # 初始神职数量
    initial_villagers_count: int  # 初始村民数量


class StateManager:
    """状态管理器"""
    
    def __init__(self):
        self.state: Optional[GameState] = None
    
    def init_state(self, players: List[Player], max_rounds: int = 20) -> GameState:
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
            "votes": {},
            "vote_results": {},
            "discussions": [],
            "current_speaker": None,
            "night_actions": {},
            "max_rounds": max_rounds,
            "consecutive_ties": 0,
            "tie_vote_round": 0,  # 0表示正常投票，1=第一轮平票，2=第二轮平票
            "tied_players": [],
            "sheriff_candidates": [],
            "sheriff_votes": {},
            "sheriff_vote_round": 0,
            "sheriff_tied_candidates": [],
            "sheriff_withdrawn": [],
            "sheriff_transfer": None,
            "seer_checks": {},
            "witch_antidote_used": False,
            "witch_poison_used": False,
            "guard_protected": None,
            "guard_protected_tonight": None,
            "self_exploded": None,
            "last_words": {},
            # 记录初始角色统计
            "initial_gods_count": len([p for p in players if p.role in ["seer", "witch", "guard"]]),
            "initial_villagers_count": len([p for p in players if p.role == "villager"]),
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

