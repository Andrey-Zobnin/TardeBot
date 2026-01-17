#!/usr/bin/env python3
"""
TardeBot - Главный модуль алгоритмического трейдинг-бота
"""

import sys
import os
from loguru import logger

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.stock_data import StockDataProvider
from models.price_predictor import PricePredictor
from trading.bot import TradingBot
from utils.config import Config


def main():
    """Главная функция запуска бота"""
    logger.info("Запуск TardeBot...")
    
    try:
        # Загружаем конфигурацию
        config = Config()
        logger.info("Конфигурация загружена")
        
        # Инициализируем компоненты
        data_provider = StockDataProvider(config)
        predictor = PricePredictor(config)
        bot = TradingBot(data_provider, predictor, config)
        
        logger.info("Все компоненты инициализированы")
        
        # Запускаем бота
        bot.run()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()