#!/bin/bash
# 测试运行脚本（Shell 版本）
# 一键执行所有测试用例，显示详细的测试执行情况

set -e

echo "======================================================================"
echo "🧪 Cyber-Werewolf 测试套件"
echo "======================================================================"
echo ""

# 检查 pytest 是否安装
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "❌ 错误: pytest 未安装"
    echo "请运行: pip install pytest pytest-asyncio"
    exit 1
fi

# 收集测试用例
echo "📋 收集测试用例..."
TEST_COUNT=$(python3 -m pytest tests/ --collect-only -q 2>/dev/null | grep -c "::test_" || echo "0")
echo "   找到 $TEST_COUNT 个测试用例"
echo ""

# 显示测试列表
echo "📝 测试列表:"
python3 -m pytest tests/ --collect-only -q 2>/dev/null | grep "::test_" | nl -w2 -s'. '
echo ""

# 运行测试
echo "🚀 开始执行测试..."
echo "----------------------------------------------------------------------"

# 使用 pytest 运行测试
# -v: 详细输出
# --tb=short: 简短的错误追踪
# --color=yes: 彩色输出
# -rA: 显示所有测试结果摘要
python3 -m pytest tests/ -v --tb=short --color=yes -rA

# 获取退出码
EXIT_CODE=$?

echo ""
echo "======================================================================"
echo "📊 测试执行摘要"
echo "======================================================================"
echo ""

# 解析测试结果
PASSED=$(python3 -m pytest tests/ -v --tb=no 2>/dev/null | grep -c "PASSED" || echo "0")
FAILED=$(python3 -m pytest tests/ -v --tb=no 2>/dev/null | grep -c "FAILED" || echo "0")
SKIPPED=$(python3 -m pytest tests/ -v --tb=no 2>/dev/null | grep -c "SKIPPED" || echo "0")
ERROR=$(python3 -m pytest tests/ -v --tb=no 2>/dev/null | grep -c "ERROR" || echo "0")

TOTAL=$((PASSED + FAILED + SKIPPED + ERROR))

echo "总计: $TOTAL 个测试"
echo "  ✅ 通过: $PASSED"
if [ $FAILED -gt 0 ]; then
    echo "  ❌ 失败: $FAILED"
fi
if [ $SKIPPED -gt 0 ]; then
    echo "  ⏭️  跳过: $SKIPPED"
fi
if [ $ERROR -gt 0 ]; then
    echo "  ⚠️  错误: $ERROR"
fi
echo ""

# 显示失败的测试
if [ $FAILED -gt 0 ] || [ $ERROR -gt 0 ]; then
    echo "======================================================================"
    echo "❌ 失败的测试"
    echo "======================================================================"
    echo ""
    python3 -m pytest tests/ -v --tb=no 2>/dev/null | grep -E "(FAILED|ERROR)" | sed 's/^/  /'
    echo ""
fi

echo "======================================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 所有测试通过！"
else
    echo "❌ 测试执行完成，但有 $((FAILED + ERROR)) 个测试失败"
fi
echo "======================================================================"

exit $EXIT_CODE

