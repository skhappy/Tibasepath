@echo off
echo 正在安装必要的依赖...

REM 升级pip
python -m pip install --upgrade pip

REM 安装依赖
pip install -r requirements.txt

REM 检查安装结果
python -c "import PyQt5; import watchdog; import configparser; import PIL; import win32api" 2>nul
if errorlevel 1 (
    echo 依赖安装可能不完整，请检查错误信息
    pause
    exit /b 1
)

echo 依赖安装完成！
pause 