# 로깅 시스템 가이드

## 📁 로그 파일 위치

모든 로그 파일은 프로젝트 루트의 `log_data/` 디렉토리에 저장됩니다:

```
stock-mento/
└── log_data/
    ├── backend.log         # 백엔드 전체 로그
    ├── backend_error.log   # 백엔드 에러만
    └── backend_access.log  # API 접근 로그
```

## 🔧 Backend 로깅

### 로그 레벨
- **DEBUG**: 상세한 디버깅 정보
- **INFO**: 일반 정보성 메시지
- **WARNING**: 경고 메시지
- **ERROR**: 에러 메시지

### 로그 포맷
```
YYYY-MM-DD HH:MM:SS | LEVEL | module | function:line | message
```

예시:
```
2025-10-12 00:50:55 | INFO | backend | startup_event:1479 | 📂 CSV 파일 로드 중...
```

### 로그 파일 관리
- **최대 파일 크기**: 10MB
- **백업 파일 수**: 5개
- **인코딩**: UTF-8

### 주요 로그 포인트

1. **서버 시작/종료**
   ```python
   log_startup()
   log_shutdown()
   ```

2. **API 요청/응답**
   - 모든 API 요청이 자동으로 로깅됨
   - 요청 메서드, URL, 상태 코드, 처리 시간 기록

3. **CSV 업로드**
   ```
   📤 CSV 파일 업로드 시작
   📄 CSV 파일 읽기 완료
   💾 CSV 파일 저장 완료
   🔄 TransactionParser 생성 중
   📊 데이터 파싱 및 캐싱 시작
   ✅ 데이터 파싱 및 캐싱 완료
   ```

4. **에러 처리**
   ```python
   log_exception(logger, error, "컨텍스트 정보")
   ```

## 💻 Frontend 로깅

### 로그 저장 위치
- **메모리**: 최대 1000개 로그 저장
- **LocalStorage**: 최근 100개 로그 저장

### 사용 방법

```typescript
import { logger } from '@/utils/logger';

// 디버그 로그
logger.debug('상세 디버그 정보', { key: 'value' });

// 정보 로그
logger.info('일반 정보', { data });

// 경고 로그
logger.warn('경고 메시지', { warning });

// 에러 로그
logger.error('에러 발생', error, { additionalData });
```

### 로그 다운로드
브라우저 콘솔에서:
```javascript
logger.downloadLogs() // JSON 파일로 다운로드
```

### 전역 에러 처리
- 모든 uncaught 에러 자동 로깅
- Unhandled promise rejection 자동 로깅

## 📊 로그 확인 방법

### Backend 로그 실시간 확인
```bash
# 전체 로그
tail -f log_data/backend.log

# 에러만
tail -f log_data/backend_error.log

# API 접근 로그
tail -f log_data/backend_access.log

# 특정 키워드 검색
grep "ERROR" log_data/backend.log
grep "CSV" log_data/backend.log
```

### Frontend 로그 확인
1. 브라우저 개발자 도구 (F12)
2. Console 탭에서 로그 확인
3. 이모지로 로그 레벨 구분:
   - 🔍 DEBUG
   - ℹ️ INFO
   - ⚠️ WARNING
   - ❌ ERROR

## 🛠️ 디버깅 팁

### 1. API 요청 추적
```bash
# 특정 API 엔드포인트 호출 추적
grep "/upload-csv" log_data/backend_access.log
```

### 2. 에러 분석
```bash
# 최근 에러 확인
tail -50 log_data/backend_error.log

# 특정 날짜 에러 검색
grep "2025-10-12" log_data/backend_error.log | grep "ERROR"
```

### 3. 성능 모니터링
```bash
# API 응답 시간 확인
grep "Duration:" log_data/backend_access.log
```

## 🧹 로그 정리

### 로그 파일 삭제
```bash
rm -rf log_data/*.log
```

### 백업 파일 정리
로그 파일은 자동으로 로테이션되며, 오래된 백업은 자동 삭제됨:
- backend.log
- backend.log.1
- backend.log.2
- backend.log.3
- backend.log.4
- backend.log.5

## 📝 개발 시 주의사항

1. **민감한 정보 로깅 금지**
   - 비밀번호, API 키, 개인정보 등은 로그에 남기지 말 것

2. **적절한 로그 레벨 사용**
   - DEBUG: 개발 중 상세 정보
   - INFO: 정상 흐름 정보
   - WARNING: 주의가 필요한 상황
   - ERROR: 에러 발생

3. **로그 크기 관리**
   - 과도한 로깅은 디스크 공간 소모
   - 필요한 정보만 로깅

4. **성능 고려**
   - 로그 I/O는 성능에 영향
   - 프로덕션 환경에서는 DEBUG 레벨 비활성화

## 🚀 프로덕션 배포 시

1. **환경별 로그 레벨 설정**
   - Development: DEBUG
   - Production: INFO

2. **로그 백업**
   - 정기적인 로그 백업
   - 로그 분석 도구 연동 (ELK, Splunk 등)

3. **모니터링**
   - 에러 로그 실시간 모니터링
   - 알림 시스템 연동

