# Backend API Documentation

포트폴리오 분석을 위한 FastAPI 백엔드 서버입니다.

## 🚀 시작하기

### 1. 환경 설정
```bash
cd backend
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python main_memory.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 3. API 문서
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📋 API 엔드포인트

### 기본 엔드포인트
- `GET /` - 서버 상태 확인
- `GET /health` - 헬스 체크

### CSV 업로드 및 관리
- `POST /upload-csv` - CSV 파일 업로드
- `GET /cache/info` - 캐시 정보 조회
- `DELETE /cache/clear` - 전체 캐시 삭제
- `DELETE /cache/{session_id}` - 특정 세션 캐시 삭제

### 포트폴리오 분석
- `GET /portfolio/summary/{session_id}` - 포트폴리오 요약
- `GET /portfolio/performance/{session_id}` - 포트폴리오 성과 분석
- `GET /portfolio/risk/{session_id}` - 포트폴리오 위험 분석

### 필터링 기능
- `GET /portfolio/filters/{session_id}` - 필터 옵션 조회
- `GET /portfolio/summary-filtered/{session_id}` - 필터링된 포트폴리오 요약
- `GET /portfolio/performance-filtered/{session_id}` - 필터링된 포트폴리오 성과

### 상세 정보
- `GET /portfolio/accounts-detailed/{session_id}` - 계좌별 상세 정보
- `GET /transactions/{session_id}` - 전체 거래 내역

## 📊 데이터 구조

### CSV 파일 형식
```
Date,Type,Security,Shares,Quote,Amount,Fees,Taxes,Net Transaction Value,Cash Account,Offset Account,Note,Source
```

### 계좌명 구조
```
{소유자} {증권사} {계좌타입} 예수금
예: "민호 토스 종합매매 해외 예수금"
```

## 🔐 환경 변수 설정

`.env` 파일을 백엔드 디렉토리에 생성하여 다음 설정을 추가하세요:

```env
# KIS API 설정 (한국 주식 실시간 가격)
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCESS_TOKEN=your_access_token

# Yahoo Finance API 설정 (전 세계 주식 가격)
YAHOO_API_KEY=your_api_key
```

## 🛠️ 개발 정보

### 의존성
- **FastAPI**: 웹 프레임워크
- **Pandas**: 데이터 분석
- **Uvicorn**: ASGI 서버
- **python-dotenv**: 환경 변수 관리
- **yfinance**: Yahoo Finance API 클라이언트

### 포트 설정
- 기본 포트: `8000`
- 포트 충돌 시 자동으로 다른 포트 사용

### 프로젝트 구조
```
backend/
├── main_memory.py          # 메인 서버 파일
├── pp/
│   └── transaction_parser.py  # 거래 데이터 파서
├── kis/                   # KIS API 모듈
├── yahoo/                 # Yahoo Finance API 모듈
├── requirements.txt       # Python 의존성
└── .env                   # 환경 변수 (생성 필요)
```

## 🚨 주의사항

1. **CSV 파일 크기**: 대용량 파일의 경우 메모리 사용량이 증가할 수 있습니다.
2. **세션 관리**: 서버 재시작 시 모든 캐시가 초기화됩니다.
3. **API 제한**: Yahoo Finance API는 일일 요청 제한이 있을 수 있습니다.
4. **포트 충돌**: 기본 포트 8000 사용, 충돌 시 자동으로 다른 포트 사용

## 🔍 문제 해결

### 포트 충돌
```bash
# 포트 8000을 사용하는 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### 메모리 부족
- 캐시 삭제 API 사용
- 서버 재시작
- 대용량 CSV 파일 분할

### API 오류
- 환경 변수 확인
- 네트워크 연결 상태 확인
- API 키 유효성 검증

## 🔧 주요 기능

### 1. 메모리 캐싱
- 업로드된 CSV 파일을 메모리에 저장
- 세션별 데이터 관리
- 임시 파일 자동 정리

### 2. 실시간 가격 조회
- **KIS API**: 한국 주식 실시간 가격 ('.KS' 종목)
- **Yahoo Finance API**: 전 세계 주식 가격
- 가격 캐싱으로 성능 최적화

### 3. 포트폴리오 분석
- 자산 배분 분석
- 수익률 계산
- 위험 지표 분석
- 계좌별 성과 분석

### 4. 필터링 시스템
- 소유자별 필터링 (혜란, 유신, 민호)
- 증권사별 필터링 (키움, 토스, NH, 신한)
- 계좌타입별 필터링 (연금저축, ISA, 종합매매, 종합매매 해외)
