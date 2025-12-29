"""
游戏演示示例
"""
import asyncio
from src.state.game_state import StateManager, Player
from src.agents.villager import VillagerAgent
from src.agents.werewolf import WerewolfAgent


async def main():
    """主函数"""
    print("🐺 Cyber-Werewolf 游戏演示")
    print("=" * 50)
    
    # 初始化状态管理器
    state_manager = StateManager()
    
    # 创建玩家
    players = [
        Player(player_id=1, name="玩家1", role="villager"),
        Player(player_id=2, name="玩家2", role="villager"),
        Player(player_id=3, name="玩家3", role="werewolf"),
        Player(player_id=4, name="玩家4", role="werewolf"),
    ]
    
    # 初始化游戏状态
    state = state_manager.init_state(players)
    print(f"游戏状态初始化完成，共 {len(players)} 名玩家")
    print(f"当前阶段: {state['current_phase']}")
    print(f"游戏状态: {state['game_status']}")
    
    # 创建 Agent
    agents = [
        VillagerAgent(agent_id=1, name="玩家1"),
        VillagerAgent(agent_id=2, name="玩家2"),
        WerewolfAgent(agent_id=3, name="玩家3"),
        WerewolfAgent(agent_id=4, name="玩家4"),
    ]
    
    print("\nAgent 创建完成:")
    for agent in agents:
        print(f"  - {agent.name} ({agent.role})")
    
    print("\n✅ 演示完成！")
    print("提示: 完整游戏流程需要实现 LangGraph 工作流")


if __name__ == "__main__":
    asyncio.run(main())

