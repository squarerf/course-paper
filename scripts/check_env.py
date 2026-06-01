#!/usr/bin/env python3
"""环境检测脚本 - 检查 course-paper skill 的运行依赖"""

import shutil
import sys
import os
import platform
import subprocess
import json

def find_python():
    """按优先级检测可用的 Python 路径，跳过 Windows Store stub"""
    for cmd in ['python', 'python3', 'py']:
        path = shutil.which(cmd)
        if path:
            # Windows Store stub 通常是 0 字节
            if os.path.getsize(path) > 100:
                return cmd
    return None

def check_node():
    """检测 Node.js 是否可用"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return None

def check_python_deps():
    """检测 Python 依赖是否安装"""
    missing = []
    for pkg in ['matplotlib', 'numpy']:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return missing

def check_node_deps(script_dir):
    """检测 Node.js 依赖是否安装"""
    pkg_json = os.path.join(script_dir, 'package.json')
    node_modules = os.path.join(script_dir, 'node_modules')
    if not os.path.exists(node_modules):
        return ['docx']
    return []

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results = {
        'platform': platform.system(),
        'python': None,
        'python_version': None,
        'node': None,
        'python_deps_missing': [],
        'node_deps_missing': [],
        'issues': []
    }

    # 检测 Python
    python_cmd = find_python()
    if python_cmd:
        results['python'] = python_cmd
        try:
            ver = subprocess.run([python_cmd, '--version'], capture_output=True, text=True)
            results['python_version'] = ver.stdout.strip()
        except:
            pass
    else:
        results['issues'].append('Python 未安装或不可用')

    # 检测 Node.js
    node_ver = check_node()
    if node_ver:
        results['node'] = node_ver
    else:
        results['issues'].append('Node.js 未安装')

    # 检测 Python 依赖
    if python_cmd:
        missing = check_python_deps()
        results['python_deps_missing'] = missing
        if missing:
            results['issues'].append(f'Python 依赖缺失: {", ".join(missing)}')

    # 检测 Node.js 依赖
    node_missing = check_node_deps(script_dir)
    results['node_deps_missing'] = node_missing
    if node_missing:
        results['issues'].append(f'Node.js 依赖缺失: {", ".join(node_missing)}')

    # 输出结果
    print(json.dumps(results, ensure_ascii=False, indent=2))

    # 返回状态码
    return 1 if results['issues'] else 0

if __name__ == '__main__':
    sys.exit(main())
