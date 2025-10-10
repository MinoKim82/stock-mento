"""
LangChain ChatService 테스트 스크립트
"""
import asyncio
from chat_service import ChatService, PortfolioAnalysisChat

def test_basic_chat():
    """기본 채팅 테스트"""
    print("=" * 50)
    print("1. 기본 채팅 테스트")
    print("=" * 50)
    
    try:
        chat = ChatService(provider="gemini")
        
        # 첫 번째 메시지
        response1 = chat.chat("안녕하세요!")
        print(f"User: 안녕하세요!")
        print(f"AI: {response1}\n")
        
        # 두 번째 메시지
        response2 = chat.chat("포트폴리오 투자에 대해 조언해주세요.")
        print(f"User: 포트폴리오 투자에 대해 조언해주세요.")
        print(f"AI: {response2}\n")
        
        # 히스토리 확인
        print("대화 히스토리:")
        for msg in chat.get_history():
            print(f"  {msg['role']}: {msg['content'][:50]}...")
        
        print("\n✅ 기본 채팅 테스트 성공!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 기본 채팅 테스트 실패: {str(e)}\n")
        return False

async def test_async_chat():
    """비동기 채팅 테스트"""
    print("=" * 50)
    print("2. 비동기 채팅 테스트")
    print("=" * 50)
    
    try:
        chat = ChatService(provider="gemini")
        
        # 비동기 메시지
        response = await chat.achat("주식 투자 초보자를 위한 조언을 해주세요.")
        print(f"User: 주식 투자 초보자를 위한 조언을 해주세요.")
        print(f"AI: {response}\n")
        
        print("✅ 비동기 채팅 테스트 성공!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 비동기 채팅 테스트 실패: {str(e)}\n")
        return False

async def test_streaming_chat():
    """스트리밍 채팅 테스트"""
    print("=" * 50)
    print("3. 스트리밍 채팅 테스트")
    print("=" * 50)
    
    try:
        chat = ChatService(provider="gemini")
        
        print(f"User: 분산 투자의 장점은 무엇인가요?")
        print(f"AI: ", end="", flush=True)
        
        async for chunk in chat.stream_chat("분산 투자의 장점은 무엇인가요?"):
            print(chunk, end="", flush=True)
        
        print("\n\n✅ 스트리밍 채팅 테스트 성공!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 스트리밍 채팅 테스트 실패: {str(e)}\n")
        return False

def test_portfolio_chat():
    """포트폴리오 분석 채팅 테스트"""
    print("=" * 50)
    print("4. 포트폴리오 분석 채팅 테스트")
    print("=" * 50)
    
    try:
        # 샘플 포트폴리오 데이터
        portfolio_data = {
            "portfolio_summary": {
                "total_value": 50000000,  # 5천만원
                "total_investment": 45000000,  # 4천 5백만원
                "total_gain_loss": 5000000,  # 500만원
                "total_gain_loss_rate": 11.11  # 11.11%
            }
        }
        
        chat = PortfolioAnalysisChat(
            portfolio_data=portfolio_data,
            provider="gemini"
        )
        
        # 포트폴리오 질문
        response = chat.chat("제 포트폴리오 수익률이 괜찮은 편인가요?")
        print(f"User: 제 포트폴리오 수익률이 괜찮은 편인가요?")
        print(f"AI: {response}\n")
        
        print("✅ 포트폴리오 분석 채팅 테스트 성공!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ 포트폴리오 분석 채팅 테스트 실패: {str(e)}\n")
        return False

async def run_all_tests():
    """모든 테스트 실행"""
    print("\n🚀 LangChain ChatService 테스트 시작\n")
    
    results = []
    
    # 1. 기본 채팅 테스트
    results.append(test_basic_chat())
    
    # 2. 비동기 채팅 테스트
    results.append(await test_async_chat())
    
    # 3. 스트리밍 채팅 테스트
    results.append(await test_streaming_chat())
    
    # 4. 포트폴리오 분석 채팅 테스트
    results.append(test_portfolio_chat())
    
    # 결과 요약
    print("=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    success_count = sum(results)
    total_count = len(results)
    print(f"성공: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 모든 테스트 통과!")
    else:
        print(f"⚠️ {total_count - success_count}개 테스트 실패")
    
    print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    print("""
⚠️ 테스트를 실행하기 전에:
1. .env 파일에 API 키를 설정하세요:
   - GOOGLE_API_KEY=your_google_api_key (Gemini 사용)
   - OPENAI_API_KEY=your_openai_api_key (OpenAI 사용)
   - AI_PROVIDER=gemini 또는 openai

2. 필요한 패키지를 설치하세요:
   pip install langchain langchain-openai langchain-google-genai python-dotenv
    """)
    
    input("준비가 되었으면 Enter를 누르세요...")
    
    asyncio.run(run_all_tests())

