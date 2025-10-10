"""
대화 히스토리 저장/로드 기능 테스트
"""
import asyncio
from chat_service import ChatService, PortfolioAnalysisChat

def test_auto_save():
    """자동 저장 테스트"""
    print("=" * 60)
    print("1. 자동 저장 테스트")
    print("=" * 60)
    
    # 세션 ID 지정
    session_id = "test_auto_save"
    
    # 새 세션 시작
    chat = ChatService(
        provider="gemini",
        session_id=session_id
    )
    
    print(f"세션 ID: {chat.session_id}")
    print(f"저장 경로: {chat._get_history_file_path()}")
    print()
    
    # 메시지 1
    print("User: 안녕하세요")
    response1 = chat.chat("안녕하세요")
    print(f"AI: {response1}\n")
    
    # 메시지 2
    print("User: 주식 투자 조언해주세요")
    response2 = chat.chat("주식 투자 조언해주세요")
    print(f"AI: {response2}\n")
    
    # 세션 정보
    info = chat.get_session_info()
    print("=" * 60)
    print("세션 정보:")
    print(f"  메시지 수: {info['message_count']}")
    print(f"  생성 시간: {info['created_at']}")
    print(f"  업데이트: {info['updated_at']}")
    print(f"✅ 파일 저장됨: {info['storage_path']}")
    print()

def test_session_reload():
    """세션 재로드 테스트"""
    print("=" * 60)
    print("2. 세션 재로드 테스트")
    print("=" * 60)
    
    session_id = "test_auto_save"
    
    # 기존 세션 로드
    chat = ChatService.load_session(
        session_id=session_id,
        provider="gemini"
    )
    
    print(f"✅ 세션 '{session_id}' 로드 완료")
    print(f"로드된 메시지 수: {len(chat.chat_history)}")
    print()
    
    # 이전 대화 내역 출력
    print("이전 대화 내역:")
    print("-" * 60)
    for msg in chat.get_history():
        role = msg['role'].upper()
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"[{role}] {content}")
        print()
    
    # 대화 이어가기
    print("-" * 60)
    print("User: 좀 더 자세히 설명해주세요")
    response = chat.chat("좀 더 자세히 설명해주세요")
    print(f"AI: {response}\n")
    
    # 업데이트된 세션 정보
    info = chat.get_session_info()
    print(f"✅ 메시지 수 증가: {info['message_count']}개")
    print()

def test_session_list():
    """세션 목록 조회 테스트"""
    print("=" * 60)
    print("3. 세션 목록 조회 테스트")
    print("=" * 60)
    
    # 모든 세션 목록
    sessions = ChatService.list_sessions()
    
    print(f"저장된 세션 수: {len(sessions)}")
    print()
    
    for i, session in enumerate(sessions, 1):
        print(f"{i}. 세션 ID: {session['session_id']}")
        print(f"   Provider: {session['provider']}")
        print(f"   메시지 수: {session['message_count']}")
        print(f"   생성 시간: {session['created_at']}")
        print(f"   업데이트: {session['updated_at']}")
        print()
    
    print("✅ 세션 목록 조회 완료")
    print()

def test_portfolio_session():
    """포트폴리오 분석 세션 테스트"""
    print("=" * 60)
    print("4. 포트폴리오 분석 세션 테스트")
    print("=" * 60)
    
    # 포트폴리오 데이터
    portfolio_data = {
        "portfolio_summary": {
            "total_value": 50000000,
            "total_investment": 45000000,
            "total_gain_loss": 5000000,
            "total_gain_loss_rate": 11.11
        }
    }
    
    # 포트폴리오 분석 세션
    chat = PortfolioAnalysisChat(
        portfolio_data=portfolio_data,
        provider="gemini",
        session_id="test_portfolio"
    )
    
    print(f"세션 ID: {chat.session_id}")
    print()
    
    # 포트폴리오 질문
    print("User: 제 포트폴리오 수익률이 괜찮은가요?")
    response = chat.chat("제 포트폴리오 수익률이 괜찮은가요?")
    print(f"AI: {response}\n")
    
    print("✅ 포트폴리오 세션 저장 완료")
    print()

def test_clear_history():
    """히스토리 초기화 테스트"""
    print("=" * 60)
    print("5. 히스토리 초기화 테스트")
    print("=" * 60)
    
    session_id = "test_clear"
    
    # 새 세션 생성
    chat = ChatService(
        provider="gemini",
        session_id=session_id
    )
    
    # 메시지 추가
    chat.chat("테스트 메시지 1")
    chat.chat("테스트 메시지 2")
    
    print(f"초기화 전 메시지 수: {len(chat.chat_history)}")
    
    # 히스토리 초기화
    chat.clear_history()
    
    print(f"초기화 후 메시지 수: {len(chat.chat_history)}")
    print("✅ 히스토리 초기화 완료")
    print()

def run_all_tests():
    """모든 테스트 실행"""
    print("\n🚀 대화 히스토리 저장/로드 기능 테스트 시작\n")
    
    try:
        # 1. 자동 저장
        test_auto_save()
        
        # 2. 세션 재로드
        test_session_reload()
        
        # 3. 세션 목록
        test_session_list()
        
        # 4. 포트폴리오 세션
        test_portfolio_session()
        
        # 5. 히스토리 초기화
        test_clear_history()
        
        print("=" * 60)
        print("🎉 모든 테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("""
⚠️ 테스트를 실행하기 전에:
1. .env 파일에 API 키를 설정하세요:
   - GOOGLE_API_KEY=your_google_api_key (Gemini 사용)
   - AI_PROVIDER=gemini

2. backend/chat_history/ 디렉토리를 확인하여
   테스트 후 생성된 파일들을 확인하세요.
    """)
    
    input("준비가 되었으면 Enter를 누르세요...")
    
    run_all_tests()
    
    print("\n📁 생성된 파일 확인:")
    print("   backend/chat_history/ 디렉토리를 확인하세요")
    print("   각 세션마다 JSON 파일이 생성되어 있습니다.\n")

