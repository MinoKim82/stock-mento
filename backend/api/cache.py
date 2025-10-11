"""
캐시 관리 API 라우터
"""
from fastapi import APIRouter, HTTPException
from typing import List
import os
import json

from .models import CacheInfo
from .dependencies import get_current_parser, set_current_parser
from logger_config import main_logger as logger

router = APIRouter(prefix="/cache", tags=["cache"])

# 경로 설정 (main.py에서 가져올 변수)
CURRENT_CSV_FILE = None
PARSED_DATA_FILE = None

def init_cache_paths(csv_file: str, parsed_file: str):
    """캐시 경로 초기화"""
    global CURRENT_CSV_FILE, PARSED_DATA_FILE
    CURRENT_CSV_FILE = csv_file
    PARSED_DATA_FILE = parsed_file

@router.get("/info", response_model=CacheInfo)
async def get_cache_info():
    """현재 CSV 파일 정보 조회"""
    logger.debug("캐시 정보 조회 요청")
    
    try:
        parser = get_current_parser()
        has_data = True
    except:
        parser = None
        has_data = False
    
    has_parsed_data = os.path.exists(PARSED_DATA_FILE) if PARSED_DATA_FILE else False
    
    # 파일 크기 계산
    total_size = 0
    if CURRENT_CSV_FILE and os.path.exists(CURRENT_CSV_FILE):
        total_size += os.path.getsize(CURRENT_CSV_FILE)
    if PARSED_DATA_FILE and os.path.exists(PARSED_DATA_FILE):
        total_size += os.path.getsize(PARSED_DATA_FILE)
    
    return CacheInfo(
        csv_file=CURRENT_CSV_FILE if os.path.exists(CURRENT_CSV_FILE) else None,
        parsed_data_file=PARSED_DATA_FILE if has_parsed_data else None,
        has_data=has_data,
        has_parsed_data=has_parsed_data,
        sessions=["current"] if has_data else [],
        total_sessions=1 if has_data else 0,
        total_cache_size=total_size,
        total_cache_size_mb=round(total_size / (1024 * 1024), 2)
    )

@router.delete("/{session_id}")
async def clear_session_cache(session_id: str):
    """특정 세션의 캐시 삭제"""
    logger.info(f"세션 캐시 삭제 요청: {session_id}")
    
    set_current_parser(None)
    
    # 파싱된 데이터 파일 삭제
    if PARSED_DATA_FILE and os.path.exists(PARSED_DATA_FILE):
        os.remove(PARSED_DATA_FILE)
        logger.info(f"파싱 데이터 삭제: {PARSED_DATA_FILE}")
    
    return {"message": f"세션 {session_id}의 캐시가 삭제되었습니다."}

@router.delete("/clear")
async def clear_all_cache():
    """모든 캐시 삭제"""
    logger.info("전체 캐시 삭제 요청")
    
    set_current_parser(None)
    
    # CSV 파일 삭제
    if CURRENT_CSV_FILE and os.path.exists(CURRENT_CSV_FILE):
        os.remove(CURRENT_CSV_FILE)
        logger.info(f"CSV 파일 삭제: {CURRENT_CSV_FILE}")
    
    # 파싱된 데이터 파일 삭제
    if PARSED_DATA_FILE and os.path.exists(PARSED_DATA_FILE):
        os.remove(PARSED_DATA_FILE)
        logger.info(f"파싱 데이터 삭제: {PARSED_DATA_FILE}")
    
    return {"message": "모든 캐시가 삭제되었습니다."}

