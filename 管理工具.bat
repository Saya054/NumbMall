@echo off
chcp 65001 >nul
title 大拇哥积分商城 - 管理工具

REM 检查 PyQt5
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyQt5...
    pip install PyQt5 -i https://pypi.tuna.tsinghua.edu.cn/simple
)

REM 启动管理工具
python manage_tool.py

pause



