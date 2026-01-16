#!/bin/bash

echo "AI审稿系统启动中..."
echo ""

# 激活虚拟环境
if [ -f "AIreviewer/bin/activate" ]; then
    source AIreviewer/bin/activate
else
    echo "警告: 未找到虚拟环境，使用系统Python"
fi

# 运行主程序
python main.py
