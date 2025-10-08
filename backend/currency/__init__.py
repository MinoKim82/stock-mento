"""
Currency Exchange Rate Module

네이버 금융에서 환율 정보를 스크래핑하는 모듈
"""

from .exchange_rate_service import get_exchange_rate_service, ExchangeRateService

__all__ = ['get_exchange_rate_service', 'ExchangeRateService']

