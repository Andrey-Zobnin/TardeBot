"""
Основной модуль торгового бота
"""

import time
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime


class TradingBot:
    """Основной класс торгового бота"""
    
    def __init__(self, data_provider, predictor, config):
        """Инициализация бота"""
        self.data_provider = data_provider
        self.predictor = predictor
        self.config = config
        
        # Состояние бота
        self.balance = config.get('INITIAL_BALANCE', 10000.0)
        self.positions = {}  # {symbol: quantity}
        self.trade_history = []
        self.is_running = False
        
        # Настройки торговли
        self.symbol = config.get('DEFAULT_SYMBOL', 'AAPL')
        self.max_position_size = config.get('MAX_POSITION_SIZE', 0.1)
        self.prediction_threshold = 0.02  # 2% минимальное изменение для торговли
        
        logger.info(f"Бот инициализирован. Баланс: ${self.balance}")
    
    def run(self):
        """Запуск основного цикла бота"""
        logger.info("Запуск торгового бота...")
        self.is_running = True
        
        # Сначала обучаем модель
        if not self._train_model():
            logger.error("Не удалось обучить модель. Остановка бота.")
            return
        
        # Основной торговый цикл
        while self.is_running:
            try:
                self._trading_cycle()
                time.sleep(60)  # Пауза между циклами (1 минута)
                
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки")
                self.stop()
            except Exception as e:
                logger.error(f"Ошибка в торговом цикле: {e}")
                time.sleep(30)  # Пауза при ошибке
    
    def _train_model(self) -> bool:
        """Обучение модели предсказания"""
        logger.info("Обучение модели...")
        
        # Получаем исторические данные
        historical_data = self.data_provider.get_historical_data(
            self.symbol, 
            period="1y"
        )
        
        if historical_data is None or historical_data.empty:
            logger.error("Не удалось получить исторические данные")
            return False
        
        # Обучаем модель
        return self.predictor.train_model(historical_data)
    
    def _trading_cycle(self):
        """Один цикл торговли"""
        logger.info(f"--- Торговый цикл {datetime.now().strftime('%H:%M:%S')} ---")
        
        # Получаем текущие данные
        current_price = self.data_provider.get_current_price(self.symbol)
        previous_price = self.data_provider.get_previous_price(self.symbol)
        
        if current_price is None or previous_price is None:
            logger.warning("Не удалось получить данные о ценах")
            return
        
        # Получаем исторические данные для предсказания
        recent_data = self.data_provider.get_historical_data(
            self.symbol, 
            period="3mo"
        )
        
        if recent_data is None or recent_data.empty:
            logger.warning("Не удалось получить данные для предсказания")
            return
        
        # Делаем предсказание
        predicted_price = self.predictor.predict_price(recent_data)
        
        if predicted_price is None:
            logger.warning("Не удалось получить предсказание цены")
            return
        
        # Принимаем торговое решение
        self._make_trading_decision(current_price, predicted_price)
        
        # Выводим статус
        self._print_status(current_price, previous_price, predicted_price)
    
    def _make_trading_decision(self, current_price: float, predicted_price: float):
        """Принятие торгового решения"""
        price_change_percent = (predicted_price - current_price) / current_price
        
        logger.info(f"Ожидаемое изменение цены: {price_change_percent:.2%}")
        
        # Решение о покупке
        if price_change_percent > self.prediction_threshold:
            self._buy_signal(current_price, price_change_percent)
        
        # Решение о продаже
        elif price_change_percent < -self.prediction_threshold:
            self._sell_signal(current_price, price_change_percent)
        
        else:
            logger.info("Удерживаем позицию (изменение цены незначительно)")
    
    def _buy_signal(self, current_price: float, expected_change: float):
        """Обработка сигнала на покупку"""
        if self.symbol in self.positions and self.positions[self.symbol] > 0:
            logger.info("Уже есть позиция по этому символу")
            return
        
        # Рассчитываем размер позиции
        max_investment = self.balance * self.max_position_size
        quantity = int(max_investment / current_price)
        
        if quantity > 0 and self.balance >= quantity * current_price:
            cost = quantity * current_price
            self.balance -= cost
            self.positions[self.symbol] = self.positions.get(self.symbol, 0) + quantity
            
            trade = {
                'timestamp': datetime.now(),
                'action': 'BUY',
                'symbol': self.symbol,
                'quantity': quantity,
                'price': current_price,
                'cost': cost,
                'expected_change': expected_change
            }
            
            self.trade_history.append(trade)
            logger.info(f"ПОКУПКА: {quantity} акций {self.symbol} по ${current_price:.2f}")
        else:
            logger.warning("Недостаточно средств для покупки")
    
    def _sell_signal(self, current_price: float, expected_change: float):
        """Обработка сигнала на продажу"""
        if self.symbol not in self.positions or self.positions[self.symbol] <= 0:
            logger.info("Нет позиции для продажи")
            return
        
        quantity = self.positions[self.symbol]
        revenue = quantity * current_price
        self.balance += revenue
        self.positions[self.symbol] = 0
        
        trade = {
            'timestamp': datetime.now(),
            'action': 'SELL',
            'symbol': self.symbol,
            'quantity': quantity,
            'price': current_price,
            'revenue': revenue,
            'expected_change': expected_change
        }
        
        self.trade_history.append(trade)
        logger.info(f"ПРОДАЖА: {quantity} акций {self.symbol} по ${current_price:.2f}")
    
    def _print_status(self, current_price: float, previous_price: float, predicted_price: float):
        """Вывод текущего статуса"""
        position_value = self.positions.get(self.symbol, 0) * current_price
        total_value = self.balance + position_value
        
        logger.info(f"Баланс: ${self.balance:.2f}")
        logger.info(f"Позиция: {self.positions.get(self.symbol, 0)} акций (${position_value:.2f})")
        logger.info(f"Общая стоимость: ${total_value:.2f}")
        logger.info(f"Текущая цена: ${current_price:.2f}")
        logger.info(f"Предсказанная цена: ${predicted_price:.2f}")
    
    def stop(self):
        """Остановка бота"""
        logger.info("Остановка торгового бота...")
        self.is_running = False
        
        # Выводим финальную статистику
        self._print_final_stats()
    
    def _print_final_stats(self):
        """Вывод финальной статистики"""
        logger.info("=== ФИНАЛЬНАЯ СТАТИСТИКА ===")
        logger.info(f"Всего сделок: {len(self.trade_history)}")
        logger.info(f"Финальный баланс: ${self.balance:.2f}")
        
        if self.trade_history:
            logger.info("Последние сделки:")
            for trade in self.trade_history[-5:]:
                logger.info(f"{trade['timestamp'].strftime('%H:%M:%S')} - "
                          f"{trade['action']} {trade['quantity']} {trade['symbol']} "
                          f"по ${trade['price']:.2f}")