"""
测试 DeepSeek-V3 API 连接
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from src.utils.llm_client import LLMClient

load_dotenv()


async def test_deepseek_connection():
    """测试 DeepSeek API 连接"""
    print("🔍 测试 DeepSeek-V3 API 连接...")
    print("=" * 50)
    
    try:
        # 创建 DeepSeek 客户端
        client = LLMClient(provider="deepseek", temperature=0.7)
        print("✅ LLM 客户端创建成功")
        
        # 测试简单调用
        system_prompt = "你是一个狼人杀游戏中的村民。你需要通过观察和分析找出狼人。"
        user_prompt = "当前游戏中有4名玩家，其中2名是狼人。玩家1在发言时逻辑矛盾，玩家2表现正常。你会投票给谁？"
        
        print("\n📤 发送测试请求...")
        response = await client.call(system_prompt, user_prompt)
        
        print("\n📥 DeepSeek 响应:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        print("\n✅ DeepSeek-V3 API 连接测试成功！")
        
    except ValueError as e:
        print(f"\n❌ 配置错误: {e}")
        print("\n💡 提示: 请确保在 .env 文件中配置了 DEEPSEEK_API_KEY")
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n💡 请检查:")
        print("  1. API Key 是否正确")
        print("  2. 网络连接是否正常")
        print("  3. DeepSeek API 服务是否可用")


async def test_structured_output():
    """测试结构化输出"""
    print("\n\n🔍 测试结构化输出...")
    print("=" * 50)
    
    from src.schemas.actions import AgentAction
    
    client = LLMClient(provider="deepseek")
    structured_llm = client.get_structured_llm(AgentAction)
    
    system_prompt = """你是一个狼人杀游戏中的村民。你需要输出结构化的行动指令。
行动类型包括: vote, kill, check, save, guard, skip"""
    
    user_prompt = """当前游戏状态：
- 玩家1: 发言逻辑矛盾，可疑
- 玩家2: 表现正常
- 玩家3: 你（村民）
- 玩家4: 表现正常

请输出你的投票决策。"""
    
    print("📤 发送结构化输出请求...")
    action = await structured_llm.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])
    
    print("\n📥 结构化输出结果:")
    print("-" * 50)
    print(f"推理: {action.thought}")
    print(f"行动类型: {action.action_type}")
    print(f"目标: {action.target}")
    print(f"置信度: {action.confidence}")
    print(f"理由: {action.reasoning}")
    print("-" * 50)
    
    print("\n✅ 结构化输出测试成功！")


async def main():
    """主函数"""
    print("🐺 Cyber-Werewolf - DeepSeek-V3 API 测试\n")
    
    # 检查环境变量
    has_api_key = bool(os.getenv("DEEPSEEK_API_KEY"))
    if not has_api_key:
        print("⚠️  警告: 未找到 DEEPSEEK_API_KEY 环境变量")
        print("💡 请在 .env 文件中配置:")
        print("   DEEPSEEK_API_KEY=your_api_key_here\n")
        print("=" * 50)
        print("❌ 测试无法继续：缺少 API Key")
        print("=" * 50)
        return
    
    # 测试结果跟踪
    results = {
        "connection": False,
        "structured": False
    }
    
    # 测试连接
    try:
        await test_deepseek_connection()
        results["connection"] = True
    except Exception as e:
        print(f"\n❌ 连接测试失败: {e}")
    
    # 测试结构化输出
    try:
        await test_structured_output()
        results["structured"] = True
    except Exception as e:
        print(f"\n❌ 结构化输出测试失败: {e}")
    
    # 显示测试结果摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要")
    print("=" * 50)
    print(f"  API 连接测试: {'✅ 通过' if results['connection'] else '❌ 失败'}")
    print(f"  结构化输出测试: {'✅ 通过' if results['structured'] else '❌ 失败'}")
    
    if all(results.values()):
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

