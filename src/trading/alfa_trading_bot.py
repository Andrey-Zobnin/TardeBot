"""
Торговый бот с интеграцией Альфа-Инвестиций
"""

import time
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

from ..brokers.alfa_broker import AlfaBroker


class AlfaTradingBot:
    """Торговый бот для работы с Альфа-Инвестициями"""
    
    def __init__(self, data_provider, predictor, config):
        """Инициализация бота"""
        self.data_provider = data_provider
        self.predictor = predictor
        self.config = config
        
        # Инициализация брокера
        self.broker = AlfaBroker(config)
        
        # Состояние бота
        self.initial_balance = config.get('INITIAL_BALANCE', 100000.0)
        self.positions = {}  # {ticker: quantity}
        self.trade_history = []
        self.is_running = False
        
        # Настройки торговли
        self.symbol = config.get('DEFAULT_SYMBOL', 'SBER')
        self.max_position_size = config.get('MAX_POSITION_SIZE', 0.1)
        self.prediction_threshold = 0.02  # 2% минимальное изменение для торговли
        
        logger.info(f"Альфа-Бот инициализирован для торговли {self.symbol}")
    
    def run(self):
        """Запуск основного цикла бота"""
        logger.info("Запуск Альфа торгового бота...")
        
        # Проверяем подключение к брокеру
        if not self._check_broker_connection():
            logger.error("Не удалось подключиться к брокеру. Остановка.")
            return
        
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
    
    def _check_broker_connection(self) -> bool:
        """Проверка подключения к брокеру"""
        logger.info("Проверка подключения к Альфа-Инвестициям...")
        
        account_info = self.broker.get_account_info()
        if account_info:
            logger.info(f"Подключение успешно. Аккаунт: {account_info.get('name', 'N/A')}")
            
            # Получаем текущий баланс
            balance = self.broker.get_balance()
            if balance:
                logger.info(f"Текущий баланс: {balance:,.2f} RUB")
            
            return True
        
        logger.error("Не удалось подключиться к брокеру")
        return False
    
    def _train_model(self) -> bool:
        """Обучение модели предсказания"""
        logger.info("Обучение модели на данных из Альфа-Инвестиций...")
        
        # Получаем исторические данные через брокера
        candles = self.broker.get_candles(self.symbol, interval='1day', days=365)
        
        if not candles:
            logger.warning("Не удалось получить данные через брокера, используем альтернативный источник")
            # Fallback на обычный провайдер данных
            historical_data = self.data_provider.get_historical_data(
                self.symbol, 
                period="1y"
            )
        else:
            # Конвертируем данные свечей в формат pandas
            historical_data = self._convert_candles_to_dataframe(candles)
        
        if historical_data is None or historical_data.empty:
            logger.error("Не удалось получить исторические данные")
            return False
        
        # Обучаем модель
        return self.predictor.train_model(historical_data)
    
    def _convert_candles_to_dataframe(self, candles):
        """Конвертация свечей в DataFrame"""
        import pandas as pd
        
        data = []
        for candle in candles:
            data.append({
                'Open': float(candle.get('open', 0)),
                'High': float(candle.get('high', 0)),
                'Low': float(candle.get('low', 0)),
                'Close': float(candle.get('close', 0)),
                'Volume': int(candle.get('volume', 0)),
                'Date': candle.get('time', '')
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        
        return df
    
    def _trading_cycle(self):
        """Один цикл торговли"""
        logger.info(f"--- Альфа торговый цикл {datetime.now().strftime('%H:%M:%S')} ---")
        
        # Получаем текущую цену через брокера
        current_price = self.broker.get_current_price(self.symbol)
        
        if current_price is None:
            logger.warning("Не удалось получить текущую цену")
            return
        
        # Получаем исторические данные для предсказания
        recent_candles = self.broker.get_candles(self.symbol, interval='1day', days=90)
        
        if not recent_candles:
            logger.warning("Не удалось получить данные для предсказания")
            return
        
        recent_data = self._convert_candles_to_dataframe(recent_candles)
        
        # Делаем предсказание
        predicted_price = self.predictor.predict_price(recent_data)
        
        if predicted_price is None:
            logger.warning("Не удалось получить предсказание цены")
            return
        
        # Принимаем торговое решение
        self._make_trading_decision(current_price, predicted_price)
        
        # Выводим статус
        self._print_status(current_price, predicted_price)
    
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
        # Проверяем текущие позиции
        portfolio = self.broker.get_portfolio()
        current_position = 0
        
        if portfolio:
            for position in portfolio.get('positions', []):
                if position.get('ticker') == self.symbol:
                    current_position = int(position.get('balance', 0))
                    break
        
        if current_position > 0:
            logger.info(f"Уже есть позиция: {current_position} акций {self.symbol}")
            return
        
        # Рассчитываем размер позиции
        balance = self.broker.get_balance()
        if not balance:
            logger.warning("Не удалось получить баланс")
            return
        
        max_investment = balance * self.max_position_size
        quantity = int(max_investment / current_price)
        
        if quantity > 0:
            logger.info(f"Попытка покупки {quantity} акций {self.symbol}")
            
            # Размещаем ордер через брокера
            order_result = self.broker.buy_market(self.symbol, quantity)
            
            if order_result:
                trade = {
                    'timestamp': datetime.now(),
                    'action': 'BUY',
                    'symbol': self.symbol,
                    'quantity': quantity,
                    'price': current_price,
                    'expected_change': expected_change,
                    'order_id': order_result.get('order_id')
                }
                
                self.trade_history.append(trade)
                self.positions[self.symbol] = self.positions.get(self.symbol, 0) + quantity
                
                logger.info(f"ПОКУПКА ВЫПОЛНЕНА: {quantity} акций {self.symbol} по ~{current_price:.2f}")
            else:
                logger.error("Не удалось выполнить покупку")
        else:
            logger.warning("Недостаточно средств для покупки")
    
    def _sell_signal(self, current_price: float, expected_change: float):
        """Обработка сигнала на продажу"""
        # Проверяем текущие позиции
        portfolio = self.broker.get_portfolio()
        current_position = 0
        
        if portfolio:
            for position in portfolio.get('positions', []):
                if position.get('ticker') == self.symbol:
                    current_position = int(position.get('balance', 0))
                    break
        
        if current_position <= 0:
            logger.info("Нет позиции для продажи")
            return
        
        logger.info(f"Попытка продажи {current_position} акций {self.symbol}")
        
        # Размещаем ордер на продажу
        order_result = self.broker.sell_market(self.symbol, current_position)
        
        if order_result:
            trade = {
                'timestamp': datetime.now(),
                'action': 'SELL',
                'symbol': self.symbol,
                'quantity': current_position,
                'price': current_price,
                'expected_change': expected_change,
                'order_id': order_result.get('order_id')
            }
            
            self.trade_history.append(trade)
            self.positions[self.symbol] = 0
            
            logger.info(f"ПРОДАЖА ВЫПОЛНЕНА: {current_position} акций {self.symbol} по ~{current_price:.2f}")
        else:
            logger.error("Не удалось выполнить продажу")
    
    def _print_status(self, current_price: float, predicted_price: float):
        """Вывод текущего статуса"""
        balance = self.broker.get_balance()
        portfolio = self.broker.get_portfolio()
        
        position_quantity = 0
        if portfolio:
            for position in portfolio.get('positions', []):
                if position.get('ticker') == self.symbol:
                    position_quantity = int(position.get('balance', 0))
                    break
        
        position_value = position_quantity * current_price
        total_value = (balance or 0) + position_value
        
        logger.info(f"Баланс: {balance:,.2f} RUB" if balance else "Баланс: N/A")
        logger.info(f"Позиция: {position_quantity} акций ({position_value:,.2f} RUB)")
        logger.info(f"Общая стоимость: {total_value:,.2f} RUB")
        logger.info(f"Текущая цена {self.symbol}: {current_price:.2f} RUB")
        logger.info(f"Предсказанная цена: {predicted_price:.2f} RUB")
    
    def stop(self):
        """Остановка бота"""
        logger.info("Остановка Альфа торгового бота...")
        self.is_running = False
        
        # Выводим финальную статистику
        self._print_final_stats()
    
    def _print_final_stats(self):
        """Вывод финальной статистики"""
        logger.info("=== ФИНАЛЬНАЯ СТАТИСТИКА АЛЬФА-БОТА ===")
        logger.info(f"Всего сделок: {len(self.trade_history)}")
        
        balance = self.broker.get_balance()
        if balance:
            logger.info(f"Финальный баланс: {balance:,.2f} RUB")
        
        if self.trade_history:
            logger.info("Последние сделки:")
            for trade in self.trade_history[-5:]:
                logger.info(f"{trade['timestamp'].strftime('%H:%M:%S')} - "
                          f"{trade['action']} {trade['quantity']} {trade['symbol']} "
                          f"по ~{trade['price']:.2f} RUB")