"""
애플리케이션 설정
"""
import os
from pathlib import Path

# 경로 설정
BACKEND_DIR = Path(__file__).parent
PROJECT_ROOT = BACKEND_DIR.parent
USER_DATA_DIR = PROJECT_ROOT / "user_data"
LOG_DATA_DIR = PROJECT_ROOT / "log_data"

# CSV 저장 디렉토리
CSV_STORAGE_DIR = USER_DATA_DIR / "csv_data"
CURRENT_CSV_FILE = CSV_STORAGE_DIR / "current_portfolio.csv"

# 파싱된 데이터 캐시
PARSED_DATA_DIR = USER_DATA_DIR / "parsed_data"
PARSED_DATA_FILE = PARSED_DATA_DIR / "portfolio_data.json"

# 디렉토리 생성
for directory in [USER_DATA_DIR, LOG_DATA_DIR, CSV_STORAGE_DIR, PARSED_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 설정
class Settings:
    """애플리케이션 설정"""
    APP_TITLE = "Stock Portfolio API"
    APP_VERSION = "1.0.0"
    API_PREFIX = ""
    
    # CORS
    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = True
    CORS_METHODS = ["*"]
    CORS_HEADERS = ["*"]
    
    # 로깅
    LOG_LEVEL = "INFO"
    
    # 파일 경로 (문자열로 변환)
    CURRENT_CSV_FILE = str(CURRENT_CSV_FILE)
    PARSED_DATA_FILE = str(PARSED_DATA_FILE)
    CSV_STORAGE_DIR = str(CSV_STORAGE_DIR)
    PARSED_DATA_DIR = str(PARSED_DATA_DIR)

settings = Settings()

