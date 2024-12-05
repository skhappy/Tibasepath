@echo off
echo 安装必要的依赖...
pip install watchdog
pip install pyinstaller
pip install pillow
pip install pystray
pip install PyQt5

echo 清理旧的构建文件...
rmdir /s /q dist
rmdir /s /q build
del /q *.spec

echo 使用PyInstaller构建可执行文件...
pyinstaller --noconfirm --onefile --windowed --icon=metrohm.ico --name Tibasepath ^
    --hidden-import=watchdog.observers ^
    --hidden-import=watchdog.observers.polling ^
    --hidden-import=watchdog.events ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtCore ^
    --hidden-import=PyQt5.QtGui ^
    --hidden-import=PyQt5.QtWidgets ^
    --hidden-import=pystray._win32 ^
    --add-data "metrohm.ico;." ^
    --add-data "logger.py;." ^
    --add-data "tibasepath.conf;." ^
    --collect-all watchdog ^
    --collect-all PyQt5 ^
    Tibasepath.py

echo 检查dist目录是否创建成功...
if not exist "dist\Tibasepath.exe" (
    echo 错误：PyInstaller构建失败！
    exit /b 1
)

echo 创建发布包...
mkdir "dist\Tibasepath"
move "dist\Tibasepath.exe" "dist\Tibasepath\"
copy "metrohm.ico" "dist\Tibasepath\"
copy "tibasepath.conf" "dist\Tibasepath\"
copy "README.md" "dist\Tibasepath\" 2>nul
mkdir "dist\Tibasepath\Logs"

echo 创建安装程序...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /O"Output" Tibasepath.iss

echo 构建完成！
pause