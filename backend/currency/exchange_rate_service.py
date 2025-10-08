"""
네이버 금융 환율 조회 서비스

네이버 금융 페이지를 파싱하여 환율 정보를 가져오고 캐싱하는 서비스
- 1일 1회만 갱신
- JSON 파일에 저장
"""

import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, Optional


class ExchangeRateService:
    """네이버 금융 환율 조회 서비스"""
    
    # 네이버 금융 환율 페이지
    NAVER_FINANCE_URL = "https://finance.naver.com/marketindex/"
    
    # 캐시 파일 경로
    CACHE_DIR = "currency_cache"
    CACHE_FILE = os.path.join(CACHE_DIR, "exchange_rates.json")
    
    def __init__(self):
        """서비스 초기화"""
        # 캐시 디렉토리 생성
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        
        # 캐시 저장소
        self._cache: Dict[str, Dict] = {}
        self._last_update: Optional[datetime] = None
        self._cache_duration = timedelta(days=1)  # 1일
        
        # 기존 캐시 로드
        self._load_cache()
        
        print("✅ 환율 조회 서비스가 초기화되었습니다.")
    
    def _load_cache(self) -> bool:
        """파일에서 캐시 로드"""
        if not os.path.exists(self.CACHE_FILE):
            return False
        
        try:
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self._cache = data.get('rates', {})
            last_update_str = data.get('last_update')
            
            if last_update_str:
                self._last_update = datetime.fromisoformat(last_update_str)
                print(f"📂 캐시 파일 로드됨: {len(self._cache)}개 통화 ({last_update_str})")
                return True
            
        except Exception as e:
            print(f"⚠️ 캐시 파일 로드 실패: {e}")
        
        return False
    
    def _save_cache(self) -> bool:
        """캐시를 파일에 저장"""
        try:
            data = {
                'last_update': self._last_update.isoformat() if self._last_update else None,
                'rates': self._cache
            }
            
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 캐시 파일 저장 완료: {self.CACHE_FILE}")
            return True
            
        except Exception as e:
            print(f"❌ 캐시 파일 저장 실패: {e}")
            return False
    
    def _should_update_cache(self) -> bool:
        """캐시를 업데이트해야 하는지 확인"""
        if self._last_update is None:
            return True
        
        elapsed = datetime.now() - self._last_update
        return elapsed >= self._cache_duration
    
    def _fetch_exchange_rates(self) -> Optional[Dict]:
        """
        네이버 금융에서 환율 정보 스크래핑
        
        Returns:
            환율 정보 딕셔너리 또는 None
        """
        try:
            # User-Agent 헤더 추가
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(
                self.NAVER_FINANCE_URL,
                headers=headers,
                params={'tabSel': 'exchange'},
                timeout=10
            )
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 환율 데이터 추출
            rates = {}
            
            # data_lst 영역에서 환율 정보 파싱
            data_lists = soup.find_all('ul', {'class': 'data_lst'})
            
            # 통화 코드 매핑
            code_map = {
                '미국 USD': 'USD',
                '일본 JPY(100엔)': 'JPY',
                '유럽연합 EUR': 'EUR',
                '중국 CNY': 'CNY',
                '영국 GBP': 'GBP',
                '호주 AUD': 'AUD',
                '캐나다 CAD': 'CAD',
                '스위스 CHF': 'CHF',
                '홍콩 HKD': 'HKD',
                '스웨덴 SEK': 'SEK',
                '뉴질랜드 NZD': 'NZD',
                '체코 CZK': 'CZK',
                '칠레 CLP': 'CLP',
                '터키 TRY': 'TRY',
                '몽골 MNT': 'MNT',
                '이스라엘 ILS': 'ILS',
                '덴마크 DKK': 'DKK',
                '노르웨이 NOK': 'NOK',
                '사우디 SAR': 'SAR',
                '쿠웨이트 KWD': 'KWD',
                '바레인 BHD': 'BHD',
                '아랍에미리트 AED': 'AED',
            }
            
            for data_list in data_lists:
                items = data_list.find_all('li')
                
                for item in items:
                    # h3 태그에서 통화명 추출
                    h3 = item.find('h3')
                    if not h3:
                        continue
                    
                    # span 태그에서 실제 통화명 가져오기
                    currency_span = h3.find('span', {'class': 'blind'})
                    if not currency_span:
                        # blind 클래스가 없으면 직접 텍스트 사용
                        currency_name = h3.text.strip()
                    else:
                        currency_name = currency_span.text.strip()
                    
                    # 환율 값 추출
                    value_span = item.find('span', {'class': 'value'})
                    if not value_span:
                        continue
                    
                    try:
                        rate = float(value_span.text.strip().replace(',', ''))
                        
                        # 통화 코드 찾기
                        currency_code = code_map.get(currency_name)
                        
                        if currency_code:
                            rates[currency_code] = {
                                'currency_code': currency_code,
                                'currency_name': currency_name,
                                'rate': rate,
                                'last_update': datetime.now().isoformat()
                            }
                    except (ValueError, AttributeError) as e:
                        continue
            
            if rates:
                return rates
            else:
                print("⚠️ 환율 데이터를 찾을 수 없습니다.")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네이버 금융 접근 실패: {e}")
            return None
        except Exception as e:
            print(f"❌ 환율 데이터 파싱 실패: {e}")
            return None
    
    def _update_cache(self) -> bool:
        """캐시 업데이트"""
        print("🔄 환율 정보를 업데이트합니다...")
        
        rates = self._fetch_exchange_rates()
        
        if rates is None:
            print("❌ 환율 정보 업데이트 실패")
            return False
        
        # 캐시 업데이트
        self._cache = rates
        self._last_update = datetime.now()
        
        # 파일에 저장
        self._save_cache()
        
        print(f"✅ 환율 정보 업데이트 완료 ({len(self._cache)}개 통화)")
        return True
    
    def get_rate(self, currency_code: str) -> Optional[float]:
        """
        특정 통화의 환율 조회
        
        Args:
            currency_code: 통화 코드 (예: 'USD', 'JPY', 'EUR')
        
        Returns:
            환율 또는 None
        """
        # 캐시 업데이트 필요 시 업데이트
        if self._should_update_cache():
            self._update_cache()
        
        # 캐시에서 조회
        rate_info = self._cache.get(currency_code)
        
        if rate_info is None:
            print(f"⚠️ {currency_code} 환율 정보를 찾을 수 없습니다.")
            return None
        
        return rate_info.get('rate')
    
    def get_all_rates(self) -> Dict[str, Dict]:
        """
        모든 환율 정보 조회
        
        Returns:
            전체 환율 정보 딕셔너리
        """
        # 캐시 업데이트 필요 시 업데이트
        if self._should_update_cache():
            self._update_cache()
        
        return self._cache.copy()
    
    def get_usd_rate(self) -> Optional[float]:
        """
        미국 달러(USD) 환율 조회
        
        Returns:
            USD 환율 또는 None
        """
        return self.get_rate('USD')
    
    def convert_to_krw(self, amount: float, currency_code: str) -> Optional[float]:
        """
        외화를 원화로 변환
        
        Args:
            amount: 외화 금액
            currency_code: 통화 코드
        
        Returns:
            원화 금액 또는 None
        """
        rate = self.get_rate(currency_code)
        
        if rate is None:
            return None
        
        return amount * rate
    
    def get_cache_info(self) -> Dict:
        """
        캐시 정보 조회
        
        Returns:
            캐시 상태 정보
        """
        return {
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'next_update': (self._last_update + self._cache_duration).isoformat() if self._last_update else None,
            'cached_currencies': len(self._cache),
            'cache_duration_hours': self._cache_duration.total_seconds() / 3600,
            'cache_file': self.CACHE_FILE
        }
    
    def force_update(self) -> bool:
        """
        강제로 환율 정보 업데이트
        
        Returns:
            성공 여부
        """
        return self._update_cache()


# 싱글톤 인스턴스
_exchange_rate_service: Optional[ExchangeRateService] = None


def get_exchange_rate_service() -> ExchangeRateService:
    """
    환율 조회 서비스 인스턴스 가져오기 (싱글톤)
    
    Returns:
        ExchangeRateService 인스턴스
    """
    global _exchange_rate_service
    
    if _exchange_rate_service is None:
        _exchange_rate_service = ExchangeRateService()
    
    return _exchange_rate_service
