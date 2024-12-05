# Tibasepath

Tibasepath 是一个文件监控和处理工具，主要用于监控指定文件夹中的 .utf8 文件，并进行自动处理和移动操作。

## 功能特点

- 实时监控指定文件夹中的 .utf8 文件
- 自动处理文件内容（第7行特定格式修改）
- 将处理后的文件移动到目标文件夹
- 图形界面操作
- 系统托盘支持
- 开机自启动选项
- 详细的日志记录

## 安装要求

- Windows 7 或更高版本
- Python 3.6+
- Inno Setup 6（用于生成安装程序）

## 安装步骤

1. 安装必要软件：
   - 安装 [Python](https://www.python.org/downloads/)（3.6或更高版本）
   - 安装 [Inno Setup 6](https://jrsoftware.org/isdl.php)

2. 克隆仓库：
   ```bash
   git clone https://github.com/skhappy/Tibasepath.git
   cd Tibasepath
   ```

3. 安装依赖：
   ```bash
   install_dependencies.bat
   ```

4. 构建程序：
   ```bash
   build.bat
   ```

5. 生成安装程序：
   - 运行 Inno Setup Compiler
   - 打开 Tibasepath.iss
   - 点击 "Build" 生成安装程序

## 使用说明

1. 安装程序后首次运行：
   - 设置源文件夹（需要监控的文件夹）
   - 设置目标文件夹（处理后文件的存放位置）
   - 点击"保存设置"开始监控

2. 程序会自动：
   - 监控源文件夹中的 .utf8 文件
   - 处理文件内容
   - 将处理后的文件移动到目标文件夹

3. 系统托盘功能：
   - 右键点击托盘图标可以显示/隐藏主窗口
   - 可以设置开机自启动

## 日志

程序运行日志存储在 Logs 文件夹中，按日期命名。

## 许可证

[MIT License](LICENSE)
