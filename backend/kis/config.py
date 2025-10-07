"""
한국투자증권 API 설정
"""
import os
from typing import Optional
from dotenv import load_dotenv

class KISConfig:
    """KIS API 설정 클래스"""
    
    def __init__(self):
        # .env 파일 로드
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        
        # .env 파일에서 설정 로드 (python-dotenv 사용)
        self.user_id = os.getenv('KIS_USER_ID', 'your_user_id')
        self.account_no = os.getenv('KIS_ACCOUNT_NO', 'your_account_number')
        self.app_key = os.getenv('KIS_APP_KEY', 'your_app_key')
        self.app_secret = os.getenv('KIS_APP_SECRET', 'your_app_secret')
        
        # API 엔드포인트
        self.base_url = os.getenv('KIS_BASE_URL', 'https://openapi.koreainvestment.com:9443')
        self.real_base_url = os.getenv('KIS_REAL_BASE_URL', 'https://openapi.koreainvestment.com:9443')
        
        # 환경 설정
        self.env = os.getenv('KIS_ENV', 'sandbox')  # 'prod' or 'sandbox'
        
        # 토큰 관리
        self.token_file = os.path.join(os.path.dirname(__file__), '.token')
    
    def is_sandbox(self) -> bool:
        """모의투자 환경인지 확인"""
        return self.env == 'sandbox'
    
    def get_base_url(self) -> str:
        """환경에 따른 베이스 URL 반환"""
        return self.base_url if self.is_sandbox() else self.real_base_url
