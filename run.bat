@echo off
chcp 65001 >nul
echo AI审稿系统启动中...
echo.

REM 激活虚拟环境
if exist AIreviewer\Scripts\activate.bat (
    call AIreviewer\Scripts\activate.bat
) else (
    echo 警告: 未找到虚拟环境，使用系统Python
)

REM 运行主程序
python main.py

pause
