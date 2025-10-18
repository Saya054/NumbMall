@echo off
chcp 65001 >nul
title 重置测试用户密码
echo.
echo ════════════════════════════════════
echo   重置所有测试用户密码
echo ════════════════════════════════════
echo.
echo 提示：运行此脚本前请确保：
echo 1. MySQL 服务已启动
echo 2. 已修改脚本中的数据库密码
echo.
pause

cd backend
python reset_passwords_simple.py

pause



