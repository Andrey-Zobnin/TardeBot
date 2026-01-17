"""
Модуль для работы с конфигурацией бота
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Класс для управления конфигурацией приложения"""
    
    def __init__(self):
        """Инициализация конфигурации"""
        load_dotenv()
        self._config = self._load_default_config()
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Загрузка конфигурации по умолчанию"""
        return {
            # API ключи
            'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
            
            # Настройки торговли
            'DEFAULT_SYMBOL': os.getenv('DEFAULT_SYMBOL', 'AAPL'),
            'INITIAL_BALANCE': float(os.getenv('INITIAL_BALANCE', '10000')),
            'MAX_POSITION_SIZE': float(os.getenv('MAX_POSITION_SIZE', '0.1')),
            
            # Настройки модели
            'PREDICTION_WINDOW': int(os.getenv('PREDICTION_WINDOW', '30')),
            'TRAINING_PERIOD': int(os.getenv('TRAINING_PERIOD', '252')),
            
            # Настройки логирования
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'logs/trading_bot.log'),
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение конфигурации"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Установить значение конфигурации"""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Получить всю конфигурацию"""
        return self._config.copy()