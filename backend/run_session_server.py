#!/usr/bin/env python3
"""
포트폴리오 분석 대시보드 서버 실행 스크립트
CSV 파일 업로드 기능이 포함된 세션 기반 API 서버
"""

import uvicorn
import os
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🚀 포트폴리오 분석 대시보드 서버를 시작합니다...")
    print("📊 API 문서: http://localhost:8000/docs")
    print("🔗 서버 주소: http://localhost:8000")
    print("🌐 프론트엔드: http://localhost:8000/static/index.html")
    print("=" * 50)
    
    # 세션 기반 서버 실행
    uvicorn.run(
        "main_session:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[current_dir]
    )
