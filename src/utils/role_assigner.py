"""
身份分配工具
"""
import random
from typing import List, Dict
from ..state.game_state import Player


def assign_roles(player_names: List[str], role_config: Dict[str, int] = None) -> List[Player]:
    """
    随机分配身份
    
    Args:
        player_names: 玩家名称列表
        role_config: 角色配置，格式为 {role: count}
                    默认配置：4人局（2村民+2狼人），6人局（3村民+2狼人+1预言家），
                    8人局（3村民+2狼人+1预言家+1女巫+1守卫）
    
    Returns:
        分配好身份的玩家列表
    """
    if role_config is None:
        # 根据玩家数量自动配置
        num_players = len(player_names)
        if num_players == 4:
            role_config = {"villager": 2, "werewolf": 2}
        elif num_players == 6:
            role_config = {"villager": 3, "werewolf": 2, "seer": 1}
        elif num_players == 8:
            role_config = {"villager": 3, "werewolf": 2, "seer": 1, "witch": 1, "guard": 1}
        else:
            # 默认配置：至少2个狼人，其他为村民
            num_werewolves = max(2, num_players // 4)
            role_config = {
                "villager": num_players - num_werewolves,
                "werewolf": num_werewolves
            }
    
    # 生成角色列表
    roles = []
    for role, count in role_config.items():
        roles.extend([role] * count)
    
    # 随机打乱
    random.shuffle(roles)
    
    # 创建玩家对象
    players = []
    for i, (name, role) in enumerate(zip(player_names, roles), 1):
        players.append(Player(
            player_id=i,
            name=name,
            role=role,
            is_alive=True,
            is_sheriff=False
        ))
    
    return players


def get_role_name_cn(role: str) -> str:
    """获取角色中文名称"""
    role_map = {
        "villager": "村民",
        "werewolf": "狼人",
        "seer": "预言家",
        "witch": "女巫",
        "guard": "守卫",
    }
    return role_map.get(role, role)

