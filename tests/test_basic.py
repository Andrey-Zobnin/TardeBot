"""
Базовые тесты для проверки работы модулей
"""

import sys
import os
import pytest

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import Config
from data.stock_data import StockDataProvider
from models.price_predictor import PricePredictor


def test_config_initialization():
    """Тест инициализации конфигурации"""
    config = Config()
    assert config is not None
    assert config.get('INITIAL_BALANCE') == 10000.0
    assert config.get('DEFAULT_SYMBOL') == 'AAPL'


def test_stock_data_provider_initialization():
    """Тест инициализации провайдера данных"""
    config = Config()
    provider = StockDataProvider(config)
    assert provider is not None
    assert provider.config == config


def test_price_predictor_initialization():
    """Тест инициализации предиктора цен"""
    config = Config()
    predictor = PricePredictor(config)
    assert predictor is not None
    assert predictor.config == config
    assert predictor.is_trained == False


if __name__ == "__main__":
    pytest.main([__file__])