"""
Yahoo Finance 가격 조회 서비스
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import threading
import time
from .yahoo_client import YahooClient
from .symbol_normalizer import SymbolNormalizer


class YahooPriceService:
    """Yahoo Finance 가격 조회 서비스"""
    
    def __init__(self):
        self.client = YahooClient()
        self.symbol_normalizer = SymbolNormalizer()
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
        # 캐시 확인
        if self._is_cache_valid(symbol):
            return self.price_cache.get(symbol)
        
        # 새로 조회
        price_data = self.client.get_stock_info(symbol)
        if price_data:
            self._update_cache(symbol, price_data)
        
        return price_data
    
    def get_multiple_stock_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """여러 주식 가격 조회 (캐시 포함)"""
        results = {}
        symbols_to_fetch = []
        
        # 캐시에서 유효한 데이터 확인
        for symbol in symbols:
            if self._is_cache_valid(symbol):
                results[symbol] = self.price_cache.get(symbol)
            else:
                symbols_to_fetch.append(symbol)
        
        # 캐시에 없는 종목들 새로 조회
        if symbols_to_fetch:
            new_prices = self.client.get_multiple_stock_info(symbols_to_fetch)
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
            'symbol': price_data.get('symbol'),
            'normalized_symbol': price_data.get('normalized_symbol'),
            'current_price': price_data.get('current_price', 0),
            'previous_close': price_data.get('previous_close', 0),
            'change_amount': price_data.get('change_amount', 0),
            'change_rate': price_data.get('change_rate', 0),
            'volume': price_data.get('volume', 0),
            'market_cap': price_data.get('market_cap', 0),
            'currency': price_data.get('currency', 'USD'),
            'market': price_data.get('market', 'Unknown'),
            'sector': price_data.get('sector', 'Unknown'),
            'industry': price_data.get('industry', 'Unknown'),
            'updated_at': price_data.get('updated_at')
        }
    
    def get_stock_history(self, symbol: str, period: str = '1mo') -> Optional[Dict[str, Any]]:
        """주식 히스토리 조회"""
        return self.client.get_stock_history(symbol, period)
    
    def search_stocks(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """주식 검색"""
        return self.client.search_symbol(query, limit)
    
    def get_market_status(self) -> Dict[str, Any]:
        """시장 상태 조회"""
        return self.client.get_market_status()
    
    def validate_symbol(self, symbol: str) -> bool:
        """심볼 유효성 검증"""
        return self.client.validate_symbol(symbol)
    
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
    
    def get_symbol_info(self, symbol: str) -> Dict[str, str]:
        """심볼 정보 반환"""
        return self.symbol_normalizer.get_symbol_info(symbol)
    
    def normalize_symbol(self, symbol: str) -> Optional[str]:
        """심볼 정규화"""
        return self.symbol_normalizer.normalize_symbol(symbol)
    
    def add_custom_symbol(self, original: str, yahoo_symbol: str, market: str = 'US'):
        """커스텀 심볼 추가"""
        self.symbol_normalizer.add_custom_symbol(original, yahoo_symbol, market)
    
    def get_all_korean_stocks(self) -> Dict[str, str]:
        """모든 한국 주식 심볼 반환"""
        return self.symbol_normalizer.korean_symbols.copy()
    
    def get_all_us_stocks(self) -> Dict[str, str]:
        """모든 미국 주식 심볼 반환"""
        return self.symbol_normalizer.us_symbols.copy()
    
    def get_all_etfs(self) -> Dict[str, str]:
        """모든 ETF 심볼 반환"""
        return self.symbol_normalizer.etf_symbols.copy()
    
    def batch_update_prices(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """배치 가격 업데이트 (캐시 우회)"""
        results = {}
        
        for symbol in symbols:
            try:
                # 캐시 우회하여 새로 조회
                price_data = self.client.get_stock_info(symbol)
                if price_data:
                    results[symbol] = price_data
                    self._update_cache(symbol, price_data)
                
                # API 호출 제한을 위한 딜레이
                time.sleep(0.1)
                
            except Exception as e:
                print(f"배치 업데이트 오류 ({symbol}): {e}")
                continue
        
        return results
    
    def get_portfolio_summary(self, symbols: List[str]) -> Dict[str, Any]:
        """포트폴리오 요약 정보"""
        prices = self.get_multiple_stock_prices(symbols)
        
        if not prices:
            return {
                'total_symbols': len(symbols),
                'successful_quotes': 0,
                'failed_quotes': len(symbols),
                'markets': {},
                'summary': 'No data available'
            }
        
        # 시장별 통계
        markets = {}
        for symbol, data in prices.items():
            market = data.get('market', 'Unknown')
            if market not in markets:
                markets[market] = {
                    'count': 0,
                    'total_volume': 0,
                    'total_market_cap': 0
                }
            
            markets[market]['count'] += 1
            markets[market]['total_volume'] += data.get('volume', 0)
            markets[market]['total_market_cap'] += data.get('market_cap', 0)
        
        return {
            'total_symbols': len(symbols),
            'successful_quotes': len(prices),
            'failed_quotes': len(symbols) - len(prices),
            'markets': markets,
            'summary': f"Successfully quoted {len(prices)} out of {len(symbols)} symbols"
        }


# 전역 서비스 인스턴스 (싱글톤 패턴)
_service_instance = None
_service_lock = threading.Lock()

def get_yahoo_price_service() -> YahooPriceService:
    """전역 Yahoo 가격 서비스 인스턴스 반환"""
    global _service_instance
    with _service_lock:
        if _service_instance is None:
            _service_instance = YahooPriceService()
        return _service_instance
