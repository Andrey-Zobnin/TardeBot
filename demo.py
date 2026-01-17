#!/usr/bin/env python3
"""
Демонстрационный скрипт для показа работы TardeBot
"""

import sys
import os
from loguru import logger

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.config import Config
from data.stock_data import StockDataProvider
from models.price_predictor import PricePredictor


def demo_data_fetching():
    """Демонстрация получения данных"""
    logger.info("=== ДЕМОНСТРАЦИЯ ПОЛУЧЕНИЯ ДАННЫХ ===")
    
    config = Config()
    provider = StockDataProvider(config)
    
    symbol = "AAPL"
    
    # Получаем текущую цену
    current_price = provider.get_current_price(symbol)
    if current_price:
        logger.info(f"Текущая цена {symbol}: ${current_price:.2f}")
    
    # Получаем предыдущую цену
    previous_price = provider.get_previous_price(symbol)
    if previous_price:
        logger.info(f"Предыдущая цена {symbol}: ${previous_price:.2f}")
    
    # Получаем исторические данные
    historical_data = provider.get_historical_data(symbol, period="1mo")
    if historical_data is not None:
        logger.info(f"Получено {len(historical_data)} записей исторических данных")
        logger.info(f"Диапазон дат: {historical_data.index[0]} - {historical_data.index[-1]}")


def demo_model_training():
    """Демонстрация обучения модели"""
    logger.info("=== ДЕМОНСТРАЦИЯ ОБУЧЕНИЯ МОДЕЛИ ===")
    
    config = Config()
    provider = StockDataProvider(config)
    predictor = PricePredictor(config)
    
    symbol = "AAPL"
    
    # Получаем данные для обучения
    training_data = provider.get_historical_data(symbol, period="6mo")
    
    if training_data is not None and not training_data.empty:
        logger.info(f"Данные для обучения: {len(training_data)} записей")
        
        # Обучаем модель
        success = predictor.train_model(training_data)
        
        if success:
            logger.info("Модель успешно обучена!")
            
            # Делаем предсказание
            recent_data = provider.get_historical_data(symbol, period="1mo")
            if recent_data is not None:
                predicted_price = predictor.predict_price(recent_data)
                if predicted_price:
                    current_price = provider.get_current_price(symbol)
                    if current_price:
                        change_percent = (predicted_price - current_price) / current_price * 100
                        logger.info(f"Предсказанная цена: ${predicted_price:.2f}")
                        logger.info(f"Ожидаемое изменение: {change_percent:.2f}%")
        else:
            logger.error("Не удалось обучить модель")
    else:
        logger.error("Не удалось получить данные для обучения")


def main():
    """Главная функция демонстрации"""
    logger.info("Запуск демонстрации TardeBot")
    
    try:
        # Демонстрация получения данных
        demo_data_fetching()
        
        print("\n" + "="*50 + "\n")
        
        # Демонстрация обучения модели
        demo_model_training()
        
        logger.info("Демонстрация завершена")
        
    except Exception as e:
        logger.error(f"Ошибка в демонстрации: {e}")


if __name__ == "__main__":
    main()