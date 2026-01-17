"""
Модуль для получения данных о акциях
"""

import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any
from loguru import logger
from datetime import datetime, timedelta


class StockDataProvider:
    """Класс для получения данных о акциях"""
    
    def __init__(self, config):
        """Инициализация провайдера данных"""
        self.config = config
        self.cache = {}
        
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Получить текущую цену акции"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                logger.warning(f"Нет данных для символа {symbol}")
                return None
                
            current_price = data['Close'].iloc[-1]
            logger.info(f"Текущая цена {symbol}: ${current_price:.2f}")
            return float(current_price)
            
        except Exception as e:
            logger.error(f"Ошибка получения текущей цены для {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Получить исторические данные"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                logger.warning(f"Нет исторических данных для {symbol}")
                return None
                
            logger.info(f"Получено {len(data)} записей исторических данных для {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка получения исторических данных для {symbol}: {e}")
            return None
    
    def get_previous_price(self, symbol: str) -> Optional[float]:
        """Получить предыдущую цену закрытия"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d")
            
            if len(data) < 2:
                logger.warning(f"Недостаточно данных для получения предыдущей цены {symbol}")
                return None
                
            previous_price = data['Close'].iloc[-2]
            logger.info(f"Предыдущая цена {symbol}: ${previous_price:.2f}")
            return float(previous_price)
            
        except Exception as e:
            logger.error(f"Ошибка получения предыдущей цены для {symbol}: {e}")
            return None