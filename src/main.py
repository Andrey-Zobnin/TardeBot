#!/usr/bin/env python3
"""
TardeBot - Главный модуль алгоритмического трейдинг-бота
Поддерживает работу с Альфа-Инвестициями
"""

import sys
import os
from loguru import logger

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.stock_data import StockDataProvider
from models.price_predictor import PricePredictor
from trading.bot import TradingBot
from trading.alfa_trading_bot import AlfaTradingBot
from utils.config import Config
from utils.logger import setup_logger


def main():
    """Главная функция запуска бота"""
    # Загружаем конфигурацию
    config = Config()
    
    # Настраиваем логирование
    setup_logger(
        log_level=config.get('LOG_LEVEL', 'INFO'),
        log_file=config.get('LOG_FILE')
    )
    
    logger.info("Запуск TardeBot...")
    
    try:
        # Инициализируем компоненты
        data_provider = StockDataProvider(config)
        predictor = PricePredictor(config)
        
        # Выбираем тип бота в зависимости от конфигурации
        use_alfa_broker = config.get('USE_ALFA_BROKER', False)
        
        if use_alfa_broker:
            logger.info("Запуск с интеграцией Альфа-Инвестиций")
            bot = AlfaTradingBot(data_provider, predictor, config)
        else:
            logger.info("Запуск в демонстрационном режиме")
            bot = TradingBot(data_provider, predictor, config)
        
        logger.info("Все компоненты инициализированы")
        
        # Запускаем бота
        bot.run()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()