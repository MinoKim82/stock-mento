# Frontend - Portfolio Analysis Dashboard

포트폴리오 분석을 위한 React + TypeScript + Vite 기반 프론트엔드 애플리케이션입니다.

## 🚀 시작하기

### 1. 의존성 설치
```bash
cd frontend
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

애플리케이션이 `http://localhost:5173`에서 실행됩니다.

### 3. 빌드
```bash
npm run build
```

### 4. 미리보기
```bash
npm run preview
```

## 🏗️ 프로젝트 구조

```
frontend/
├── src/
│   ├── components/          # React 컴포넌트
│   │   ├── FileUpload.tsx   # CSV 파일 업로드
│   │   ├── PortfolioSummary.tsx  # 포트폴리오 요약
│   │   ├── PortfolioPerformance.tsx  # 포트폴리오 성과
│   │   ├── PortfolioRisk.tsx  # 포트폴리오 위험 분석
│   │   ├── AccountPortfolio.tsx  # 계좌별 포트폴리오
│   │   ├── TransactionHistory.tsx  # 거래 내역
│   │   └── SessionInfo.tsx  # 세션 정보
│   ├── hooks/              # 커스텀 훅
│   │   └── usePortfolio.ts  # 포트폴리오 데이터 관리
│   ├── api/                # API 클라이언트
│   │   └── client.ts       # Axios 설정 및 API 호출
│   ├── types/              # TypeScript 타입 정의
│   │   └── index.ts        # 모든 타입 정의
│   ├── App.tsx             # 메인 앱 컴포넌트
│   ├── main.tsx            # 앱 진입점
│   └── index.css           # 글로벌 스타일
├── public/                 # 정적 파일
├── package.json            # 의존성 및 스크립트
├── vite.config.ts          # Vite 설정
├── tailwind.config.js      # Tailwind CSS 설정
├── postcss.config.js       # PostCSS 설정
└── tsconfig.json           # TypeScript 설정
```

## 🛠️ 기술 스택

### 핵심 프레임워크
- **React 18**: 사용자 인터페이스 라이브러리
- **TypeScript**: 타입 안전성
- **Vite**: 빠른 개발 서버 및 빌드 도구

### 스타일링
- **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
- **Lucide React**: 아이콘 라이브러리

### HTTP 클라이언트
- **Axios**: Promise 기반 HTTP 클라이언트

### 개발 도구
- **ESLint**: 코드 품질 관리
- **Prettier**: 코드 포맷팅 (선택사항)

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

### 🎨 사용자 인터페이스
- **반응형 디자인**: 모바일/데스크톱 지원
- **계층적 레이아웃**: 직관적인 정보 구조
- **실시간 업데이트**: 데이터 변경 시 자동 새로고침
- **드래그 앤 드롭**: CSV 파일 업로드

## 🔧 개발 가이드

### 컴포넌트 구조
```typescript
// 예시: PortfolioSummary 컴포넌트
interface PortfolioSummaryProps {
  data: PortfolioSummary;
}

const PortfolioSummary: React.FC<PortfolioSummaryProps> = ({ data }) => {
  // 컴포넌트 로직
};
```

### API 호출
```typescript
// usePortfolio 훅 사용
const { portfolioSummary, loadPortfolioSummary } = usePortfolio();

useEffect(() => {
  if (sessionId) {
    loadPortfolioSummary(sessionId);
  }
}, [sessionId, loadPortfolioSummary]);
```

### 스타일링
```typescript
// Tailwind CSS 클래스 사용
<div className="bg-white rounded-lg shadow-md p-6">
  <h2 className="text-xl font-semibold text-gray-900 mb-4">
    포트폴리오 요약
  </h2>
</div>
```

## 📋 스크립트

- `npm run dev`: 개발 서버 시작
- `npm run build`: 프로덕션 빌드
- `npm run preview`: 빌드된 앱 미리보기
- `npm run lint`: ESLint 검사

## 🔗 API 연동

프론트엔드는 백엔드 API와 다음과 같이 연동됩니다:

- **Base URL**: `http://localhost:8000`
- **CSV 업로드**: `POST /upload-csv`
- **포트폴리오 데이터**: `GET /portfolio/*`
- **거래 내역**: `GET /transactions/*`

자세한 API 문서는 [../backend/README.md](../backend/README.md)를 참조하세요.

## 🚨 주의사항

1. **백엔드 서버**: 프론트엔드 실행 전 백엔드 서버가 실행되어야 합니다.
2. **CORS**: 개발 환경에서 CORS 설정이 필요할 수 있습니다.
3. **포트 충돌**: 기본 포트 5173 사용, 충돌 시 다른 포트 사용

## 🔍 문제 해결

### 포트 충돌
```bash
# 포트 5173을 사용하는 프로세스 확인
lsof -i :5173

# 프로세스 종료
kill -9 <PID>
```

### 의존성 문제
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

### 빌드 오류
- TypeScript 타입 오류 확인
- ESLint 규칙 확인
- Tailwind CSS 클래스명 확인

## 📚 관련 문서

- **[../README.md](../README.md)**: 전체 프로젝트 문서
- **[../backend/README.md](../backend/README.md)**: 백엔드 API 문서
- **[Vite 공식 문서](https://vitejs.dev/)**: Vite 사용법
- **[React 공식 문서](https://react.dev/)**: React 사용법
- **[Tailwind CSS 문서](https://tailwindcss.com/)**: 스타일링 가이드
