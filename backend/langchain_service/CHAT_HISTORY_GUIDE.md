# 💾 대화 내역 저장 및 관리 가이드

LangChain 챗봇의 대화 내역을 자동으로 저장하고 불러오는 기능에 대한 설명입니다.

## 📋 목차
1. [개요](#개요)
2. [자동 저장 기능](#자동-저장-기능)
3. [세션 관리](#세션-관리)
4. [API 사용법](#api-사용법)
5. [저장 파일 구조](#저장-파일-구조)
6. [Python 코드 예제](#python-코드-예제)

---

## 개요

### 주요 기능
- ✅ **자동 저장**: 모든 대화가 자동으로 JSON 파일에 저장됨
- ✅ **세션 관리**: 세션 ID로 대화 구분
- ✅ **타임스탬프**: 모든 메시지에 시간 기록
- ✅ **영구 보존**: 서버 재시작 후에도 대화 유지
- ✅ **세션 목록**: 저장된 모든 대화 조회 가능
- ✅ **세션 로드**: 이전 대화 이어서 하기

### 저장 위치
```
backend/
└── chat_history/
    ├── chat_20251010_143022.json
    ├── chat_20251010_150532.json
    └── chat_custom_session.json
```

---

## 자동 저장 기능

### 1. 메시지 전송 시 자동 저장

```python
from langchain_service import ChatService

# ChatService 생성
chat = ChatService(provider="gemini")

# 첫 번째 메시지
response1 = chat.chat("안녕하세요")
# → 자동으로 backend/chat_history/chat_YYYYMMDD_HHMMSS.json에 저장됨

# 두 번째 메시지
response2 = chat.chat("포트폴리오 분석해줘")
# → 같은 파일에 추가로 저장됨
```

### 2. 세션 ID 지정

```python
# 세션 ID를 직접 지정
chat = ChatService(
    provider="gemini",
    session_id="my_portfolio_chat"
)
# → backend/chat_history/chat_my_portfolio_chat.json에 저장됨
```

### 3. 저장 디렉토리 변경

```python
# 저장 위치 커스터마이징
chat = ChatService(
    provider="gemini",
    storage_dir="/custom/path/to/chat_history"
)
```

---

## 세션 관리

### 1. 새 세션 시작

```python
# 자동 세션 ID (현재 시간 기반)
chat = ChatService(provider="gemini")
# session_id: "20251010_143022"

# 커스텀 세션 ID
chat = ChatService(
    provider="gemini",
    session_id="portfolio_analysis_2025"
)
```

### 2. 기존 세션 로드

```python
# 이전 대화 이어서 하기
chat = ChatService.load_session(
    session_id="20251010_143022",
    provider="gemini"
)

# 이전 대화 내역이 자동으로 로드됨
print(f"로드된 메시지 수: {len(chat.chat_history)}")

# 대화 이어가기
response = chat.chat("아까 얘기한 그 종목 다시 설명해줘")
# AI가 이전 대화를 기억하고 있음!
```

### 3. 세션 목록 조회

```python
# 저장된 모든 세션 목록
sessions = ChatService.list_sessions()

for session in sessions:
    print(f"세션 ID: {session['session_id']}")
    print(f"메시지 수: {session['message_count']}")
    print(f"마지막 업데이트: {session['updated_at']}")
    print("---")
```

### 4. 세션 정보 확인

```python
chat = ChatService(provider="gemini")

# 현재 세션 정보
info = chat.get_session_info()
print(info)
# {
#     "session_id": "20251010_143022",
#     "provider": "gemini",
#     "message_count": 4,
#     "storage_path": "/path/to/chat_20251010_143022.json",
#     "created_at": "2025-10-10T14:30:22.123456",
#     "updated_at": "2025-10-10T14:35:10.789012"
# }
```

---

## API 사용법

### 1. 일반 채팅 (자동 저장)

**요청:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "제 포트폴리오 분석해주세요"
  }'
```

**응답:**
```json
{
  "response": "현재 포트폴리오는...",
  "history": [
    {
      "role": "user",
      "content": "제 포트폴리오 분석해주세요",
      "timestamp": "2025-10-10T14:30:22.123456"
    },
    {
      "role": "assistant",
      "content": "현재 포트폴리오는...",
      "timestamp": "2025-10-10T14:30:25.654321"
    }
  ]
}
```

### 2. 세션 목록 조회

```bash
curl http://localhost:8000/chat/sessions
```

**응답:**
```json
{
  "sessions": [
    {
      "session_id": "20251010_143022",
      "provider": "gemini",
      "message_count": 6,
      "created_at": "2025-10-10T14:30:22",
      "updated_at": "2025-10-10T14:35:10",
      "file_path": "/path/to/chat_20251010_143022.json"
    }
  ]
}
```

### 3. 현재 세션 정보

```bash
curl http://localhost:8000/chat/session/info
```

### 4. 특정 세션 로드

```bash
curl -X POST http://localhost:8000/chat/session/load \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "20251010_143022"
  }'
```

**응답:**
```json
{
  "message": "세션 '20251010_143022' 로드 완료",
  "session_info": { ... },
  "history": [
    { "role": "user", "content": "...", "timestamp": "..." },
    { "role": "assistant", "content": "...", "timestamp": "..." }
  ]
}
```

### 5. 대화 히스토리 초기화

```bash
curl -X DELETE http://localhost:8000/chat/history
```

---

## 저장 파일 구조

### JSON 파일 예시

```json
{
  "session_id": "20251010_143022",
  "provider": "gemini",
  "created_at": "2025-10-10T14:30:22.123456",
  "updated_at": "2025-10-10T14:35:10.789012",
  "message_count": 4,
  "messages": [
    {
      "role": "user",
      "content": "안녕하세요",
      "timestamp": "2025-10-10T14:30:22.123456"
    },
    {
      "role": "assistant",
      "content": "안녕하세요! 포트폴리오 분석을 도와드리겠습니다.",
      "timestamp": "2025-10-10T14:30:25.654321"
    },
    {
      "role": "user",
      "content": "제 포트폴리오 수익률이 괜찮나요?",
      "timestamp": "2025-10-10T14:32:10.111111"
    },
    {
      "role": "assistant",
      "content": "현재 11.11%의 수익률은...",
      "timestamp": "2025-10-10T14:32:15.222222"
    }
  ]
}
```

---

## Python 코드 예제

### 예제 1: 기본 사용

```python
from langchain_service import ChatService

# 새 세션 시작
chat = ChatService(provider="gemini")

# 대화 1
response1 = chat.chat("안녕하세요")
print(response1)
# → 자동 저장됨

# 대화 2
response2 = chat.chat("삼성전자 주가 전망은?")
print(response2)
# → 자동 저장됨

# 세션 정보 확인
info = chat.get_session_info()
print(f"세션 ID: {info['session_id']}")
print(f"메시지 수: {info['message_count']}")
```

### 예제 2: 이전 대화 이어가기

```python
from langchain_service import ChatService

# 저장된 세션 목록 확인
sessions = ChatService.list_sessions()
print(f"저장된 세션 수: {len(sessions)}")

# 가장 최근 세션 로드
if sessions:
    latest_session = sessions[0]
    session_id = latest_session['session_id']
    
    # 세션 로드
    chat = ChatService.load_session(
        session_id=session_id,
        provider="gemini"
    )
    
    print(f"로드된 메시지 수: {len(chat.chat_history)}")
    
    # 이전 대화 내역 출력
    for msg in chat.get_history():
        print(f"[{msg['role']}] {msg['content'][:50]}...")
    
    # 대화 이어가기
    response = chat.chat("좀 더 자세히 설명해줘")
    print(response)
```

### 예제 3: 포트폴리오 분석 세션

```python
from langchain_service import PortfolioAnalysisChat

# 포트폴리오 데이터와 함께 세션 시작
portfolio_data = {
    "portfolio_summary": {
        "total_value": 50000000,
        "total_investment": 45000000,
        "total_gain_loss": 5000000,
        "total_gain_loss_rate": 11.11
    }
}

# 커스텀 세션 ID 사용
chat = PortfolioAnalysisChat(
    portfolio_data=portfolio_data,
    provider="gemini",
    session_id="portfolio_2025_Q4"
)

# 분석 요청
analysis = chat.analyze_portfolio()
print(analysis)
# → backend/chat_history/chat_portfolio_2025_Q4.json에 저장됨

# 추가 질문
advice = chat.chat("리스크를 줄이려면 어떻게 해야 하나요?")
print(advice)
# → 같은 파일에 추가 저장됨
```

### 예제 4: 세션 정리

```python
from langchain_service import ChatService
import os

# 모든 세션 확인
sessions = ChatService.list_sessions()

# 30일 이상 된 세션 삭제
from datetime import datetime, timedelta

cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()

for session in sessions:
    if session['updated_at'] < cutoff_date:
        file_path = session['file_path']
        os.remove(file_path)
        print(f"삭제됨: {session['session_id']}")
```

---

## 🎯 주요 특징

### 1. 컨텍스트 유지
AI가 이전 대화를 기억하므로 자연스러운 대화 가능:
```
User: "제 포트폴리오에 삼성전자가 있나요?"
AI: "네, 100주 보유 중이시네요."

User: "그럼 얼마나 벌었어요?"  ← AI가 "삼성전자"를 기억
AI: "삼성전자로 약 300만원의 수익을 보고 계십니다."
```

### 2. 서버 재시작 후에도 유지
```python
# 서버 재시작 전
chat = ChatService(session_id="my_session")
chat.chat("포트폴리오 분석해줘")

# 서버 재시작 후
chat = ChatService.load_session(session_id="my_session")
# 이전 대화가 그대로 유지됨!
```

### 3. 타임스탬프 자동 기록
모든 메시지에 정확한 시간이 기록되어 대화 흐름 추적 가능

---

## ⚠️ 주의사항

1. **저장 공간**: 대화가 많아지면 파일 크기 증가
2. **보안**: 민감한 정보가 포함될 수 있으므로 파일 접근 권한 관리 필요
3. **세션 관리**: 불필요한 오래된 세션은 주기적으로 삭제 권장

---

## 📚 API 엔드포인트 요약

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/chat` | 채팅 (자동 저장) |
| GET | `/chat/history` | 현재 세션 히스토리 |
| DELETE | `/chat/history` | 히스토리 초기화 |
| GET | `/chat/sessions` | 모든 세션 목록 |
| GET | `/chat/session/info` | 현재 세션 정보 |
| POST | `/chat/session/load` | 특정 세션 로드 |

---

이제 LangChain 챗봇의 모든 대화가 자동으로 저장되고, 언제든지 불러와서 이어갈 수 있습니다! 🎉

