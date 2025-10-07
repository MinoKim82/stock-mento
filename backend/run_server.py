#!/usr/bin/env python3
"""
Stock Portfolio API 서버 실행 스크립트
"""

import uvicorn
import sys
import os

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Stock Portfolio API 서버를 시작합니다...")
    print("📊 API 문서: http://localhost:8000/docs")
    print("🔗 서버 주소: http://localhost:8000")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./"],
        log_level="info"
    )
