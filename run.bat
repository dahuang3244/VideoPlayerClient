@echo off
setlocal

:: 设置默认文件
set DEFAULT_FILE=src/main.py

:: 获取用户输入
set /p targetFile="请输入要运行的 Python 文件路径 (直接回车默认运行 %DEFAULT_FILE%): "

:: 如果用户直接回车，使用默认文件
if "%targetFile%"=="" set targetFile=%DEFAULT_FILE%

:: 检查文件是否存在
if not exist "%targetFile%" (
    echo [错误] 找不到文件: %targetFile%
    pause
    exit /b 1
)

:: 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 找不到虚拟环境 (.venv\Scripts\python.exe)
    echo 请先运行: python -m venv .venv
    pause
    exit /b 1
)

:: 运行程序
echo [运行] 正在启动 %targetFile% ...
".venv\Scripts\python.exe" "%targetFile%"

:: 结束后暂停，防止窗口直接关闭
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 程序异常退出，错误代码: %ERRORLEVEL%
)
pause
