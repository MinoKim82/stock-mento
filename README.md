# Stock Portfolio Analysis Dashboard

주식 포트폴리오 분석을 위한 현대적인 웹 기반 대시보드입니다. CSV 파일을 업로드하여 실시간 포트폴리오 분석을 제공합니다.

## 🚀 빠른 시작

### 1. 통합 실행 (권장)
```bash
python start_servers_react.py
```

### 2. 개별 실행
```bash
# Backend 서버
cd backend && python main.py

# Frontend 서버 (별도 터미널)
cd frontend && npm run dev
```

### 3. 대시보드 접속
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`
- **API 문서**: `http://localhost:8000/docs`

### 4. CSV 파일 업로드
- 드래그 앤 드롭 또는 파일 선택으로 CSV 업로드
- 디스크에 저장되어 서버 재시작 후에도 유지됨
- 자동으로 포트폴리오 분석 결과 표시

## 🏗️ 프로젝트 구조

```
stock-mento/
├── backend/                 # FastAPI 백엔드 서버
│   ├── main.py             # 메인 서버 파일
│   ├── pp/                 # 거래 데이터 파서
│   ├── kis/                # KIS API 모듈
│   ├── yahoo/              # Yahoo Finance API 모듈
│   ├── csv_data/           # 업로드된 CSV 파일 저장소
│   └── README.md           # 백엔드 상세 문서
├── frontend/               # React + TypeScript 프론트엔드
│   ├── src/
│   │   ├── components/     # React 컴포넌트
│   │   ├── hooks/          # 커스텀 훅
│   │   ├── api/            # API 클라이언트
│   │   └── types/          # TypeScript 타입 정의
│   ├── package.json
│   └── README.md           # 프론트엔드 개발 문서
├── start_servers_react.py  # 통합 서버 시작 스크립트
└── README.md               # 메인 프로젝트 문서
```

## 📊 주요 기능

### 🎯 포트폴리오 분석
- **포트폴리오 요약**: 총 자산, 현금/주식 비율, 수익률
- **계좌별 포트폴리오**: 소유자별, 계좌타입별 계층적 구조
- **현재 연도 수익**: 연도별 투자 성과 분석
- **전체 거래 내역**: 모든 거래 내역 조회 및 페이지네이션

### 🔍 필터링 시스템
- **소유자별 필터**: 혜란, 유신, 민호
- **증권사별 필터**: 키움, 토스, NH, 신한
- **계좌타입별 필터**: 연금저축, ISA, 종합매매, 종합매매 해외

### 📈 실시간 데이터
- **KIS API**: 한국 주식 실시간 가격 조회
- **Yahoo Finance API**: 전 세계 주식 가격 조회
- **가격 캐싱**: 성능 최적화를 위한 가격 데이터 캐싱

### 💾 데이터 관리
- **메모리 캐싱**: CSV 파일을 메모리에 저장하여 빠른 처리
- **세션 관리**: 여러 사용자 동시 사용 지원
- **캐시 관리**: 메모리 사용량 모니터링 및 캐시 삭제

### 🎨 현대적 UI/UX
- **React 18 + TypeScript**: 타입 안전성과 현대적 개발 경험
- **Tailwind CSS**: 유틸리티 우선 스타일링
- **Lucide React**: 일관된 아이콘 시스템
- **반응형 디자인**: 모바일/데스크톱 지원
- **계층적 레이아웃**: 직관적인 정보 구조

## 🛠️ 기술 스택

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **Pandas**: 데이터 분석 및 처리
- **Uvicorn**: ASGI 서버
- **python-dotenv**: 환경 변수 관리

### Frontend
- **React 18**: 사용자 인터페이스 라이브러리
- **TypeScript**: 타입 안전성
- **Vite**: 빠른 개발 서버 및 빌드 도구
- **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
- **Lucide React**: 아이콘 라이브러리
- **Axios**: HTTP 클라이언트

## 📋 요구사항

### 시스템 요구사항
- **Node.js**: 16.0.0 이상
- **Python**: 3.8 이상
- **메모리**: 최소 4GB (대용량 CSV 파일 처리 시)

### 의존성 설치
```bash
# Backend 의존성
cd backend && pip install -r requirements.txt

# Frontend 의존성
cd frontend && npm install
```

## 🔧 환경 설정

### 환경 변수 (선택사항)
`.env` 파일을 백엔드 디렉토리에 생성:

```env
# KIS API 설정 (한국 주식 실시간 가격)
KIS_APP_KEY=your_app_key
KIS_APP_SECRET=your_app_secret
KIS_ACCESS_TOKEN=your_access_token

# Yahoo Finance API 설정 (전 세계 주식 가격)
YAHOO_API_KEY=your_api_key
```

## 📚 상세 문서

- **[backend/README.md](backend/README.md)**: 백엔드 API 상세 문서
- **[frontend/README.md](frontend/README.md)**: 프론트엔드 개발 문서
- **[start_servers_react.py](start_servers_react.py)**: 통합 서버 시작 스크립트

## 🚨 전체 프로젝트 주의사항

1. **포트 충돌**: 기본 포트 8000(백엔드), 5173(프론트엔드) 사용
2. **메모리 사용량**: 대용량 CSV 파일 처리 시 메모리 사용량 증가
3. **API 제한**: Yahoo Finance API는 일일 요청 제한이 있을 수 있음
4. **세션 관리**: 서버 재시작 시 모든 캐시가 초기화됨

## 🔍 전체 프로젝트 문제 해결

### 포트 충돌 해결
```bash
# 포트 사용 프로세스 확인
lsof -i :8000  # 백엔드
lsof -i :5173  # 프론트엔드

# 프로세스 종료
kill -9 <PID>
```

### 메모리 부족 해결
- 캐시 삭제 API 사용
- 서버 재시작
- 대용량 CSV 파일 분할

## 📈 향후 계획

- [ ] LLM 연동을 통한 포트폴리오 분석 및 조언
- [ ] 실시간 알림 시스템
- [ ] 데이터 내보내기 기능
- [ ] 다국어 지원
- [ ] 모바일 앱 개발
