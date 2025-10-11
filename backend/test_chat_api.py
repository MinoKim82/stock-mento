"""
AI Chat API 테스트
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat_api():
    """채팅 API 테스트"""
    print("🧪 AI Chat API 테스트 시작\n")
    
    # 1. 서버 연결 확인
    print("1️⃣ 서버 연결 확인...")
    try:
        response = requests.get(f"{BASE_URL}/cache/info")
        print(f"✅ 서버 연결 성공: {response.status_code}")
        cache_info = response.json()
        print(f"   - 데이터 있음: {cache_info.get('has_data')}")
        print(f"   - 파싱 데이터 있음: {cache_info.get('has_parsed_data')}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("   백엔드 서버가 실행 중인지 확인하세요:")
        print("   cd backend && python -m uvicorn main:app --reload")
        return
    
    print()
    
    # 2. 채팅 API 테스트
    print("2️⃣ 채팅 API 테스트...")
    try:
        chat_request = {
            "message": "안녕하세요! 테스트 메시지입니다.",
            "provider": "gemini"
        }
        
        print(f"   요청: {chat_request['message']}")
        response = requests.post(
            f"{BASE_URL}/chat",
            json=chat_request,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 채팅 성공!")
            print(f"   AI 응답: {data.get('response')[:100]}...")
            print(f"   히스토리: {len(data.get('history', []))}개 메시지")
        else:
            print(f"❌ 채팅 실패: {response.status_code}")
            print(f"   에러: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: AI 응답 대기 시간 초과")
    except Exception as e:
        print(f"❌ 채팅 오류: {e}")
        
    print()
    
    # 3. 포트폴리오 업데이트 테스트
    print("3️⃣ 포트폴리오 데이터 업데이트 테스트...")
    try:
        response = requests.post(f"{BASE_URL}/chat/update-portfolio")
        
        if response.status_code == 200:
            print(f"✅ 업데이트 성공!")
            print(f"   메시지: {response.json().get('message')}")
        else:
            print(f"⚠️ 업데이트 실패: {response.status_code}")
            print(f"   에러: {response.json().get('detail', response.text)}")
            
    except Exception as e:
        print(f"❌ 업데이트 오류: {e}")
    
    print()
    
    # 4. 히스토리 조회 테스트
    print("4️⃣ 채팅 히스토리 조회 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/chat/history")
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print(f"✅ 히스토리 조회 성공!")
            print(f"   총 {len(history)}개 메시지")
            for i, msg in enumerate(history[-3:], 1):  # 최근 3개만 표시
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:50]
                print(f"   [{i}] {role}: {content}...")
        else:
            print(f"❌ 히스토리 조회 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 히스토리 조회 오류: {e}")
    
    print()
    print("✅ 테스트 완료!")
    print()
    print("💡 팁:")
    print("   • .env 파일에 GOOGLE_API_KEY 또는 OPENAI_API_KEY 설정")
    print("   • CSV 파일 업로드하면 포트폴리오 기반 응답 가능")
    print("   • 프론트엔드에서 채팅창 사용 가능")

if __name__ == "__main__":
    test_chat_api()

