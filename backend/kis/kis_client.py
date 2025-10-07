"""
한국투자증권 API 클라이언트
"""
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from .config import KISConfig


class KISClient:
    """한국투자증권 API 클라이언트"""
    
    def __init__(self, config: Optional[KISConfig] = None):
        self.config = config or KISConfig()
        self.access_token = None
        self.token_expires_at = None
        
        # 토큰 파일에서 기존 토큰 로드
        self._load_token()
    
    def _load_token(self):
        """파일에서 토큰 로드"""
        try:
            if os.path.exists(self.config.token_file):
                with open(self.config.token_file, 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('access_token')
                    expires_at_str = token_data.get('expires_at')
                    if expires_at_str:
                        self.token_expires_at = datetime.fromisoformat(expires_at_str)
        except Exception as e:
            print(f"토큰 로드 실패: {e}")
            self.access_token = None
            self.token_expires_at = None
    
    def _save_token(self):
        """토큰을 파일에 저장"""
        try:
            token_data = {
                'access_token': self.access_token,
                'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
            }
            with open(self.config.token_file, 'w') as f:
                json.dump(token_data, f)
        except Exception as e:
            print(f"토큰 저장 실패: {e}")
    
    def _is_token_valid(self) -> bool:
        """토큰이 유효한지 확인"""
        if not self.access_token or not self.token_expires_at:
            return False
        
        # 만료 1시간 전에 갱신
        return datetime.now() < (self.token_expires_at - timedelta(hours=1))
    
    def get_access_token(self) -> str:
        """액세스 토큰 획득 (자동 갱신 포함)"""
        if self._is_token_valid():
            return self.access_token
        
        # 새 토큰 발급
        return self._request_new_token()
    
    def _request_new_token(self) -> str:
        """새 액세스 토큰 요청"""
        url = f"{self.config.get_base_url()}/oauth2/tokenP"
        
        headers = {
            'content-type': 'application/json'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'appkey': self.config.app_key,
            'appsecret': self.config.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            self.access_token = result['access_token']
            
            # 토큰 만료 시간 설정 (24시간)
            self.token_expires_at = datetime.now() + timedelta(hours=24)
            
            # 토큰 저장
            self._save_token()
            
            print(f"새 액세스 토큰 발급 완료: {self.token_expires_at}")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"토큰 발급 실패: {e}")
        except KeyError:
            raise Exception("토큰 응답 형식 오류")
    
    def _get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        token = self.get_access_token()
        return {
            'Authorization': f'Bearer {token}',
            'appkey': self.config.app_key,
            'appsecret': self.config.app_secret,
            'tr_id': '',  # 각 API마다 설정 필요
            'content-type': 'application/json'
        }
    
    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """주식 현재가 조회"""
        # 한국 주식은 'ks' 접두사가 있는 경우에만 처리
        if not symbol.endswith('ks'):
            return None
        
        # 실제 종목 코드 추출 (ks 제거)
        stock_code = symbol.replace('ks', '')
        
        url = f"{self.config.get_base_url()}/uapi/domestic-stock/v1/quotations/inquire-price"
        
        headers = self._get_headers()
        headers['tr_id'] = 'FHKST01010100'  # 주식현재가 시세 조회
        
        params = {
            'fid_cond_mrkt_div_code': 'J',  # 주식
            'fid_input_iscd': stock_code    # 종목코드
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('rt_cd') == '0':  # 성공
                output = result.get('output', {})
                return {
                    'symbol': symbol,
                    'current_price': float(output.get('stck_prpr', 0)),  # 현재가
                    'change_rate': float(output.get('prdy_vrss_ctrt', 0)),  # 등락률
                    'change_amount': float(output.get('prdy_vrss', 0)),  # 등락폭
                    'volume': int(output.get('acml_vol', 0)),  # 누적거래량
                    'market_cap': int(output.get('hts_avls', 0)),  # 시가총액
                    'updated_at': datetime.now().isoformat()
                }
            else:
                print(f"주식 가격 조회 실패: {result.get('msg1', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"주식 가격 조회 요청 실패: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"주식 가격 데이터 파싱 실패: {e}")
            return None
    
    def get_multiple_stock_prices(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """여러 주식의 현재가 조회"""
        results = {}
        
        for symbol in symbols:
            if symbol.endswith('ks'):
                price_data = self.get_stock_price(symbol)
                if price_data:
                    results[symbol] = price_data
                # API 호출 제한을 위한 딜레이
                time.sleep(0.1)
        
        return results


# 모듈 임포트 추가
import os
