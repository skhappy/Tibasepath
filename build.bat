@echo off
echo 检查依赖...
python -c "import PyQt5; import watchdog; import configparser; import PIL; import win32api" 2>nul
if errorlevel 1 (
    echo 缺少必要的依赖，请先运行 install_dependencies.bat
    pause
    exit /b 1
)

echo 正在构建 Tibasepath...

REM 清理旧的构建文件
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"
if exist "*.spec" del /f /q "*.spec"

REM 使用 PyInstaller 构建
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --icon=metrohm.ico ^
    --add-data "metrohm.ico;." ^
    --add-data "logger.py;." ^
    --add-data "single_instance.py;." ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=PIL ^
    --name Tibasepath ^
    Tibasepath.py

REM 复制必要文件到 dist 目录
copy metrohm.ico dist\
copy tibasepath.conf dist\ 2>nul
if not exist "dist\Logs" mkdir "dist\Logs"

echo 检查构建结果...
if not exist "dist\Tibasepath.exe" (
    echo 构建失败！
    pause
    exit /b 1
)

echo 构建完成！
pause