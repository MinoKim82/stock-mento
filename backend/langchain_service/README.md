# LangChain Service

포트폴리오 분석을 위한 AI 챗봇 서비스입니다.

## 지원 AI Provider

- **OpenAI GPT**: GPT-4, GPT-4o-mini 등
- **Google Gemini**: Gemini-1.5-Flash, Gemini-1.5-Pro 등

## 설정 방법

### 1. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 설정합니다:

```bash
# OpenAI 사용 시
OPENAI_API_KEY=your_openai_api_key_here
AI_PROVIDER=openai

# 또는 Gemini 사용 시
GOOGLE_API_KEY=your_google_api_key_here
AI_PROVIDER=gemini
```

### 2. 필요한 패키지 설치

```bash
pip install langchain langchain-openai langchain-google-genai python-dotenv
```

## 사용 예시

### 기본 채팅

```python
from langchain_service import ChatService

# ChatService 초기화
chat = ChatService(provider="gemini")

# 채팅
response = chat.chat("안녕하세요!")
print(response)

# 히스토리 확인
history = chat.get_history()
```

### 포트폴리오 분석 채팅

```python
from langchain_service import PortfolioAnalysisChat

# 포트폴리오 데이터
portfolio_data = {
    "portfolio_summary": {
        "total_value": 10000000,
        "total_investment": 9000000,
        "total_gain_loss": 1000000,
        "total_gain_loss_rate": 11.11
    }
}

# PortfolioAnalysisChat 초기화
chat = PortfolioAnalysisChat(
    portfolio_data=portfolio_data,
    provider="gemini"
)

# 포트폴리오 전체 분석
analysis = chat.analyze_portfolio()
print(analysis)

# 투자 조언
advice = chat.get_investment_advice("지금 삼성전자를 사야할까요?")
print(advice)
```

### 비동기 채팅

```python
import asyncio
from langchain_service import ChatService

async def main():
    chat = ChatService(provider="gemini")
    
    # 비동기 채팅
    response = await chat.achat("포트폴리오 분석해줘")
    print(response)

asyncio.run(main())
```

### 스트리밍 채팅

```python
import asyncio
from langchain_service import ChatService

async def main():
    chat = ChatService(provider="gemini")
    
    # 스트리밍 채팅
    async for chunk in chat.stream_chat("투자 전략 알려줘"):
        print(chunk, end="", flush=True)

asyncio.run(main())
```

## API 엔드포인트 통합

`main.py`에 다음과 같이 추가하면 FastAPI와 통합할 수 있습니다:

```python
from langchain_service import ChatService, PortfolioAnalysisChat

# 전역 ChatService 인스턴스
chat_service: Optional[PortfolioAnalysisChat] = None

@app.post("/chat")
async def chat_endpoint(request: dict):
    """AI 채팅 엔드포인트"""
    global chat_service
    
    # ChatService 초기화 (처음 한 번만)
    if chat_service is None:
        portfolio_data = get_current_portfolio_data()
        chat_service = PortfolioAnalysisChat(
            portfolio_data=portfolio_data,
            provider="gemini"
        )
    
    user_message = request.get("message", "")
    response = await chat_service.achat(user_message)
    
    return {
        "response": response,
        "history": chat_service.get_history()
    }

@app.post("/chat/stream")
async def chat_stream_endpoint(request: dict):
    """스트리밍 채팅 엔드포인트"""
    global chat_service
    
    if chat_service is None:
        portfolio_data = get_current_portfolio_data()
        chat_service = PortfolioAnalysisChat(
            portfolio_data=portfolio_data,
            provider="gemini"
        )
    
    user_message = request.get("message", "")
    
    async def generate():
        async for chunk in chat_service.stream_chat(user_message):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/chat/clear")
async def clear_chat_history():
    """채팅 히스토리 초기화"""
    global chat_service
    if chat_service:
        chat_service.clear_history()
    return {"message": "Chat history cleared"}
```

## 주의사항

1. API 키는 `.env` 파일에 저장하고 절대 공개하지 마세요.
2. `.env` 파일은 `.gitignore`에 추가되어 있어야 합니다.
3. 투자 조언은 참고용이며, 실제 투자 결정은 사용자의 책임입니다.

