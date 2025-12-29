#!/bin/bash
# 测试运行脚本（Shell 版本）
# 一键执行所有测试用例

set -e

echo "============================================================"
echo "🧪 Cyber-Werewolf 测试套件"
echo "============================================================"
echo ""

# 检查 pytest 是否安装
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "❌ 错误: pytest 未安装"
    echo "请运行: pip install pytest pytest-asyncio"
    exit 1
fi

# 运行测试
echo "📋 运行测试用例..."
echo ""

# 使用 pytest 运行测试
python3 -m pytest tests/ -v --tb=short --color=yes

# 获取退出码
EXIT_CODE=$?

echo ""
echo "============================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 所有测试通过！"
else
    echo "❌ 部分测试失败"
fi
echo "============================================================"

exit $EXIT_CODE

