"""
Модуль для работы с API Альфа-Инвестиций
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from loguru import logger
from datetime import datetime, timedelta


class AlfaBroker:
    """Класс для работы с API Альфа-Инвестиций"""
    
    def __init__(self, config):
        """Инициализация брокера"""
        self.config = config
        self.token = config.get('ALFA_TOKEN')
        self.account_id = config.get('ALFA_ACCOUNT_ID')
        self.base_url = "https://apigateway.alfabank.ru/invest/v1"
        
        # Заголовки для запросов
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Кэш для инструментов
        self.instruments_cache = {}
        
        logger.info("Альфа-Брокер инициализирован")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Выполнение HTTP запроса к API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            else:
                logger.error(f"Неподдерживаемый HTTP метод: {method}")
                return None
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Превышен лимит запросов, ожидание...")
                time.sleep(1)
                return self._make_request(method, endpoint, data)
            else:
                logger.error(f"Ошибка API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка запроса к API: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Получение информации о счете"""
        logger.info("Получение информации о счете...")
        
        response = self._make_request('GET', f'/accounts/{self.account_id}')
        
        if response:
            logger.info(f"Информация о счете получена: {response.get('name', 'N/A')}")
            return response
        
        return None
    
    def get_portfolio(self) -> Optional[Dict]:
        """Получение портфеля"""
        logger.info("Получение портфеля...")
        
        response = self._make_request('GET', f'/accounts/{self.account_id}/portfolio')
        
        if response:
            positions = response.get('positions', [])
            logger.info(f"Портфель получен: {len(positions)} позиций")
            return response
        
        return None
    
    def get_balance(self) -> Optional[float]:
        """Получение баланса счета"""
        portfolio = self.get_portfolio()
        
        if portfolio:
            # Ищем рублевые позиции
            for position in portfolio.get('positions', []):
                if position.get('instrument_type') == 'currency' and position.get('ticker') == 'RUB':
                    balance = float(position.get('balance', 0))
                    logger.info(f"Баланс счета: {balance} RUB")
                    return balance
        
        logger.warning("Не удалось получить баланс")
        return None
    
    def search_instrument(self, query: str) -> Optional[List[Dict]]:
        """Поиск финансового инструмента"""
        logger.info(f"Поиск инструмента: {query}")
        
        response = self._make_request('GET', '/instruments/search', {'query': query})
        
        if response:
            instruments = response.get('instruments', [])
            logger.info(f"Найдено инструментов: {len(instruments)}")
            return instruments
        
        return None
    
    def get_instrument_by_ticker(self, ticker: str) -> Optional[Dict]:
        """Получение инструмента по тикеру"""
        if ticker in self.instruments_cache:
            return self.instruments_cache[ticker]
        
        instruments = self.search_instrument(ticker)
        
        if instruments:
            for instrument in instruments:
                if instrument.get('ticker') == ticker:
                    self.instruments_cache[ticker] = instrument
                    return instrument
        
        logger.warning(f"Инструмент {ticker} не найден")
        return None
    
    def get_current_price(self, ticker: str) -> Optional[float]:
        """Получение текущей цены инструмента"""
        instrument = self.get_instrument_by_ticker(ticker)
        
        if not instrument:
            return None
        
        figi = instrument.get('figi')
        if not figi:
            logger.error(f"FIGI не найден для {ticker}")
            return None
        
        response = self._make_request('GET', f'/market-data/last-prices', {'figis': [figi]})
        
        if response:
            last_prices = response.get('last_prices', [])
            if last_prices:
                price_data = last_prices[0]
                price = float(price_data.get('price', 0))
                logger.info(f"Текущая цена {ticker}: {price}")
                return price
        
        logger.warning(f"Не удалось получить цену для {ticker}")
        return None
    
    def get_candles(self, ticker: str, interval: str = '1day', days: int = 30) -> Optional[List[Dict]]:
        """Получение свечей (исторических данных)"""
        instrument = self.get_instrument_by_ticker(ticker)
        
        if not instrument:
            return None
        
        figi = instrument.get('figi')
        if not figi:
            return None
        
        # Рассчитываем временной интервал
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        params = {
            'figi': figi,
            'interval': interval,
            'from': start_time.isoformat(),
            'to': end_time.isoformat()
        }
        
        response = self._make_request('GET', '/market-data/candles', params)
        
        if response:
            candles = response.get('candles', [])
            logger.info(f"Получено {len(candles)} свечей для {ticker}")
            return candles
        
        return None
    
    def place_market_order(self, ticker: str, quantity: int, direction: str) -> Optional[Dict]:
        """Размещение рыночного ордера"""
        instrument = self.get_instrument_by_ticker(ticker)
        
        if not instrument:
            logger.error(f"Не удалось найти инструмент {ticker}")
            return None
        
        figi = instrument.get('figi')
        if not figi:
            logger.error(f"FIGI не найден для {ticker}")
            return None
        
        order_data = {
            'figi': figi,
            'quantity': abs(quantity),
            'direction': direction.upper(),  # BUY или SELL
            'account_id': self.account_id,
            'order_type': 'ORDER_TYPE_MARKET'
        }
        
        logger.info(f"Размещение {direction} ордера: {quantity} {ticker}")
        
        response = self._make_request('POST', '/orders', order_data)
        
        if response:
            order_id = response.get('order_id')
            logger.info(f"Ордер размещен: {order_id}")
            return response
        
        logger.error(f"Не удалось разместить ордер для {ticker}")
        return None
    
    def buy_market(self, ticker: str, quantity: int) -> Optional[Dict]:
        """Покупка по рыночной цене"""
        return self.place_market_order(ticker, quantity, 'BUY')
    
    def sell_market(self, ticker: str, quantity: int) -> Optional[Dict]:
        """Продажа по рыночной цене"""
        return self.place_market_order(ticker, quantity, 'SELL')
    
    def get_orders(self) -> Optional[List[Dict]]:
        """Получение списка ордеров"""
        response = self._make_request('GET', f'/accounts/{self.account_id}/orders')
        
        if response:
            orders = response.get('orders', [])
            logger.info(f"Получено ордеров: {len(orders)}")
            return orders
        
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Отмена ордера"""
        response = self._make_request('POST', f'/orders/{order_id}/cancel')
        
        if response:
            logger.info(f"Ордер {order_id} отменен")
            return True
        
        logger.error(f"Не удалось отменить ордер {order_id}")
        return False
    
    def get_operations(self, days: int = 7) -> Optional[List[Dict]]:
        """Получение операций за период"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        params = {
            'account_id': self.account_id,
            'from': start_time.isoformat(),
            'to': end_time.isoformat()
        }
        
        response = self._make_request('GET', '/operations', params)
        
        if response:
            operations = response.get('operations', [])
            logger.info(f"Получено операций: {len(operations)}")
            return operations
        
        return None