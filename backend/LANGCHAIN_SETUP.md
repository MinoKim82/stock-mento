# LangChain AI 챗봇 설정 가이드

## 📋 목차
1. [개요](#개요)
2. [설치 방법](#설치-방법)
3. [API 키 발급](#api-키-발급)
4. [환경 설정](#환경-설정)
5. [사용 방법](#사용-방법)
6. [API 엔드포인트](#api-엔드포인트)
7. [프론트엔드 통합](#프론트엔드-통합)

## 개요

이 프로젝트는 LangChain을 활용하여 포트폴리오 분석 AI 챗봇을 제공합니다.
- **지원 AI**: Google Gemini, OpenAI GPT
- **주요 기능**: 포트폴리오 분석, 투자 조언, 대화형 인터페이스

## 설치 방법

### 1. 필요한 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

또는 개별 설치:

```bash
pip install langchain langchain-openai langchain-google-genai python-dotenv
```

## API 키 발급

### Google Gemini API 키 발급 (무료)

1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. API 키 복사

### OpenAI API 키 발급 (유료)

1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. "Create new secret key" 클릭
3. API 키 복사

## 환경 설정

### 1. .env 파일 생성

`backend/.env` 파일을 생성하고 다음 내용을 추가:

```bash
# Google Gemini 사용 (권장 - 무료)
GOOGLE_API_KEY=your_google_api_key_here
AI_PROVIDER=gemini

# 또는 OpenAI 사용
# OPENAI_API_KEY=your_openai_api_key_here
# AI_PROVIDER=openai
```

### 2. 서버 재시작

```bash
# 백엔드 디렉토리에서
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 LangChain 서비스가 자동으로 로드됩니다.

## 사용 방법

### Python 코드에서 사용

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

# ChatService 초기화
chat = PortfolioAnalysisChat(
    portfolio_data=portfolio_data,
    provider="gemini"  # 또는 "openai"
)

# 채팅
response = chat.chat("제 포트폴리오를 분석해주세요")
print(response)
```

### 테스트 실행

```bash
cd backend/langchain_service
python test_chat.py
```

## API 엔드포인트

### 1. POST /chat
기본 채팅 엔드포인트

**요청:**
```json
{
  "message": "포트폴리오를 분석해주세요",
  "provider": "gemini"  // 선택사항
}
```

**응답:**
```json
{
  "response": "AI 응답 내용...",
  "history": [
    {
      "role": "user",
      "content": "포트폴리오를 분석해주세요"
    },
    {
      "role": "assistant",
      "content": "AI 응답 내용..."
    }
  ]
}
```

### 2. POST /chat/stream
스트리밍 채팅 (실시간 응답)

**요청:**
```json
{
  "message": "투자 전략을 알려주세요",
  "provider": "gemini"
}
```

**응답:** 텍스트 스트림

### 3. POST /chat/analyze
포트폴리오 전체 분석

**응답:**
```json
{
  "analysis": "포트폴리오 분석 결과...",
  "history": [...]
}
```

### 4. GET /chat/history
대화 히스토리 조회

**응답:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ]
}
```

### 5. DELETE /chat/history
대화 히스토리 초기화

**응답:**
```json
{
  "message": "채팅 히스토리가 초기화되었습니다."
}
```

### 6. POST /chat/update-portfolio
포트폴리오 데이터 업데이트

**응답:**
```json
{
  "message": "포트폴리오 데이터가 업데이트되었습니다."
}
```

## 프론트엔드 통합

### React/TypeScript 예제

```typescript
// API 클라이언트
async function sendMessage(message: string) {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      provider: 'gemini'
    })
  });
  
  const data = await response.json();
  return data;
}

// 사용 예시
const result = await sendMessage("제 포트폴리오를 분석해주세요");
console.log(result.response);
```

### 스트리밍 예제

```typescript
async function streamMessage(message: string) {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      provider: 'gemini'
    })
  });
  
  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  
  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    console.log(chunk); // 실시간 출력
  }
}
```

## 주의사항

1. **API 키 보안**
   - `.env` 파일은 절대 Git에 커밋하지 마세요
   - `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

2. **비용 관리**
   - Gemini: 무료 (일일 제한 있음)
   - OpenAI: 유료 (토큰당 과금)

3. **투자 조언**
   - AI의 응답은 참고용이며, 실제 투자 결정은 사용자의 책임입니다
   - 모든 응답에 면책 조항이 포함됩니다

## 문제 해결

### LangChain 서비스를 사용할 수 없습니다

```bash
pip install langchain langchain-openai langchain-google-genai python-dotenv
```

### API 키 오류

1. `.env` 파일이 `backend/` 디렉토리에 있는지 확인
2. API 키가 올바른지 확인
3. `AI_PROVIDER`가 올바르게 설정되었는지 확인

### 서버 오류

1. 로그 확인: 터미널에서 오류 메시지 확인
2. 패키지 버전 확인: `pip list | grep langchain`
3. 환경 변수 확인: `python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"`

## 참고 자료

- [LangChain 문서](https://python.langchain.com/)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/docs)
