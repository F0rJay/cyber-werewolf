#!/usr/bin/env python3
"""
测试运行脚本
一键执行所有测试用例，显示详细的测试执行情况
"""
import sys
import subprocess
import os
import re
from pathlib import Path
from collections import defaultdict

def collect_tests(project_root):
    """收集所有测试用例"""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    tests = []
    for line in result.stdout.split('\n'):
        line = line.strip()
        if '::' in line and 'test_' in line:
            tests.append(line)
    
    return tests

def parse_test_results(output):
    """解析测试结果"""
    results = {
        'passed': [],
        'failed': [],
        'skipped': [],
        'error': [],
        'test_map': {}  # 完整路径 -> 状态
    }
    
    # 解析测试结果行
    # 格式: tests/test_xxx.py::test_function PASSED [ 10%]
    test_pattern = r'(tests/[^:]+::[^\s]+)\s+(\w+)(?:\s+\[.*?\])?'
    
    for line in output.split('\n'):
        match = re.search(test_pattern, line)
        if match:
            test_path = match.group(1)
            status = match.group(2).upper()
            
            # 提取测试名称（最后一部分）
            test_name = test_path.split('::')[-1]
            results['test_map'][test_path] = status
            
            if status == 'PASSED':
                results['passed'].append(test_name)
            elif status == 'FAILED':
                results['failed'].append(test_name)
            elif status == 'SKIPPED':
                results['skipped'].append(test_name)
            elif status == 'ERROR':
                results['error'].append(test_name)
    
    return results

def print_test_summary(results, tests):
    """打印测试摘要"""
    print("\n" + "=" * 70)
    print("📊 测试执行摘要")
    print("=" * 70)
    print()
    
    # 按文件分组显示
    test_files = defaultdict(list)
    for test_path in tests:
        if '::' in test_path:
            parts = test_path.split('::')
            file_name = parts[0]
            test_name = parts[-1]
            status = results['test_map'].get(test_path, 'UNKNOWN')
            test_files[file_name].append((test_name, status))
    
    # 显示每个测试文件的结果
    for file_name in sorted(test_files.keys()):
        print(f"📁 {file_name}")
        file_tests = test_files[file_name]
        for test_name, status in file_tests:
            if status == 'PASSED':
                status_icon = "✅ PASSED"
            elif status == 'FAILED':
                status_icon = "❌ FAILED"
            elif status == 'SKIPPED':
                status_icon = "⏭️  SKIPPED"
            elif status == 'ERROR':
                status_icon = "⚠️  ERROR"
            else:
                status_icon = "❓ UNKNOWN"
            
            print(f"   {status_icon:15} {test_name}")
        print()
    
    # 显示统计信息
    print("-" * 70)
    total = len(results['test_map'])
    passed = len(results['passed'])
    failed = len(results['failed'])
    skipped = len(results['skipped'])
    error = len(results['error'])
    
    if total > 0:
        print(f"总计: {total} 个测试")
        print(f"  ✅ 通过: {passed} ({passed*100//total}%)")
        if failed > 0:
            print(f"  ❌ 失败: {failed} ({failed*100//total}%)")
        if skipped > 0:
            print(f"  ⏭️  跳过: {skipped} ({skipped*100//total}%)")
        if error > 0:
            print(f"  ⚠️  错误: {error} ({error*100//total}%)")
    print()

def main():
    """运行所有测试"""
    # 获取项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("=" * 70)
    print("🧪 Cyber-Werewolf 测试套件")
    print("=" * 70)
    print()
    
    # 检查 pytest 是否安装
    try:
        import pytest
    except ImportError:
        print("❌ 错误: pytest 未安装")
        print("请运行: pip install pytest pytest-asyncio")
        sys.exit(1)
    
    # 收集所有测试用例
    print("📋 收集测试用例...")
    tests = collect_tests(project_root)
    print(f"   找到 {len(tests)} 个测试用例")
    print()
    
    # 显示测试列表
    if tests:
        print("📝 测试列表:")
        for i, test in enumerate(tests, 1):
            # 只显示测试名称，不显示完整路径
            test_name = test.split('::')[-1] if '::' in test else test
            print(f"   {i:2d}. {test_name}")
        print()
    
    # 运行测试
    print("🚀 开始执行测试...")
    print("-" * 70)
    
    # 使用 pytest 运行测试并捕获输出
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    
    # 打印测试执行输出
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    # 解析测试结果
    results = parse_test_results(result.stdout)
    
    # 打印摘要（总是显示，即使没有结果）
    print()
    print_test_summary(results, tests)
    
    # 显示失败的测试详情
    failed_tests = []
    for test_path, status in results['test_map'].items():
        if status in ['FAILED', 'ERROR']:
            failed_tests.append(test_path)
    
    if failed_tests:
        print("=" * 70)
        print("❌ 失败的测试详情")
        print("=" * 70)
        print()
        
        # 从原始输出中提取失败信息
        in_failure_section = False
        failure_lines = []
        current_test = None
        
        for line in result.stdout.split('\n'):
            # 检测失败测试的开始
            if 'FAILED' in line or 'ERROR' in line:
                if '::' in line:
                    # 提取测试路径
                    match = re.search(r'(tests/[^:]+::[^\s]+)', line)
                    if match:
                        if current_test and failure_lines:
                            print(f"🔍 {current_test}")
                            print("-" * 70)
                            print('\n'.join(failure_lines[:50]))  # 限制输出行数
                            print()
                        current_test = match.group(1)
                        failure_lines = []
                        in_failure_section = True
            elif in_failure_section:
                # 收集错误信息直到遇到分隔符
                if line.strip() and not line.startswith('='):
                    failure_lines.append(line)
                elif line.startswith('=' * 20):
                    if current_test and failure_lines:
                        print(f"🔍 {current_test}")
                        print("-" * 70)
                        print('\n'.join(failure_lines[:50]))
                        print()
                    in_failure_section = False
                    failure_lines = []
        
        # 处理最后一个失败
        if current_test and failure_lines:
            print(f"🔍 {current_test}")
            print("-" * 70)
            print('\n'.join(failure_lines[:50]))
            print()
    
    # 最终状态
    print("=" * 70)
    if result.returncode == 0:
        print("✅ 所有测试通过！")
    else:
        failed_count = len(results['failed']) + len(results['error'])
        print(f"❌ 测试执行完成，但有 {failed_count} 个测试失败")
    print("=" * 70)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
