#!/bin/bash
# 本地开发环境清理脚本

set -euo pipefail

PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$PROJECT_ROOT"

echo "======================================"
echo "清理本地开发环境"
echo "======================================"

# 1. 删除 Python 缓存
echo "[1/6] 清理 Python 缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✓ Python 缓存已清理"

# 2. 删除 macOS 系统文件
echo "[2/6] 清理 macOS 系统文件..."
find . -name ".DS_Store" -delete 2>/dev/null || true
echo "✓ .DS_Store 已清理"

# 3. 清理日志文件（保留目录）
echo "[3/6] 清理日志文件..."
if [ -d "logs" ]; then
    rm -f logs/*.log 2>/dev/null || true
    echo "✓ 日志文件已清理"
else
    echo "- 日志目录不存在"
fi

# 4. 询问是否删除虚拟环境
if [ -d ".venv" ]; then
    echo ""
    read -p "[4/6] 检测到虚拟环境 .venv/，是否删除？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .venv
        echo "✓ 虚拟环境已删除"
    else
        echo "- 保留虚拟环境"
    fi
else
    echo "[4/6] 无虚拟环境"
fi

# 5. 询问是否删除 IDE 配置
if [ -d ".idea" ]; then
    echo ""
    read -p "[5/6] 检测到 PyCharm 配置 .idea/，是否删除？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .idea
        echo "✓ IDE 配置已删除"
    else
        echo "- 保留 IDE 配置"
    fi
else
    echo "[5/6] 无 IDE 配置"
fi

# 6. 清理空目录
echo "[6/6] 清理空目录..."
if [ -d "deploy" ] && [ -z "$(ls -A deploy)" ]; then
    rm -rf deploy
    echo "✓ 空目录 deploy/ 已删除"
else
    echo "- deploy/ 目录非空或不存在"
fi

if [ -d "tests" ] && [ -z "$(ls -A tests)" ]; then
    rm -rf tests
    echo "✓ 空目录 tests/ 已删除"
else
    echo "- tests/ 目录非空或不存在"
fi

# 显示清理后的大小
echo ""
echo "======================================"
echo "清理完成！"
echo "======================================"
du -sh . 2>/dev/null || true
