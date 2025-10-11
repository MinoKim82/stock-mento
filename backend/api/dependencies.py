"""
API 의존성 및 유틸리티
"""
from fastapi import HTTPException
from typing import Optional
from pp import TransactionParser

# 전역 파서 인스턴스
current_parser: Optional[TransactionParser] = None

def get_current_parser() -> TransactionParser:
    """현재 파서 인스턴스 반환"""
    if current_parser is None:
        raise HTTPException(
            status_code=404,
            detail="CSV 파일이 로드되지 않았습니다. CSV 파일을 업로드해주세요."
        )
    return current_parser

def set_current_parser(parser: Optional[TransactionParser]):
    """현재 파서 인스턴스 설정"""
    global current_parser
    current_parser = parser

def get_parser(session_id: str = None) -> TransactionParser:
    """세션 ID로 파서 가져오기 (현재는 단일 세션만 지원)"""
    return get_current_parser()

