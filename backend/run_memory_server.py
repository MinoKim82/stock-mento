#!/usr/bin/env python3
"""
포트폴리오 분석 API 서버 실행 스크립트 (메모리 캐싱 버전)
CSV 파일을 메모리에 캐싱하여 처리하는 세션 기반 API 서버
"""

import uvicorn
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🚀 포트폴리오 분석 API 서버를 시작합니다... (메모리 캐싱)")
    print("📊 API 문서: http://localhost:8000/docs")
    print("🔗 서버 주소: http://localhost:8000")
    print("💾 메모리 캐싱: 활성화")
    print("🧹 파일 저장: 비활성화 (메모리만 사용)")
    print("=" * 50)
    
    # 메모리 캐싱 서버 실행
    uvicorn.run(
        "main_memory:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[current_dir]
    )

