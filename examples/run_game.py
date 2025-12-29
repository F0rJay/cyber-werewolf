"""
运行完整的狼人杀游戏示例
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.state.game_state import StateManager
from src.utils.role_assigner import assign_roles
from src.graph.game_graph import create_game_graph


async def main():
    """主函数"""
    print("🐺 Cyber-Werewolf 游戏开始！")
    print("=" * 60)
    
    # 创建状态管理器
    state_manager = StateManager()
    
    # 使用身份分配工具创建玩家（4人局：2村民 + 2狼人）
    player_names = ["玩家1", "玩家2", "玩家3", "玩家4"]
    players = assign_roles(player_names, role_config={"villager": 2, "werewolf": 2})
    
    # 初始化游戏状态
    initial_state = state_manager.init_state(players, max_rounds=10)
    print(f"\n📋 游戏配置：")
    print(f"  玩家数量: {len(players)}")
    print(f"  村民: {len([p for p in players if p.role == 'villager'])}")
    print(f"  狼人: {len([p for p in players if p.role == 'werewolf'])}")
    print(f"  最大轮次: {initial_state['max_rounds']}")
    print(f"  警长机制: ✅ 已启用（第一天竞选）")
    print(f"  平票机制: ✅ 已启用（第一轮平票→重议，第二轮平票→直接黑夜）")
    print("\n" + "=" * 60)
    
    # 创建游戏图
    game_graph = create_game_graph()
    
    # 运行游戏
    try:
        final_state = await game_graph.ainvoke(initial_state)
        
        print("\n" + "=" * 60)
        print("🎮 游戏结束！")
        print("=" * 60)
        print(f"获胜方: {final_state.get('winner', '未知')}")
        print(f"游戏状态: {final_state.get('game_status', 'unknown')}")
        print(f"总轮次: {final_state.get('round_number', 0)}")
        print(f"总天数: {final_state.get('day_number', 0)}")
        
        print("\n📊 最终存活玩家：")
        alive_players = [p for p in final_state["players"] if p.is_alive]
        for player in alive_players:
            sheriff_mark = " 👮" if player.is_sheriff else ""
            print(f"  - {player.name} ({player.role}){sheriff_mark}")
        
        # 显示警长信息
        sheriff = next((p for p in final_state["players"] if p.is_sheriff), None)
        if sheriff:
            print(f"\n👮 警长: {sheriff.name} (玩家{sheriff.player_id}) - {'存活' if sheriff.is_alive else '已淘汰'}")
        
        print("\n📜 游戏历史记录数：", len(final_state.get("history", [])))
        
    except Exception as e:
        print(f"\n❌ 游戏运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

