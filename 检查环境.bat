@echo off
chcp 65001 >nul
echo ====================================
echo 大拇哥积分商城 - 环境检查工具
echo ====================================
echo.

set ALL_OK=1

echo [1/4] 检查 Python...
where python >nul 2>nul
if errorlevel 1 (
    echo [×] Python 未安装
    echo [!] 请访问 https://www.python.org/ 下载安装 Python 3.8+
    set ALL_OK=0
) else (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
    echo [√] !PYTHON_VER!
)
echo.

echo [2/4] 检查 Node.js...
where node >nul 2>nul
if errorlevel 1 (
    echo [×] Node.js 未安装
    echo [!] 请访问 https://nodejs.org/ 下载安装 Node.js 16+
    set ALL_OK=0
) else (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
    echo [√] Node.js !NODE_VER!
)
echo.

echo [3/4] 检查 MySQL...
where mysql >nul 2>nul
if errorlevel 1 (
    echo [×] MySQL 未安装或未添加到 PATH
    echo [!] 请确保 MySQL 8.0+ 已安装并运行
    set ALL_OK=0
) else (
    echo [√] MySQL 已安装
)
echo.

echo [4/4] 检查项目文件...
if not exist "backend\app.py" (
    echo [×] 后端文件不完整
    set ALL_OK=0
) else (
    echo [√] 后端文件完整
)

if not exist "frontend\package.json" (
    echo [×] 前端文件不完整
    set ALL_OK=0
) else (
    echo [√] 前端文件完整
)

if not exist "database\init.sql" (
    echo [×] 数据库脚本不存在
    set ALL_OK=0
) else (
    echo [√] 数据库脚本存在
)
echo.

echo ====================================
if "%ALL_OK%"=="1" (
    echo [√] 环境检查通过！
    echo.
    echo 下一步：
    echo 1. 初始化数据库: mysql -u root -p ^< database\init.sql
    echo 2. 修改后端配置: backend\config.py 中的数据库密码
    echo 3. 启动后端: 双击 backend\run.bat
    echo 4. 启动前端: 双击 frontend\run.bat
) else (
    echo [×] 环境检查未通过，请根据上述提示安装缺失的软件
)
echo ====================================
echo.

pause



