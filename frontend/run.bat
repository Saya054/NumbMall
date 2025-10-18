@echo off
chcp 65001 >nul
echo ====================================
echo 大拇哥积分商城 - 前端启动脚本
echo ====================================
echo.

REM 检查 Node.js
where node >nul 2>nul
if errorlevel 1 (
    echo [×] 错误: 未安装 Node.js
    echo [!] 请访问 https://nodejs.org/ 下载安装
    pause
    exit /b 1
)

REM 检查依赖
if not exist node_modules (
    echo [!] 依赖包未安装，正在安装...
    echo [*] 使用国内镜像源加速...
    call npm install --registry=https://registry.npmmirror.com
)

echo.
echo [√] 准备就绪，正在启动前端服务...
echo [*] 前端地址: http://localhost:5173
echo [*] 按 Ctrl+C 停止服务
echo.
echo ====================================
echo.

call npm run dev

pause



