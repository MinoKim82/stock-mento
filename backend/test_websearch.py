"""
웹 검색 기능 테스트
"""
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_service import PortfolioAnalysisChat

print("🧪 웹 검색 기능 테스트\n")

# ChatService 초기화
print("1️⃣ ChatService 초기화...")
try:
    chat = PortfolioAnalysisChat(
        portfolio_data=None,
        provider="gemini"
    )
    print(f"✅ 초기화 완료")
    print(f"   search_tool: {chat.search_tool is not None}")
except Exception as e:
    print(f"❌ 초기화 실패: {e}")
    sys.exit(1)

print()

# 키워드 테스트
print("2️⃣ 키워드 감지 테스트...")
test_messages = [
    "오늘 코스피 지수는?",
    "삼성전자 최신 뉴스",
    "반도체 업종 동향",
    "포트폴리오 분석해줘"  # 검색 불필요
]

for msg in test_messages:
    should_search = chat._should_search_web(msg)
    print(f"   '{msg}' → {should_search}")

print()

# 실제 검색 테스트
print("3️⃣ 실제 웹 검색 테스트...")
try:
    query = "코스피 지수 오늘"
    print(f"   검색어: {query}")
    results = chat.search_web(query)
    print(f"   결과 길이: {len(results)}자")
    print(f"   내용 미리보기:\n   {results[:200]}...")
    print(f"\n✅ 웹 검색 작동 확인!")
except Exception as e:
    print(f"❌ 웹 검색 실패: {e}")
    import traceback
    traceback.print_exc()

