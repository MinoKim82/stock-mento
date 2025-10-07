"""
Yahoo Finance API 클라이언트
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import yfinance as yf
from .symbol_normalizer import SymbolNormalizer


class YahooClient:
    """Yahoo Finance API 클라이언트"""
    
    def __init__(self):
        self.symbol_normalizer = SymbolNormalizer()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        주식 정보 조회
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            주식 정보 딕셔너리 또는 None
        """
        try:
            # 심볼 정규화
            normalized_symbol = self.symbol_normalizer.normalize_symbol(symbol)
            if not normalized_symbol:
                print(f"심볼 정규화 실패: {symbol}")
                return None
            
            # yfinance를 사용한 정보 조회
            ticker = yf.Ticker(normalized_symbol)
            info = ticker.info
            
            if not info or 'regularMarketPrice' not in info:
                print(f"정보 조회 실패: {normalized_symbol}")
                return None
            
            # 현재가 및 기본 정보 추출
            current_price = info.get('regularMarketPrice', 0)
            previous_close = info.get('previousClose', 0)
            change_amount = current_price - previous_close if previous_close > 0 else 0
            change_rate = (change_amount / previous_close * 100) if previous_close > 0 else 0
            
            return {
                'symbol': symbol,
                'normalized_symbol': normalized_symbol,
                'current_price': float(current_price),
                'previous_close': float(previous_close),
                'change_amount': float(change_amount),
                'change_rate': float(change_rate),
                'volume': int(info.get('volume', 0)),
                'market_cap': int(info.get('marketCap', 0)) if info.get('marketCap') else 0,
                'currency': info.get('currency', 'USD'),
                'market': info.get('market', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'updated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"주식 정보 조회 오류 ({symbol}): {e}")
            return None
    
    def get_multiple_stock_info(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        여러 주식 정보 조회
        
        Args:
            symbols: 주식 심볼 리스트
            
        Returns:
            {심볼: 정보} 딕셔너리
        """
        results = {}
        
        for symbol in symbols:
            try:
                info = self.get_stock_info(symbol)
                if info:
                    results[symbol] = info
                
                # API 호출 제한을 위한 딜레이
                time.sleep(0.1)
                
            except Exception as e:
                print(f"주식 정보 조회 오류 ({symbol}): {e}")
                continue
        
        return results
    
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """
        현재가만 조회
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            현재가 또는 None
        """
        info = self.get_stock_info(symbol)
        return info.get('current_price') if info else None
    
    def get_stock_history(self, symbol: str, period: str = '1mo') -> Optional[Dict[str, Any]]:
        """
        주식 히스토리 조회
        
        Args:
            symbol: 주식 심볼
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            히스토리 데이터 또는 None
        """
        try:
            normalized_symbol = self.symbol_normalizer.normalize_symbol(symbol)
            if not normalized_symbol:
                return None
            
            ticker = yf.Ticker(normalized_symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # 최근 데이터만 반환
            latest = hist.iloc[-1]
            
            return {
                'symbol': symbol,
                'normalized_symbol': normalized_symbol,
                'period': period,
                'data': {
                    'date': latest.name.isoformat(),
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'close': float(latest['Close']),
                    'volume': int(latest['Volume'])
                }
            }
            
        except Exception as e:
            print(f"히스토리 조회 오류 ({symbol}): {e}")
            return None
    
    def search_symbol(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        심볼 검색
        
        Args:
            query: 검색어
            limit: 결과 수 제한
            
        Returns:
            검색 결과 리스트
        """
        results = []
        query_lower = query.lower()
        
        # 한국 주식 검색
        for name, symbol in self.symbol_normalizer.korean_symbols.items():
            if query_lower in name.lower() and len(results) < limit:
                results.append({
                    'name': name,
                    'symbol': symbol,
                    'market': 'KR'
                })
        
        # 미국 주식 검색
        for name, symbol in self.symbol_normalizer.us_symbols.items():
            if query_lower in name.lower() and len(results) < limit:
                results.append({
                    'name': name,
                    'symbol': symbol,
                    'market': 'US'
                })
        
        # ETF 검색
        for name, symbol in self.symbol_normalizer.etf_symbols.items():
            if query_lower in name.lower() and len(results) < limit:
                results.append({
                    'name': name,
                    'symbol': symbol,
                    'market': 'ETF'
                })
        
        return results
    
    def get_market_status(self) -> Dict[str, Any]:
        """
        주요 시장 상태 조회
        
        Returns:
            시장 상태 정보
        """
        try:
            # 주요 지수 정보
            indices = {
                '^GSPC': 'S&P 500',
                '^IXIC': 'NASDAQ',
                '^DJI': 'Dow Jones',
                '^KS11': 'KOSPI',
                '^KQ11': 'KOSDAQ'
            }
            
            status = {}
            for symbol, name in indices.items():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    if info:
                        status[name] = {
                            'symbol': symbol,
                            'price': float(info.get('regularMarketPrice', 0)),
                            'change': float(info.get('regularMarketChange', 0)),
                            'change_rate': float(info.get('regularMarketChangePercent', 0)),
                            'is_open': info.get('marketState') == 'REGULAR'
                        }
                except:
                    continue
            
            return {
                'timestamp': datetime.now().isoformat(),
                'markets': status
            }
            
        except Exception as e:
            print(f"시장 상태 조회 오류: {e}")
            return {}
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        심볼 유효성 검증
        
        Args:
            symbol: 주식 심볼
            
        Returns:
            유효한 심볼인지 여부
        """
        try:
            normalized = self.symbol_normalizer.normalize_symbol(symbol)
            if not normalized:
                return False
            
            ticker = yf.Ticker(normalized)
            info = ticker.info
            
            return info is not None and 'regularMarketPrice' in info
            
        except:
            return False
