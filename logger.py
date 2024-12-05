import os
import logging
from logging.handlers import RotatingFileHandler
import time

def setup_logger():
    """设置日志记录器"""
    try:
        # 创建logs目录（如果不存在）
        if not os.path.exists('Logs'):
            os.makedirs('Logs')
        
        # 生成日志文件名（使用当前日期）
        log_file = os.path.join('Logs', f'tibasepath_{time.strftime("%Y%m%d")}.log')
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建文件处理器（限制单个文件大小为5MB，最多保留5个备份）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        root_logger.handlers.clear()
        
        # 添加处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logging.info('日志系统初始化完成')
        
    except Exception as e:
        print(f"设置日志系统时出错: {str(e)}")
        # 如果设置失败，至少确保基本的控制台日志功能
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        ) 