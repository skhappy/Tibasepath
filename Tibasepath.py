import os
import time
import shutil
import logging
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser
import threading
from logger import setup_logger
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QFileDialog, QMessageBox, QFrame,
                            QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QFont

class FileHandler(FileSystemEventHandler):
    def __init__(self, source_path, target_path):
        self.source_path = source_path
        self.target_path = target_path
        self.processed_files = set()  # 用于记录已处理的文件
        self.processing_files = set()  # 用于记录正在处理的文件
        self.last_event_time = {}  # 用于记录文件最后一次事件时间
        self.stats = {
            'total_processed': 0,
            'modified': 0,
            'moved': 0,
            'errors': 0
        }

    def get_stats(self):
        """获取统计信息"""
        return (
            f"总处理: {self.stats['total_processed']} | "
            f"已修改: {self.stats['modified']} | "
            f"已移动: {self.stats['moved']} | "
            f"错误: {self.stats['errors']}"
        )

    def clear_records(self):
        """清理所有记录"""
        self.processed_files.clear()
        self.processing_files.clear()
        self.last_event_time.clear()

    def on_modified(self, event):
        try:
            current_time = time.time()
            file_path = event.src_path
            
            # 忽略非文件事件
            if event.is_directory:
                return
                
            # 忽略临时文件
            if file_path.endswith('.tmp'):
                return
                
            # 只处理.utf8文件
            if not file_path.lower().endswith('.utf8'):
                return
                
            # 检查事件时间间隔（防止重复触发）
            last_time = self.last_event_time.get(file_path, 0)
            if current_time - last_time < 1.0:  # 1秒内的重复事件将被忽略
                return
                
            self.last_event_time[file_path] = current_time
            
            # 标记文件正在处理
            self.processing_files.add(file_path)
            
            try:
                # 等待文件写入完成
                time.sleep(0.5)
                
                if os.path.exists(file_path):
                    logging.debug(f"开始处理文件: {file_path}")
                    if self.process_file(file_path):
                        self.processed_files.add(file_path)
                        logging.info(f"文件处理成功: {file_path}")
                else:
                    logging.debug(f"文件不存在，可能已被处理: {file_path}")
            finally:
                # 处理完成后移除标记
                self.processing_files.discard(file_path)
                
        except Exception as e:
            logging.error(f"处理文件事件时出错: {str(e)}", exc_info=True)

    def process_file(self, file_path):
        try:
            logging.debug(f"开始处理文件: {file_path}")
            
            # 检查文件是否存在和可访问
            if not os.path.exists(file_path):
                logging.debug(f"文件不存在，可能已被处理: {file_path}")
                return False
            
            # 检查目标目录
            if not os.path.exists(self.target_path):
                os.makedirs(self.target_path)
                logging.info(f"创建目标目录: {self.target_path}")
            
            # 读取文件内容
            content = None
            lines = None
            modified = False
            
            # 读取源文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.splitlines()
                    logging.debug(f"成功读取文件，行数: {len(lines)}")
                    
                    # 在同一个文件句柄中检查和修改内容
                    if len(lines) >= 7:
                        line7 = lines[6]
                        logging.debug(f"第7行内容: [{line7.strip()}]")
                        
                        if '6' in line7 and not '6.' in line7:
                            old_content = line7
                            lines[6] = line7.replace('6', '6.')
                            logging.info(f"修改第7行: [{old_content.strip()}] -> [{lines[6].strip()}]")
                            modified = True
                            content = '\n'.join(lines)  # 更新content
            except Exception as e:
                logging.error(f"读取文件失败: {str(e)}")
                return False
            finally:
                # 强制进行垃圾回
                import gc
                gc.collect()
            
            # 目标文件路径
            target_file = os.path.join(self.target_path, os.path.basename(file_path))
            
            try:
                # 写入新文件而不是修改原文件
                temp_file = target_file + '.tmp'
                
                # 写入临时文件
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    f.flush()
                    os.fsync(f.fileno())
                
                # 如果目标文件已存在，先删除
                if os.path.exists(target_file):
                    os.remove(target_file)
                
                # 重命名临时文件
                os.rename(temp_file, target_file)
                
                # 等待文件系统操作完成
                time.sleep(0.5)
                
                # 删除源文件
                try:
                    os.chmod(file_path, 0o777)  # 确保有删除权限
                    os.remove(file_path)
                    logging.debug(f"成功删除源文件: {file_path}")
                except Exception as e:
                    logging.error(f"删除源文件失败: {str(e)}")
                    # 继续处理，不影响果
                
                if modified:
                    self.stats['modified'] += 1
                    logging.info(f"文件已修改并移动: {file_path} -> {target_file}")
                else:
                    logging.info(f"文件已直接移动: {file_path} -> {target_file}")
                
                self.stats['moved'] += 1
                self.stats['total_processed'] += 1
                return True
                
            except Exception as e:
                self.stats['errors'] += 1
                logging.error(f"处理文件失败: {str(e)}")
                # 清理临时文件
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                return False
                
        except Exception as e:
            self.stats['errors'] += 1
            logging.error(f"处理文件时出错: {str(e)}", exc_info=True)
            return False

class TibasepathGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        # 初始化日志
        setup_logger()
        logging.info("程序启动")
        
        # 检查是否是开机启动
        self.is_startup = self.check_startup_launch()
        
        self.config = configparser.ConfigParser()
        config_valid = self.load_config()
        
        # 设置窗口
        self.setWindowTitle("Tibasepath")
        self.setWindowIcon(QIcon('metrohm.ico'))
        
        # 创建事件处理器和观察者
        self.event_handler = None
        self.observer = Observer()
        self.observer.daemon = True
        
        # 设置GUI
        self.setup_gui()
        
        # 创建系统托盘
        self.setup_tray()
        
        # 开始监控（如果配置有效）
        if config_valid:
            self.start_monitoring()
        else:
            logging.warning("请在设置中配置有效的源文件夹和目标文件夹")
            self.status_label.setText("请配置目录")
            self.status_label.setStyleSheet("color: orange")
        
        # 开始定期更新日志显示
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_log_display)
        self.update_timer.start(1000)  # 每秒更新一次
        
        # 如果是开机启动，自动最小化到托盘
        if self.is_startup:
            QTimer.singleShot(1000, self.minimize_to_tray)  # 延迟1秒后最小化

    def check_startup_launch(self):
        """检查是否是开机启动"""
        try:
            import sys
            import winreg
            
            # 获取注册表中的启动项
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, "Tibasepath")
                # 检查当前程序路径是否与注册表中的路径匹配
                if sys.executable in value:
                    logging.info("程序通过开机启动项启动")
                    return True
            except WindowsError:
                pass
            finally:
                winreg.CloseKey(key)
            
            # 检查启动文件夹
            import os
            startup_path = os.path.join(
                os.environ["PROGRAMDATA"],
                r"Microsoft\Windows\Start Menu\Programs\StartUp"
            )
            startup_link = os.path.join(startup_path, "Tibasepath.lnk")
            
            if os.path.exists(startup_link):
                logging.info("程序通过启动文件夹启动")
                return True
                
        except Exception as e:
            logging.error(f"检查开机启动状态时出错: {str(e)}")
        
        return False

    def minimize_to_tray(self):
        """最小化到托盘"""
        if hasattr(self, 'has_tray_support') and self.has_tray_support:
            self.hide()  # 隐藏主窗口
            self.is_minimized = True
            if self.is_startup:
                self.tray_icon.showMessage(
                    "Tibasepath",
                    "程序已在后台运行",
                    QSystemTrayIcon.Information,
                    2000
                )
        else:
            self.showMinimized()  # 如果没有托盘支持，就只是最小化窗口

    def setup_gui(self):
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 设置区域
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        settings_layout = QVBoxLayout(settings_frame)
        
        # 源文件夹设置
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("源文件夹:"))
        self.source_entry = QLineEdit()
        self.source_entry.setText(self.config['Paths'].get('source', ''))
        source_layout.addWidget(self.source_entry)
        browse_source_btn = QPushButton("浏览")
        browse_source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(browse_source_btn)
        settings_layout.addLayout(source_layout)
        
        # 目标文件夹设置
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标文件夹:"))
        self.target_entry = QLineEdit()
        self.target_entry.setText(self.config['Paths'].get('target', ''))
        target_layout.addWidget(self.target_entry)
        browse_target_btn = QPushButton("浏览")
        browse_target_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(browse_target_btn)
        settings_layout.addLayout(target_layout)
        
        # 保存设置按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                padding: 5px 15px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005999;
            }
        """)
        settings_layout.addWidget(save_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(settings_frame)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                padding: 5px;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        clear_log_btn = QPushButton("清除日志")
        clear_log_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_log_btn)
        
        minimize_btn = QPushButton("最小化到托盘")
        minimize_btn.clicked.connect(self.hide)
        button_layout.addWidget(minimize_btn)
        layout.addLayout(button_layout)
        
        # 状态栏
        status_bar = self.statusBar()
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        self.stats_label = QLabel("")
        status_bar.addPermanentWidget(self.stats_label)
        
        # 设置窗口大小和位置
        self.resize(800, 600)
        self.center()

    def center(self):
        # 将窗口移动到屏幕中央
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_tray(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(QIcon('metrohm.ico'), self)
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def load_config(self):
        try:
            if os.path.exists('tibasepath.conf'):
                self.config.read('tibasepath.conf', encoding='utf-8')
                # 验证配置的有效性
                source_path = self.config['Paths'].get('source', '')
                target_path = self.config['Paths'].get('target', '')
                
                # 检查路径是否存在
                if source_path and target_path and \
                   os.path.exists(source_path) and os.path.exists(target_path):
                    return True
                else:
                    logging.warning("配置文件中的路径无效或不存在")
            else:
                logging.info("配置文件不存在，使用默认配置")
                
            # 如果配置无效或不存在，使用默认配置
            self.config['Paths'] = {
                'source': '',
                'target': ''
            }
            return False
        except Exception as e:
            logging.error(f"加载配置文件失败: {str(e)}")
            self.config['Paths'] = {
                'source': '',
                'target': ''
            }
            return False

    def browse_source(self):
        folder = QFileDialog.getExistingDirectory(self, "选择源文件夹")
        if folder:
            self.source_entry.setText(folder)

    def browse_target(self):
        folder = QFileDialog.getExistingDirectory(self, "选择目标文件夹")
        if folder:
            self.target_entry.setText(folder)

    def save_settings(self):
        source_path = self.source_entry.text()
        target_path = self.target_entry.text()
        
        # 验证路径
        if not source_path or not target_path:
            QMessageBox.critical(self, "错误", "请设置源文件夹和目标文件夹")
            return False
        
        if not os.path.exists(source_path):
            QMessageBox.critical(self, "错误", f"源文件夹不存在: {source_path}")
            return False
        
        if not os.path.exists(target_path):
            QMessageBox.critical(self, "错误", f"目标文件夹不存在: {target_path}")
            return False
        
        try:
            # 保存配置
            self.config['Paths'] = {
                'source': source_path,
                'target': target_path
            }
            with open('tibasepath.conf', 'w', encoding='utf-8') as f:
                self.config.write(f)
            
            # 重启监控
            self.restart_monitoring()
            QMessageBox.information(self, "成功", "设置已保存，监控��启动")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败: {str(e)}")
            logging.error(f"保存设置失败: {str(e)}")
            return False

    def start_monitoring(self):
        source_path = self.config['Paths'].get('source', '')
        target_path = self.config['Paths'].get('target', '')
        
        logging.info(f"开始监控 - 源目录: {source_path}")
        logging.info(f"开始监控 - 目标目录: {target_path}")
        
        if not source_path or not target_path:
            logging.warning("源目录或目标目录未设置，请在设置中配置目录")
            self.status_label.setText("未设置目录")
            self.status_label.setStyleSheet("color: orange")
            return
        
        try:
            # 如果没有事件处理器，创建一个
            if not self.event_handler:
                self.event_handler = FileHandler(source_path, target_path)
            
            # 停止现有的监控
            if self.observer.is_alive():
                self.observer.unschedule_all()
            
            # 启动新的监控
            self.observer.schedule(self.event_handler, source_path, recursive=False)
            if not self.observer.is_alive():
                self.observer.start()
            logging.info("文件监控已启动")
            self.status_label.setText("监控中")
            self.status_label.setStyleSheet("color: green")
            
            # 更新统计信息
            if hasattr(self.event_handler, 'get_stats'):
                self.stats_label.setText(self.event_handler.get_stats())
                
        except Exception as e:
            logging.error(f"启动监控失败: {str(e)}", exc_info=True)
            self.status_label.setText("启动失败")
            self.status_label.setStyleSheet("color: red")

    def restart_monitoring(self):
        try:
            # 取消所有现有的监控
            self.observer.unschedule_all()
            # 重新开始监控
            self.start_monitoring()
        except Exception as e:
            logging.error(f"重启监控失败: {str(e)}", exc_info=True)

    def clear_log(self):
        try:
            # 清空GUI显示
            self.log_text.clear()
            
            # 清空日志文件
            log_file = os.path.join("Logs", f"tibasepath_{time.strftime('%Y%m%d')}.log")
            if os.path.exists(log_file):
                # 备份旧日志
                backup_file = log_file + '.bak'
                try:
                    if os.path.exists(backup_file):
                        os.remove(backup_file)
                    os.rename(log_file, backup_file)
                except Exception as e:
                    logging.error(f"备份日志文件失败: {str(e)}")
                
                # 创建新的日志文件
                try:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write(f"=== 日志已清空 ({time.strftime('%Y-%m-%d %H:%M:%S')}) ===\n")
                    logging.info("日志已清空")
                except Exception as e:
                    logging.error(f"创建新日志文件失败: {str(e)}")
                    if os.path.exists(backup_file):
                        os.rename(backup_file, log_file)
            
            # 重新初始化日志系统
            setup_logger()
            logging.info("日志系统已重新初始化")
            
            # 显示成功消息
            QMessageBox.information(self, "成功", "日志已清空")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清空日志失败: {str(e)}")
            logging.error(f"清空日志失败: {str(e)}")

    def update_log_display(self):
        try:
            # 更新日志显示
            log_file = os.path.join("Logs", f"tibasepath_{time.strftime('%Y%m%d')}.log")
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 只保留最后的50行
                    lines = content.split('\n')
                    if len(lines) > 50:
                        content = '\n'.join(lines[-50:])
                    self.log_text.setText(content)
                    # 滚动到底部
                    self.log_text.verticalScrollBar().setValue(
                        self.log_text.verticalScrollBar().maximum()
                    )
            
            # 更新状态和统计信息
            if self.observer and self.observer.is_alive():
                if self.event_handler and hasattr(self.event_handler, 'stats'):
                    if self.event_handler.stats['total_processed'] > 0:
                        self.status_label.setText("正在运行")
                        self.status_label.setStyleSheet("color: green")
                    else:
                        self.status_label.setText("监控中")
                        self.status_label.setStyleSheet("color: green")
                    
                    # 更新统计信息
                    self.stats_label.setText(self.event_handler.get_stats())
                    if self.event_handler.stats['errors'] > 0:
                        self.stats_label.setStyleSheet("color: red")
                    else:
                        self.stats_label.setStyleSheet("color: black")
            else:
                self.status_label.setText("已停止")
                self.status_label.setStyleSheet("color: red")
                
        except Exception as e:
            logging.error(f"更新显示时出错: {str(e)}")

    def quit_app(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        QApplication.quit()

    def closeEvent(self, event):
        # 重写关闭事件，改为最小化到托盘
        event.ignore()
        self.hide()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格
    window = TibasepathGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()