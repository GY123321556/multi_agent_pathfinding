"""
日志记录模块
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str, level=logging.INFO):
    """设置日志记录器"""

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 创建文件处理器
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_handler = logging.FileHandler(f"mapf_{timestamp}.log")
    file_handler.setLevel(level)

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 添加格式化器到处理器
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加处理器到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger