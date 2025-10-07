#!/usr/bin/env python3
"""
포트폴리오 분석 대시보드 서버 시작 스크립트 (React 버전)
- Backend: FastAPI (포트 8000)
- Frontend: React + Vite (포트 5173)
"""

import subprocess
import os
import time
import signal
import sys
import webbrowser
from pathlib import Path

def print_banner():
    """시작 배너 출력"""
    print("=" * 60)
    print("🚀 포트폴리오 분석 대시보드 서버 시작")
    print("=" * 60)
    print("📊 Backend:  FastAPI + Python (포트 8000)")
    print("⚛️  Frontend: React + TypeScript + Vite (포트 5173)")
    print("=" * 60)

def start_backend():
    """Backend 서버 시작"""
    # 포트 8000 충돌 확인 및 해결
    if not check_port_available(8000):
        print("⚠️  포트 8000이 이미 사용 중입니다. 기존 프로세스를 종료합니다...")
        kill_process_on_port(8000)
        time.sleep(2)
    
    backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'main_memory.py')
    print(f"🔧 Backend 서버 시작: python {backend_path}")
    return subprocess.Popen([sys.executable, backend_path], preexec_fn=os.setsid)

def start_frontend():
    """Frontend 서버 시작"""
    # 포트 5173 충돌 확인 및 해결
    if not check_port_available(5173):
        print("⚠️  포트 5173이 이미 사용 중입니다. 기존 프로세스를 종료합니다...")
        kill_process_on_port(5173)
        time.sleep(2)
    
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
    print(f"⚛️  Frontend 서버 시작: npm run dev (포트 5173)")
    
    # npm run dev 명령어 실행
    return subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_path,
        preexec_fn=os.setsid,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def check_port_available(port):
    """포트 사용 가능 여부 확인"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def kill_process_on_port(port):
    """특정 포트를 사용하는 프로세스 종료"""
    import subprocess
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], check=False)
                    print(f"✅ 포트 {port} 사용 프로세스 {pid} 종료됨")
        return True
    except Exception as e:
        print(f"⚠️  포트 {port} 프로세스 종료 실패: {e}")
        return False

def check_backend_health():
    """Backend 서버 헬스 체크"""
    import requests
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def wait_for_backend():
    """Backend 서버가 준비될 때까지 대기"""
    print("⏳ Backend 서버 시작 대기 중...")
    max_attempts = 30
    for attempt in range(max_attempts):
        if check_backend_health():
            print("✅ Backend 서버가 준비되었습니다!")
            return True
        time.sleep(1)
        print(f"   시도 {attempt + 1}/{max_attempts}")
    
    print("❌ Backend 서버 시작에 실패했습니다.")
    return False

def open_browser():
    """브라우저에서 Frontend 열기"""
    try:
        webbrowser.open('http://localhost:5173')
        print("🌐 브라우저에서 Frontend가 열렸습니다.")
    except Exception as e:
        print(f"⚠️  브라우저 열기 실패: {e}")
        print("   수동으로 http://localhost:5173 에 접속해주세요.")

def print_access_info():
    """접속 정보 출력"""
    print("\n" + "=" * 60)
    print("🎉 모든 서버가 시작되었습니다!")
    print("=" * 60)
    print("📊 Backend API:  http://localhost:8000")
    print("⚛️  Frontend UI:  http://localhost:5173")
    print("📚 API 문서:     http://localhost:8000/docs")
    print("=" * 60)
    print("💡 사용법:")
    print("   1. Frontend에서 CSV 파일 업로드")
    print("   2. 실시간 포트폴리오 분석 결과 확인")
    print("   3. Ctrl+C로 서버 종료")
    print("=" * 60)

def main():
    backend_process = None
    frontend_process = None
    
    try:
        print_banner()
        
        # Backend 서버 시작
        backend_process = start_backend()
        time.sleep(2)
        
        # Backend 서버 헬스 체크
        if not wait_for_backend():
            return 1
        
        # Frontend 서버 시작
        frontend_process = start_frontend()
        time.sleep(3)
        
        # 브라우저 열기
        open_browser()
        
        # 접속 정보 출력
        print_access_info()
        
        print("\n🔄 서버 실행 중... (Ctrl+C로 종료)")
        
        # 메인 루프
        while True:
            time.sleep(1)
            
            # 프로세스 상태 확인
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend 서버가 예기치 않게 종료되었습니다.")
                break
                
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend 서버가 예기치 않게 종료되었습니다.")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 서버 종료 중...")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        
    finally:
        # 프로세스 정리
        print("🧹 프로세스 정리 중...")
        
        if backend_process:
            try:
                os.killpg(os.getpgid(backend_process.pid), signal.SIGTERM)
                backend_process.wait(timeout=5)
                print("✅ Backend 서버 종료됨")
            except:
                print("⚠️  Backend 서버 강제 종료")
                
        if frontend_process:
            try:
                os.killpg(os.getpgid(frontend_process.pid), signal.SIGTERM)
                frontend_process.wait(timeout=5)
                print("✅ Frontend 서버 종료됨")
            except:
                print("⚠️  Frontend 서버 강제 종료")
        
        print("🎉 모든 서버가 종료되었습니다.")

if __name__ == "__main__":
    sys.exit(main())
