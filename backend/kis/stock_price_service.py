"""
한국 주식 실시간 가격 조회 서비스
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import time
from .kis_client import KISClient
from .config import KISConfig


class StockPriceService:
    """한국 주식 실시간 가격 조회 서비스"""
    
    def __init__(self, config: Optional[KISConfig] = None):
        self.config = config or KISConfig()
        self.client = KISClient(self.config)
        self.price_cache = {}
        self.cache_expiry = {}  # 캐시 만료 시간
        self.cache_duration = timedelta(minutes=5)  # 5분 캐시
        self.lock = threading.Lock()
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """캐시가 유효한지 확인"""
        if symbol not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[symbol]
    
    def _update_cache(self, symbol: str, price_data: Dict[str, Any]):
        """캐시 업데이트"""
        with self.lock:
            self.price_cache[symbol] = price_data
            self.cache_expiry[symbol] = datetime.now() + self.cache_duration
    
    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """단일 주식 가격 조회 (캐시 포함)"""
        # 한국 주식이 아니면 None 반환
        if not symbol.endswith('ks'):
            return None
        
        # 캐시 확인
        if self._is_cache_valid(symbol):
            return self.price_cache.get(symbol)
        
        # 새로 조회
        price_data = self.client.get_stock_price(symbol)
        if price_data:
            self._update_cache(symbol, price_data)
        
        return price_data
    
    def get_multiple_stock_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """여러 주식 가격 조회 (캐시 포함)"""
        results = {}
        symbols_to_fetch = []
        
        # 캐시에서 유효한 데이터 확인
        for symbol in symbols:
            if symbol.endswith('ks'):
                if self._is_cache_valid(symbol):
                    results[symbol] = self.price_cache.get(symbol)
                else:
                    symbols_to_fetch.append(symbol)
        
        # 캐시에 없는 종목들 새로 조회
        if symbols_to_fetch:
            new_prices = self.client.get_multiple_stock_prices(symbols_to_fetch)
            for symbol, price_data in new_prices.items():
                results[symbol] = price_data
                self._update_cache(symbol, price_data)
        
        return results
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """현재가만 반환"""
        price_data = self.get_stock_price(symbol)
        return price_data.get('current_price') if price_data else None
    
    def get_price_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """가격 정보 상세 조회"""
        price_data = self.get_stock_price(symbol)
        if not price_data:
            return None
        
        return {
            'symbol': symbol,
            'current_price': price_data.get('current_price', 0),
            'change_rate': price_data.get('change_rate', 0),
            'change_amount': price_data.get('change_amount', 0),
            'volume': price_data.get('volume', 0),
            'market_cap': price_data.get('market_cap', 0),
            'updated_at': price_data.get('updated_at')
        }
    
    def clear_cache(self, symbol: Optional[str] = None):
        """캐시 클리어"""
        with self.lock:
            if symbol:
                self.price_cache.pop(symbol, None)
                self.cache_expiry.pop(symbol, None)
            else:
                self.price_cache.clear()
                self.cache_expiry.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """캐시 정보 조회"""
        with self.lock:
            return {
                'cached_symbols': list(self.price_cache.keys()),
                'cache_size': len(self.price_cache),
                'expiry_times': {k: v.isoformat() for k, v in self.cache_expiry.items()}
            }


# 전역 서비스 인스턴스 (싱글톤 패턴)
_service_instance = None
_service_lock = threading.Lock()

def get_stock_price_service() -> StockPriceService:
    """전역 주식 가격 서비스 인스턴스 반환"""
    global _service_instance
    with _service_lock:
        if _service_instance is None:
            _service_instance = StockPriceService()
        return _service_instance
