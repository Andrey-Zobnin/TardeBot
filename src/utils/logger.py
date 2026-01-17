"""
Модуль для настройки логирования
"""

import os
from loguru import logger
from typing import Optional


def setup_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week"
) -> None:
    """
    Настройка логгера для приложения
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_file: Путь к файлу логов (если None, логи только в консоль)
        rotation: Размер файла для ротации
        retention: Время хранения старых логов
    """
    
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Добавляем консольный обработчик
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # Добавляем файловый обработчик, если указан путь
    if log_file:
        # Создаем директорию для логов, если её нет
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        logger.add(
            sink=log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=rotation,
            retention=retention,
            compression="zip"
        )
        
        logger.info(f"Логирование настроено. Файл: {log_file}")
    else:
        logger.info("Логирование настроено (только консоль)")


def get_logger(name: str):
    """
    Получить логгер с указанным именем
    
    Args:
        name: Имя логгера
        
    Returns:
        Настроенный логгер
    """
    return logger.bind(name=name)