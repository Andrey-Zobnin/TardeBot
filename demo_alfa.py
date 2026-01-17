#!/usr/bin/env python3
"""
Демонстрационный скрипт для работы с Альфа-Инвестициями
"""

import sys
import os
from loguru import logger

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.config import Config
from brokers.alfa_broker import AlfaBroker


def demo_alfa_connection():
    """Демонстрация подключения к Альфа-Инвестициям"""
    logger.info("=== ДЕМОНСТРАЦИЯ ПОДКЛЮЧЕНИЯ К АЛЬФА-ИНВЕСТИЦИЯМ ===")
    
    config = Config()
    broker = AlfaBroker(config)
    
    # Проверяем подключение
    account_info = broker.get_account_info()
    if account_info:
        logger.info(f"✅ Подключение успешно!")
        logger.info(f"Аккаунт: {account_info.get('name', 'N/A')}")
        logger.info(f"ID: {account_info.get('id', 'N/A')}")
    else:
        logger.error("❌ Не удалось подключиться к Альфа-Инвестициям")
        logger.error("Проверьте токен и ID аккаунта в .env файле")
        return False
    
    return True


def demo_portfolio():
    """Демонстрация получения портфеля"""
    logger.info("=== ДЕМОНСТРАЦИЯ ПОРТФЕЛЯ ===")
    
    config = Config()
    broker = AlfaBroker(config)
    
    # Получаем портфель
    portfolio = broker.get_portfolio()
    if portfolio:
        positions = portfolio.get('positions', [])
        logger.info(f"Позиций в портфеле: {len(positions)}")
        
        for position in positions[:5]:  # Показываем первые 5 позиций
            ticker = position.get('ticker', 'N/A')
            balance = position.get('balance', 0)
            instrument_type = position.get('instrument_type', 'N/A')
            
            logger.info(f"  {ticker}: {balance} ({instrument_type})")
    
    # Получаем баланс
    balance = broker.get_balance()
    if balance:
        logger.info(f"Денежный баланс: {balance:,.2f} RUB")


def demo_market_data():
    """Демонстрация получения рыночных данных"""
    logger.info("=== ДЕМОНСТРАЦИЯ РЫНОЧНЫХ ДАННЫХ ===")
    
    config = Config()
    broker = AlfaBroker(config)
    
    # Тестируем на популярных российских акциях
    symbols = ['SBER', 'GAZP', 'LKOH', 'YNDX', 'TCSG']
    
    logger.info("Текущие цены:")
    for symbol in symbols:
        price = broker.get_current_price(symbol)
        if price:
            logger.info(f"  {symbol}: {price:.2f} RUB")
        else:
            logger.warning(f"  {symbol}: цена недоступна")


def demo_historical_data():
    """Демонстрация получения исторических данных"""
    logger.info("=== ДЕМОНСТРАЦИЯ ИСТОРИЧЕСКИХ ДАННЫХ ===")
    
    config = Config()
    broker = AlfaBroker(config)
    
    symbol = config.get('DEFAULT_SYMBOL', 'SBER')
    
    # Получаем свечи за последние 30 дней
    candles = broker.get_candles(symbol, interval='1day', days=30)
    
    if candles:
        logger.info(f"Получено {len(candles)} свечей для {symbol}")
        
        # Показываем последние 3 свечи
        logger.info("Последние 3 дня:")
        for candle in candles[-3:]:
            date = candle.get('time', 'N/A')[:10]  # Только дата
            open_price = float(candle.get('open', 0))
            close_price = float(candle.get('close', 0))
            volume = int(candle.get('volume', 0))
            
            change = ((close_price - open_price) / open_price * 100) if open_price > 0 else 0
            
            logger.info(f"  {date}: {open_price:.2f} → {close_price:.2f} "
                       f"({change:+.2f}%), объем: {volume:,}")
    else:
        logger.warning(f"Не удалось получить исторические данные для {symbol}")


def demo_search_instruments():
    """Демонстрация поиска инструментов"""
    logger.info("=== ДЕМОНСТРАЦИЯ ПОИСКА ИНСТРУМЕНТОВ ===")
    
    config = Config()
    broker = AlfaBroker(config)
    
    # Поиск по разным запросам
    queries = ['Сбербанк', 'Газпром', 'Яндекс']
    
    for query in queries:
        logger.info(f"Поиск: '{query}'")
        instruments = broker.search_instrument(query)
        
        if instruments:
            for instrument in instruments[:3]:  # Показываем первые 3 результата
                name = instrument.get('name', 'N/A')
                ticker = instrument.get('ticker', 'N/A')
                figi = instrument.get('figi', 'N/A')
                
                logger.info(f"  {ticker} - {name} (FIGI: {figi})")
        else:
            logger.warning(f"  Ничего не найдено для '{query}'")
        
        print()  # Пустая строка для разделения


def main():
    """Главная функция демонстрации"""
    logger.info("Запуск демонстрации Альфа-Инвестиций")
    
    try:
        # Проверяем подключение
        if not demo_alfa_connection():
            return
        
        print("\n" + "="*60 + "\n")
        
        # Демонстрация портфеля
        demo_portfolio()
        
        print("\n" + "="*60 + "\n")
        
        # Демонстрация рыночных данных
        demo_market_data()
        
        print("\n" + "="*60 + "\n")
        
        # Демонстрация исторических данных
        demo_historical_data()
        
        print("\n" + "="*60 + "\n")
        
        # Демонстрация поиска инструментов
        demo_search_instruments()
        
        logger.info("Демонстрация завершена успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка в демонстрации: {e}")
        logger.error("Убедитесь, что:")
        logger.error("1. Создан файл .env с правильными токенами")
        logger.error("2. Токен Альфа-Инвестиций действителен")
        logger.error("3. ID аккаунта указан корректно")


if __name__ == "__main__":
    main()