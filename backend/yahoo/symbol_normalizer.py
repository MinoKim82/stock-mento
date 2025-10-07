"""
주식 심볼 정규화 모듈
Yahoo Finance API에서 사용할 수 있는 형태로 심볼을 변환합니다.
"""
from typing import Dict, List, Optional


class SymbolNormalizer:
    """주식 심볼 정규화 클래스"""
    
    def __init__(self):
        # 한국 주식 심볼 매핑 (종목명 -> Yahoo 심볼) - Securities_(Standard).csv 기반
        self.korean_symbols = {
            # 실제 보유 종목들 (Securities_(Standard).csv 기반)
            '삼성전자': '005930.KS',
            '기업은행': '024110.KS',
            'PS일렉트로닉스': '332570.KQ',  # KOSDAQ
            'GS글로벌': '001250.KS',
            
            # ETF (실제 보유 종목)
            'KODEX 200': '069500.KS',
            'KODEX 고배당주': '279530.KS',
            'ACE 미국S&P500': '360200.KS',
            'ACE 미국나스닥100': '367380.KS',
            'ACE 테슬라밸류체인액티브': '457480.KS',
            'RISE 미국S&P500': '379780.KS',
            'RISE 미국S&P500(H)': '453330.KS',
            'SOL 미국S&P500': '433330.KS',
            'TIGER 리츠부동산인프라': '329200.KS',
            'TIGER 미국S&P500': '360750.KS',
            'TIGER 미국배당다우존스': '458730.KS',
            
            # 추가 보유 종목들
            '가온칩스': '399720.KQ',  # KOSDAQ
            '금양': '001570.KS',
            '두산': '000155.KS',
            '유햔양행': '000100.KS',
            '제이오': '418550.KQ',  # KOSDAQ
            '코난테크놀로지': '402030.KQ',  # KOSDAQ
            '포스코DX': '022100.KS',
            '포스코엠텍': '009520.KQ',  # KOSDAQ
            '포스코인터내셔널': '047050.KS',
            
            # 기타 주요 종목들 (참고용)
            '삼성바이오로직스': '207940.KS',
            '삼성SDI': '006400.KS',
            '삼성물산': '028260.KS',
            '삼성생명': '032830.KS',
            '삼성화재': '000810.KS',
            '삼성전기': '009150.KS',
            '삼성중공업': '010140.KS',
            'LG화학': '051910.KS',
            'LG전자': '066570.KS',
            'LG생활건강': '051900.KS',
            'LG에너지솔루션': '373220.KS',
            'LG이노텍': '011070.KS',
            'SK하이닉스': '000660.KS',
            'SK텔레콤': '017670.KS',
            'SK이노베이션': '096770.KS',
            'SK바이오팜': '326030.KS',
            'SK': '034730.KS',
            '네이버': '035420.KS',
            '카카오': '035720.KS',
            '현대차': '005380.KS',
            '기아': '000270.KS',
            '현대모비스': '012330.KS',
            'POSCO': '005490.KS',
            'KB금융': '105560.KS',
            '신한지주': '055550.KS',
            '하나금융지주': '086790.KS',
            'KT&G': '033780.KS',
            '아모레퍼시픽': '090430.KS',
            '셀트리온': '068270.KS',
            '현대글로비스': '086280.KS',
            '한국전력': '015760.KS'
        }
        
        # 미국 주식 심볼 매핑 (종목명 -> Yahoo 심볼)
        self.us_symbols = {
            # 기술주
            'Apple': 'AAPL',
            'Microsoft': 'MSFT',
            'Google': 'GOOGL',
            'Amazon': 'AMZN',
            'Tesla': 'TSLA',
            'Meta': 'META',
            'Nvidia': 'NVDA',
            'Netflix': 'NFLX',
            'Oracle': 'ORCL',
            'Salesforce': 'CRM',
            
            # 금융주
            'JPMorgan': 'JPM',
            'Bank of America': 'BAC',
            'Wells Fargo': 'WFC',
            'Goldman Sachs': 'GS',
            'Morgan Stanley': 'MS',
            'Visa': 'V',
            'Mastercard': 'MA',
            
            # 소비재
            'Coca Cola': 'KO',
            'PepsiCo': 'PEP',
            'Procter & Gamble': 'PG',
            'Johnson & Johnson': 'JNJ',
            'Walmart': 'WMT',
            'Home Depot': 'HD',
            'Nike': 'NKE',
            
            # 에너지
            'Exxon Mobil': 'XOM',
            'Chevron': 'CVX',
            'ConocoPhillips': 'COP',
            
            # 헬스케어
            'Pfizer': 'PFE',
            'Merck': 'MRK',
            'AbbVie': 'ABBV',
            'Bristol Myers': 'BMY'
        }
        
        # ETF 심볼 매핑
        self.etf_symbols = {
            # 미국 ETF
            'SPDR S&P 500': 'SPY',
            'Invesco QQQ': 'QQQ',
            'iShares Russell 2000': 'IWM',
            'Vanguard Total Stock Market': 'VTI',
            'Vanguard S&P 500': 'VOO',
            'Vanguard S&P 500 ETF': 'VOO',  # Securities_(Standard).csv에서 확인
            'Schwab U.S. Dividend Equity': 'SCHD',
            
            # 국제 ETF
            'iShares MSCI EAFE': 'EFA',
            'Vanguard FTSE Developed Markets': 'VEA',
            'iShares MSCI Emerging Markets': 'EEM',
            
            # 섹터 ETF
            'Technology Select Sector': 'XLK',
            'Financial Select Sector': 'XLF',
            'Health Care Select Sector': 'XLV',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Energy Select Sector': 'XLE',
            'Industrial Select Sector': 'XLI',
            'Materials Select Sector': 'XLB',
            'Real Estate Select Sector': 'XLRE',
            'Utilities Select Sector': 'XLU',
            'Communication Services': 'XLC'
        }
    
    def normalize_symbol(self, symbol: str) -> Optional[str]:
        """
        주식 심볼을 Yahoo Finance에서 사용할 수 있는 형태로 정규화
        
        Args:
            symbol: 원본 심볼
            
        Returns:
            정규화된 심볼 또는 None
        """
        if not symbol:
            return None
        
        # 이미 Yahoo 형식인지 확인 (예: AAPL, 005930.KS)
        if self._is_yahoo_format(symbol):
            return symbol
        
        # 한국 주식 확인
        normalized = self._normalize_korean_stock(symbol)
        if normalized:
            return normalized
        
        # 미국 주식 확인
        normalized = self._normalize_us_stock(symbol)
        if normalized:
            return normalized
        
        # ETF 확인
        normalized = self._normalize_etf(symbol)
        if normalized:
            return normalized
        
        # 기본 정규화 시도
        return self._basic_normalize(symbol)
    
    def _is_yahoo_format(self, symbol: str) -> bool:
        """Yahoo 형식인지 확인"""
        # 이미 .KS, .KQ로 끝나는 경우 (한국 주식 코드)
        if symbol.endswith('.KS') or symbol.endswith('.KQ'):
            return True
        
        # 숫자로 시작하고 .KS로 끝나는 경우 (한국 주식 코드)
        if symbol.replace('.KS', '').replace('.KQ', '').isdigit():
            return True
        
        # 영문 대문자만으로 구성된 경우 (미국 주식 코드, 길이 1-5자, 한글 미포함)
        if symbol.isalpha() and symbol.isupper() and 1 <= len(symbol) <= 5 and all(ord(c) < 128 for c in symbol):
            return True
        
        return False
    
    def _normalize_korean_stock(self, symbol: str) -> Optional[str]:
        """한국 주식 심볼 정규화"""
        # 정확한 매칭
        if symbol in self.korean_symbols:
            return self.korean_symbols[symbol]
        
        # 부분 매칭 (포함 검색) - 더 정확한 매칭을 위해 우선순위 적용
        best_match = None
        best_score = 0
        
        for korean_name, yahoo_symbol in self.korean_symbols.items():
            # 정확한 매칭이면 즉시 반환
            if korean_name == symbol:
                return yahoo_symbol
            
            # 부분 매칭 점수 계산
            if korean_name in symbol:
                score = len(korean_name)  # 더 긴 매칭에 더 높은 점수
                if score > best_score:
                    best_match = yahoo_symbol
                    best_score = score
            elif symbol in korean_name:
                score = len(symbol)
                if score > best_score:
                    best_match = yahoo_symbol
                    best_score = score
        
        return best_match
    
    def _normalize_us_stock(self, symbol: str) -> Optional[str]:
        """미국 주식 심볼 정규화"""
        # 정확한 매칭
        if symbol in self.us_symbols:
            return self.us_symbols[symbol]
        
        # 부분 매칭
        for us_name, yahoo_symbol in self.us_symbols.items():
            if us_name in symbol or symbol in us_name:
                return yahoo_symbol
        
        return None
    
    def _normalize_etf(self, symbol: str) -> Optional[str]:
        """ETF 심볼 정규화"""
        # 정확한 매칭
        if symbol in self.etf_symbols:
            return self.etf_symbols[symbol]
        
        # ETF 키워드 확인
        etf_keywords = ['KODEX', 'TIGER', 'ACE', 'RISE', 'SOL', 'ARIRANG', 'SPDR', 'Invesco', 'iShares', 'Vanguard', 'Schwab', 'ETF']
        is_etf = any(keyword in symbol for keyword in etf_keywords)
        
        if is_etf:
            # 부분 매칭
            for etf_name, yahoo_symbol in self.etf_symbols.items():
                if etf_name in symbol or symbol in etf_name:
                    return yahoo_symbol
            
            # 한국 ETF의 경우 .KS 또는 .KQ 접미사가 있는지 확인
            if any(keyword in symbol for keyword in ['KODEX', 'TIGER', 'ACE', 'RISE', 'SOL', 'ARIRANG']):
                # 이미 .KS 또는 .KQ가 있는 경우 그대로 반환
                if symbol.endswith('.KS') or symbol.endswith('.KQ'):
                    return symbol
        
        return None
    
    def _basic_normalize(self, symbol: str) -> Optional[str]:
        """기본 정규화 시도"""
        # 한국 주식 패턴 확인 (6자리 숫자)
        if symbol.isdigit() and len(symbol) == 6:
            # KOSDAQ 종목 코드 패턴 확인 (3자리가 3으로 시작하는 경우)
            if symbol.startswith('3') or symbol.startswith('4'):
                return f"{symbol}.KQ"  # KOSDAQ
            else:
                return f"{symbol}.KS"  # KOSPI
        
        # 미국 주식 패턴 확인 (대문자 알파벳)
        if symbol.isalpha() and symbol.isupper() and len(symbol) <= 5:
            return symbol
        
        return None
    
    def get_symbol_info(self, symbol: str) -> Dict[str, str]:
        """
        심볼 정보 반환
        
        Returns:
            {
                'original': 원본 심볼,
                'normalized': 정규화된 심볼,
                'market': 시장 구분 (KR, US, ETF, UNKNOWN),
                'type': 종목 타입 (STOCK, ETF, UNKNOWN)
            }
        """
        normalized = self.normalize_symbol(symbol)
        
        if not normalized:
            return {
                'original': symbol,
                'normalized': None,
                'market': 'UNKNOWN',
                'type': 'UNKNOWN'
            }
        
        # 시장 구분
        if normalized.endswith('.KS') or normalized.endswith('.KQ'):
            market = 'KR'
            symbol_type = 'STOCK'
            # ETF 키워드가 있으면 ETF로 분류
            if any(etf in symbol for etf in ['ETF', 'KODEX', 'TIGER', 'ARIRANG', 'ACE', 'RISE', 'SOL']):
                symbol_type = 'ETF'
        elif normalized in self.etf_symbols.values() or any(etf in symbol for etf in ['ETF', 'KODEX', 'TIGER', 'ARIRANG', 'ACE', 'RISE', 'SOL']):
            market = 'ETF'
            symbol_type = 'ETF'
        elif normalized.isalpha() and len(normalized) <= 5:
            market = 'US'
            symbol_type = 'STOCK'
        else:
            market = 'UNKNOWN'
            symbol_type = 'UNKNOWN'
        
        return {
            'original': symbol,
            'normalized': normalized,
            'market': market,
            'type': symbol_type
        }
    
    def add_custom_symbol(self, original: str, yahoo_symbol: str, market: str = 'US'):
        """커스텀 심볼 추가"""
        if market == 'KR':
            self.korean_symbols[original] = yahoo_symbol
        elif market == 'US':
            self.us_symbols[original] = yahoo_symbol
        elif market == 'ETF':
            self.etf_symbols[original] = yahoo_symbol
