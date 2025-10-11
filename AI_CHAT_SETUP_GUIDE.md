# 🤖 AI 챗봇 설정 가이드

## 📋 개요

"세션을 찾을 수 없습니다" 오류를 해결하고, CSV 파일 대신 마크다운 문서 기반으로 AI 챗봇이 동작하도록 구현했습니다.

## 🔍 발견된 문제

### 1. Import 오류
- `backend/langchain_service/__init__.py`에 `PortfolioAnalysisChat` export 누락
- 서버 시작 시 `LANGCHAIN_AVAILABLE = False`로 설정됨
- 모든 `/chat/*` 엔드포인트가 404 반환

### 2. 에러 메시지 불명확
- 프론트엔드가 모든 404를 "세션을 찾을 수 없습니다"로 변환
- 실제 오류 원인 파악 어려움

### 3. API 키 설정 필요
- Gemini API 키가 설정되지 않으면 모델 오류 발생

## ✅ 해결 완료

### 1. Import 수정
```python
# backend/langchain_service/__init__.py
from .chat_service import ChatService, Message, PortfolioAnalysisChat

__all__ = ["ChatService", "Message", "PortfolioAnalysisChat"]
```

### 2. 에러 핸들링 개선
```typescript
// frontend/src/api/client.ts
const detailMessage = error.response?.data?.detail;
if (detailMessage) {
  throw new Error(detailMessage);  // 백엔드 메시지 우선 사용
}
```

### 3. 디버깅 로그 추가
```python
# backend/main.py
print(f"✅ 포트폴리오 데이터 로드 완료: {PARSED_DATA_FILE}")
print(f"🤖 ChatService 초기화: provider={provider}")
print(f"💬 사용자 메시지: {request.message[:50]}...")
```

### 4. 마크다운 문서 생성
- `portfolio_document.py`: JSON → 마크다운 변환
- `PortfolioAnalysisChat`: 마크다운을 LangChain Document로 로드
- 시스템 프롬프트에 포트폴리오 전체 데이터 포함 (최대 10,000자)

## 🚀 설정 방법

### 1단계: API 키 설정

#### Google Gemini 사용 (추천)
```bash
cd backend
cat > .env << 'EOF'
GOOGLE_API_KEY=your_google_api_key_here
AI_PROVIDER=gemini
EOF
```

**API 키 받기**: https://makersuite.google.com/app/apikey

#### OpenAI 사용
```bash
cd backend
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your_openai_api_key_here
AI_PROVIDER=openai
EOF
```

**API 키 받기**: https://platform.openai.com/api-keys

### 2단계: 패키지 설치

```bash
cd backend
pip install langchain langchain-openai langchain-google-genai langchain-community python-dotenv
```

### 3단계: 서버 시작

```bash
# 기존 서버 종료
pkill -f 'uvicorn main:app'

# 서버 재시작
cd backend
python -m uvicorn main:app --reload
```

### 4단계: 테스트

```bash
# API 테스트
python backend/test_chat_api.py

# 마크다운 생성 테스트
python backend/test_portfolio_markdown.py
```

## 🧪 테스트 결과 예시

### 성공 시:
```
✅ 서버 연결 성공: 200
✅ 채팅 성공!
   AI 응답: 안녕하세요! 포트폴리오 분석 도우미입니다...
✅ 업데이트 성공!
✅ 히스토리 조회 성공!
```

### API 키 미설정 시:
```
❌ 채팅 실패: 500
   에러: Gemini 모델 오류: 'gemini-1.5-flash is not found'
```
→ `.env` 파일에 API 키 추가 필요

## 💬 사용 방법

### 프론트엔드에서

1. CSV 파일 업로드
2. 대화창에서 질문:
   - "제 포트폴리오 수익률이 어때요?"
   - "어떤 종목이 가장 잘 나가고 있어?"
   - "민호와 유신의 투자 전략 비교해줘"
3. ✨ "전체 분석" 버튼으로 포트폴리오 종합 분석

### API 직접 호출

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "제 포트폴리오 분석해줘",
    "provider": "gemini"
  }'
```

## 🎯 작동 원리

### 1. CSV 업로드 → 마크다운 생성
```
CSV 파일
  ↓
parsed_data/portfolio_data.json
  ↓
portfolio_document.py
  ↓
portfolio_docs/portfolio_20251011.md
  ↓
LangChain Document 객체
```

### 2. AI 대화
```
사용자 질문
  ↓
PortfolioAnalysisChat
  ↓
시스템 프롬프트 (마크다운 포함)
  ↓
Gemini/OpenAI API
  ↓
AI 응답 (포트폴리오 데이터 기반)
```

### 3. 히스토리 저장
```
모든 대화
  ↓
backend/chat_history/chat_{session_id}.json
  ↓
서버 재시작 후에도 유지
```

## 📂 생성된 파일 구조

```
backend/
├── .env                           # API 키 설정
├── langchain_service/
│   ├── __init__.py               # ✅ PortfolioAnalysisChat export 추가
│   ├── chat_service.py           # ✅ Document Loader 통합
│   └── portfolio_document.py     # 🆕 마크다운 생성기
├── portfolio_docs/               # 🆕 생성된 마크다운 저장
│   └── portfolio_20251011.md
├── chat_history/                 # 대화 히스토리 저장
│   └── chat_default.json
├── test_chat_api.py             # 🆕 API 테스트 스크립트
└── test_portfolio_markdown.py   # 🆕 마크다운 테스트 스크립트

frontend/
└── src/
    └── api/
        └── client.ts             # ✅ 에러 핸들링 개선
```

## 🐛 트러블슈팅

### 문제: "세션을 찾을 수 없습니다"
**원인**: Import 오류로 `/chat` 엔드포인트가 등록되지 않음  
**해결**: `__init__.py`에 `PortfolioAnalysisChat` 추가 (완료)

### 문제: "Gemini 모델을 찾을 수 없습니다"
**원인**: API 키 미설정 또는 잘못된 모델명  
**해결**: `.env` 파일에 `GOOGLE_API_KEY` 설정

### 문제: "LangChain 서비스를 사용할 수 없습니다"
**원인**: 패키지 미설치  
**해결**: `pip install langchain langchain-openai langchain-google-genai langchain-community`

### 문제: 서버 응답이 느림
**원인**: AI API 응답 대기 시간  
**정상**: 첫 응답까지 3-10초 소요 (Gemini 기준)

## 📊 마크다운 문서 예시

```markdown
# 📊 포트폴리오 분석 리포트

## 1. 💼 포트폴리오 요약
- 총 평가액: ₩180,715,715
- 총 투자금: ₩122,917,159
- 총 손익: ₩57,798,556 (47.03%)

### 소유자별 현황
#### 민호
- 평가액: ₩107,211,851
- 투자금: ₩74,091,157
- 손익: ₩33,120,694 (44.70%)

## 2. 🏦 계좌별 포트폴리오
### 민호의 계좌
#### 연금저축
**NH 연금저축**
- 잔액: ₩77,889
- 투자금: ₩52,180,555
- 보유 종목:
  - ACE 미국나스닥100: 1,506주 (₩41,061,090)
  - ACE 미국S&P500: 1,680주 (₩40,462,800)

## 3. 💰 수익 분석
#### 2024년
- 총 수익: ₩15,234,567
  - 배당금: ₩1,234,567
  - 매도 수익: ₩14,000,000
```

## 🎉 완료!

이제 프론트엔드 대화창에서:
- ✅ AI와 실시간 대화 가능
- ✅ 포트폴리오 데이터 기반 개인화된 조언
- ✅ 대화 히스토리 자동 저장/로드
- ✅ CSV 파일 세션 오류 해결

**API 키만 설정하면 바로 사용 가능합니다!** 🚀

