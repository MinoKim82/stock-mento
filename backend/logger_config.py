"""
로깅 설정 모듈
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 프로젝트 루트의 log_data 디렉토리
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "log_data")
os.makedirs(LOG_DIR, exist_ok=True)

# 로그 파일 경로
BACKEND_LOG_FILE = os.path.join(LOG_DIR, "backend.log")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "backend_error.log")
ACCESS_LOG_FILE = os.path.join(LOG_DIR, "backend_access.log")

# 로그 포맷
DETAILED_FORMAT = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SIMPLE_FORMAT = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def setup_logger(name: str, log_file: str, level=logging.INFO, use_detailed_format=True):
    """로거 설정"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 파일 핸들러 (로테이션: 10MB, 백업 5개)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(DETAILED_FORMAT if use_detailed_format else SIMPLE_FORMAT)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(SIMPLE_FORMAT)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 기본 로거들
main_logger = setup_logger('backend', BACKEND_LOG_FILE, logging.DEBUG)
error_logger = setup_logger('backend.error', ERROR_LOG_FILE, logging.ERROR)
access_logger = setup_logger('backend.access', ACCESS_LOG_FILE, logging.INFO, use_detailed_format=False)

def log_exception(logger, exc: Exception, context: str = ""):
    """예외 로깅"""
    import traceback
    error_msg = f"{context}\n{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
    logger.error(error_msg)
    error_logger.error(error_msg)

def log_api_call(endpoint: str, method: str, status_code: int, duration_ms: float):
    """API 호출 로깅"""
    access_logger.info(
        f"{method} {endpoint} | Status: {status_code} | Duration: {duration_ms:.2f}ms"
    )

def log_startup():
    """서버 시작 로그"""
    main_logger.info("="*60)
    main_logger.info(f"Backend Server Starting - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    main_logger.info("="*60)

def log_shutdown():
    """서버 종료 로그"""
    main_logger.info("="*60)
    main_logger.info(f"Backend Server Shutting Down - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    main_logger.info("="*60)

