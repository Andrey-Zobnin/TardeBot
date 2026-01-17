"""
Модуль для предсказания цен акций с помощью машинного обучения
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Optional, Tuple, List
from loguru import logger


class PricePredictor:
    """Класс для предсказания цен акций"""
    
    def __init__(self, config):
        """Инициализация предиктора"""
        self.config = config
        self.model = None
        self.scaler = MinMaxScaler()
        self.is_trained = False
        self.feature_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
    def prepare_features(self, data: pd.DataFrame, window_size: int = 5) -> pd.DataFrame:
        """Подготовка признаков для модели"""
        try:
            df = data.copy()
            
            # Технические индикаторы
            df['SMA_5'] = df['Close'].rolling(window=5).mean()
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['RSI'] = self._calculate_rsi(df['Close'])
            df['Price_Change'] = df['Close'].pct_change()
            df['Volume_Change'] = df['Volume'].pct_change()
            
            # Лаговые признаки
            for i in range(1, window_size + 1):
                df[f'Close_lag_{i}'] = df['Close'].shift(i)
                df[f'Volume_lag_{i}'] = df['Volume'].shift(i)
            
            # Удаляем строки с NaN
            df = df.dropna()
            
            logger.info(f"Подготовлено {len(df)} записей с признаками")
            return df
            
        except Exception as e:
            logger.error(f"Ошибка подготовки признаков: {e}")
            return pd.DataFrame()
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Расчет индекса относительной силы (RSI)"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_model(self, data: pd.DataFrame) -> bool:
        """Обучение модели предсказания"""
        try:
            # Подготовка данных
            df = self.prepare_features(data)
            if df.empty:
                logger.error("Нет данных для обучения")
                return False
            
            # Выбор признаков и целевой переменной
            feature_cols = [col for col in df.columns if col not in ['Close']]
            X = df[feature_cols]
            y = df['Close']
            
            # Нормализация данных
            X_scaled = self.scaler.fit_transform(X)
            
            # Разделение на обучающую и тестовую выборки
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Обучение модели
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            
            self.model.fit(X_train, y_train)
            
            # Оценка качества модели
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            
            logger.info(f"Модель обучена. MAE: {mae:.2f}, MSE: {mse:.2f}")
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обучения модели: {e}")
            return False
    
    def predict_price(self, current_data: pd.DataFrame) -> Optional[float]:
        """Предсказание будущей цены"""
        try:
            if not self.is_trained or self.model is None:
                logger.error("Модель не обучена")
                return None
            
            # Подготовка данных для предсказания
            df = self.prepare_features(current_data)
            if df.empty:
                logger.error("Нет данных для предсказания")
                return None
            
            # Получаем последнюю запись
            feature_cols = [col for col in df.columns if col not in ['Close']]
            X = df[feature_cols].iloc[-1:]
            
            # Нормализация
            X_scaled = self.scaler.transform(X)
            
            # Предсказание
            predicted_price = self.model.predict(X_scaled)[0]
            
            logger.info(f"Предсказанная цена: ${predicted_price:.2f}")
            return float(predicted_price)
            
        except Exception as e:
            logger.error(f"Ошибка предсказания цены: {e}")
            return None