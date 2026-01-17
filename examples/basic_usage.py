#!/usr/bin/env python3
"""
Примеры базового использования TardeBot
"""

import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import Config
from data.stock_data import StockDataProvider
from models.price_predictor import PricePredictor
from loguru import logger


def example_get_stock_data():
    """Пример получения данных о акциях"""
    logger.info("Пример: Получение данных о акциях")
    
    config = Config()
    provider = StockDataProvider(config)
    
    # Получаем данные по Apple
    symbol = "AAPL"
    
    current_price = provider.get_current_price(symbol)
    previous_price = provider.get_previous_price(symbol)
    
    if current_price and previous_price:
        change = current_price - previous_price
        change_percent = (change / previous_price) * 100
        
        logger.info(f"Символ: {symbol}")
        logger.info(f"Текущая цена: ${current_price:.2f}")
        logger.info(f"Предыдущая цена: ${previous_price:.2f}")
        logger.info(f"Изменение: ${change:.2f} ({change_percent:+.2f}%)")


def example_train_and_predict():
    """Пример обучения модели и предсказания"""
    logger.info("Пример: Обучение модели и предсказание")
    
    config = Config()
    provider = StockDataProvider(config)
    predictor = PricePredictor(config)
    
    symbol = "MSFT"
    
    # Получаем исторические данные для обучения
    training_data = provider.get_historical_data(symbol, period="1y")
    
    if training_data is not None and len(training_data) > 100:
        logger.info(f"Обучение модели на {len(training_data)} записях")
        
        # Обучаем модель
        if predictor.train_model(training_data):
            logger.info("Модель успешно обучена!")
            
            # Получаем свежие данные для предсказания
            recent_data = provider.get_historical_data(symbol, period="3mo")
            
            if recent_data is not None:
                predicted_price = predictor.predict_price(recent_data)
                current_price = provider.get_current_price(symbol)
                
                if predicted_price and current_price:
                    expected_return = (predicted_price - current_price) / current_price * 100
                    
                    logger.info(f"Текущая цена {symbol}: ${current_price:.2f}")
                    logger.info(f"Предсказанная цена: ${predicted_price:.2f}")
                    logger.info(f"Ожидаемая доходность: {expected_return:+.2f}%")
                    
                    # Торговая рекомендация
                    if expected_return > 2:
                        logger.info("Рекомендация: ПОКУПАТЬ")
                    elif expected_return < -2:
                        logger.info("Рекомендация: ПРОДАВАТЬ")
                    else:
                        logger.info("Рекомендация: ДЕРЖАТЬ")
        else:
            logger.error("Не удалось обучить модель")
    else:
        logger.error("Недостаточно данных для обучения")


def example_multiple_stocks():
    """Пример анализа нескольких акций"""
    logger.info("Пример: Анализ нескольких акций")
    
    config = Config()
    provider = StockDataProvider(config)
    
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    
    logger.info("Текущие цены:")
    for symbol in symbols:
        current_price = provider.get_current_price(symbol)
        if current_price:
            logger.info(f"{symbol}: ${current_price:.2f}")


if __name__ == "__main__":
    logger.info("Запуск примеров использования TardeBot")
    
    try:
        example_get_stock_data()
        print("\n" + "="*50 + "\n")
        
        example_train_and_predict()
        print("\n" + "="*50 + "\n")
        
        example_multiple_stocks()
        
        logger.info("Все примеры выполнены")
        
    except Exception as e:
        logger.error(f"Ошибка в примерах: {e}")