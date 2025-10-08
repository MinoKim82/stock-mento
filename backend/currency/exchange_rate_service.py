"""
한국수출입은행 환율 조회 서비스

환율 정보를 조회하고 캐싱하는 서비스
- 1일 1회만 API 호출
- 메모리 캐싱
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class ExchangeRateService:
    """한국수출입은행 환율 조회 서비스"""
    
    # API 엔드포인트
    API_URL = "https://oapi.koreaexim.go.kr/site/program/financial/exchangeJSON"
    
    def __init__(self):
        """서비스 초기화"""
        self.auth_key = os.getenv('EXCHANGE_RATE_AUTH_KEY')
        if not self.auth_key:
            print("⚠️ EXCHANGE_RATE_AUTH_KEY가 .env 파일에 설정되지 않았습니다.")
        
        # 캐시 저장소
        self._cache: Dict[str, Dict] = {}
        self._last_update: Optional[datetime] = None
        self._cache_duration = timedelta(days=1)  # 1일
        
        print("✅ 환율 조회 서비스가 초기화되었습니다.")
    
    def _should_update_cache(self) -> bool:
        """캐시를 업데이트해야 하는지 확인"""
        if self._last_update is None:
            return True
        
        elapsed = datetime.now() - self._last_update
        return elapsed >= self._cache_duration
    
    def _fetch_exchange_rates(self, search_date: Optional[str] = None) -> Optional[list]:
        """
        한국수출입은행 API에서 환율 정보 조회
        
        Args:
            search_date: 조회 날짜 (YYYYMMDD 형식, 기본값: 오늘)
        
        Returns:
            환율 정보 리스트 또는 None
        """
        if not self.auth_key:
            print("❌ 환율 API 인증키가 없습니다.")
            return None
        
        # 날짜 설정 (기본값: 오늘)
        if search_date is None:
            search_date = datetime.now().strftime('%Y%m%d')
        
        try:
            params = {
                'authkey': self.auth_key,
                'searchdate': search_date,
                'data': 'AP01'  # 환율 정보
            }
            
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 결과 코드 확인 (dict 형태)
            if isinstance(data, dict) and 'result' in data:
                result_code = data.get('result')
                if result_code == 2:
                    print(f"❌ DATA 코드 오류")
                    return None
                elif result_code == 3:
                    print(f"❌ 인증코드 오류")
                    return None
                elif result_code == 4:
                    print(f"❌ 일일 제한 횟수 마감")
                    return None
            
            # 리스트 형태의 응답
            if isinstance(data, list) and len(data) > 0:
                # result 필드 확인 (첫 번째 항목에 있을 수 있음)
                if isinstance(data[0], dict) and 'result' in data[0]:
                    result_code = int(data[0].get('result', 0))
                    if result_code != 1:
                        print(f"❌ API 오류 (코드: {result_code})")
                        return None
                return data
            elif isinstance(data, list) and len(data) == 0:
                # 빈 배열 - 주말이나 공휴일일 가능성
                print(f"⚠️ {search_date} 날짜의 환율 데이터가 없습니다. (주말/공휴일 가능성)")
                # 최근 평일 데이터 시도
                for days_ago in range(1, 10):
                    prev_date = (datetime.strptime(search_date, '%Y%m%d') - timedelta(days=days_ago)).strftime('%Y%m%d')
                    prev_params = params.copy()
                    prev_params['searchdate'] = prev_date
                    prev_response = requests.get(self.API_URL, params=prev_params, timeout=10)
                    prev_data = prev_response.json()
                    if isinstance(prev_data, list) and len(prev_data) > 0:
                        print(f"✅ {prev_date} 날짜의 환율 데이터 사용")
                        return prev_data
                print(f"❌ 최근 환율 데이터를 찾을 수 없습니다.")
                return None
            else:
                print(f"⚠️ 예상치 못한 응답 형식: {type(data)}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 환율 API 호출 실패: {e}")
            return None
        except Exception as e:
            print(f"❌ 환율 데이터 처리 실패: {e}")
            return None
    
    def _update_cache(self) -> bool:
        """캐시 업데이트"""
        print("🔄 환율 정보를 업데이트합니다...")
        
        data = self._fetch_exchange_rates()
        
        if data is None:
            print("❌ 환율 정보 업데이트 실패")
            return False
        
        # 캐시 초기화
        self._cache.clear()
        
        # 데이터 파싱 및 저장
        for item in data:
            try:
                # 소문자 필드명 사용 (실제 API 응답)
                cur_unit = item.get('cur_unit')  # 통화 코드
                cur_nm = item.get('cur_nm')      # 통화명
                ttb = item.get('ttb')            # 전신환(송금) 받으실때
                tts = item.get('tts')            # 전신환(송금) 보내실때
                deal_bas_r = item.get('deal_bas_r')  # 매매 기준율
                
                if cur_unit and deal_bas_r:
                    # 쉼표 제거 및 float 변환
                    deal_bas_r_value = float(deal_bas_r.replace(',', ''))
                    ttb_value = float(ttb.replace(',', '')) if ttb else deal_bas_r_value
                    tts_value = float(tts.replace(',', '')) if tts else deal_bas_r_value
                    
                    self._cache[cur_unit] = {
                        'currency_code': cur_unit,
                        'currency_name': cur_nm,
                        'buy_rate': ttb_value,      # 살 때 (은행 기준)
                        'sell_rate': tts_value,     # 팔 때 (은행 기준)
                        'base_rate': deal_bas_r_value,  # 기준율
                        'last_update': datetime.now().isoformat()
                    }
            except (ValueError, KeyError, AttributeError) as e:
                print(f"⚠️ 환율 데이터 파싱 오류: {item}, {e}")
                continue
        
        self._last_update = datetime.now()
        print(f"✅ 환율 정보 업데이트 완료 ({len(self._cache)}개 통화)")
        return True
    
    def get_rate(self, currency_code: str, rate_type: str = 'base') -> Optional[float]:
        """
        특정 통화의 환율 조회
        
        Args:
            currency_code: 통화 코드 (예: 'USD', 'JPY(100)', 'EUR')
            rate_type: 환율 타입 ('base': 기준율, 'buy': 살 때, 'sell': 팔 때)
        
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
        
        rate_key = {
            'base': 'base_rate',
            'buy': 'buy_rate',
            'sell': 'sell_rate'
        }.get(rate_type, 'base_rate')
        
        return rate_info.get(rate_key)
    
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
        미국 달러(USD) 기준 환율 조회
        
        Returns:
            USD 기준 환율 또는 None
        """
        return self.get_rate('USD', 'base')
    
    def convert_to_krw(self, amount: float, currency_code: str) -> Optional[float]:
        """
        외화를 원화로 변환
        
        Args:
            amount: 외화 금액
            currency_code: 통화 코드
        
        Returns:
            원화 금액 또는 None
        """
        rate = self.get_rate(currency_code, 'base')
        
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
            'cache_duration_hours': self._cache_duration.total_seconds() / 3600
        }


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

