#!/usr/bin/env python3
"""
测试运行脚本
一键执行所有测试用例
"""
import sys
import subprocess
import os
from pathlib import Path

def main():
    """运行所有测试"""
    # 获取项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("=" * 60)
    print("🧪 Cyber-Werewolf 测试套件")
    print("=" * 60)
    print()
    
    # 检查 pytest 是否安装
    try:
        import pytest
    except ImportError:
        print("❌ 错误: pytest 未安装")
        print("请运行: pip install pytest pytest-asyncio")
        sys.exit(1)
    
    # 运行测试
    print("📋 运行测试用例...")
    print()
    
    # 使用 pytest 运行测试
    # -v: 详细输出
    # -q: 简洁输出（与 -v 冲突，这里用 -v）
    # --tb=short: 简短的错误追踪
    # --color=yes: 彩色输出
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ],
        cwd=project_root
    )
    
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())

