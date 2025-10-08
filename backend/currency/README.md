# Currency Exchange Rate Module

네이버 금융 페이지를 파싱하여 환율 정보를 가져오는 모듈입니다.

## 기능

- ✅ 네이버 금융 실시간 환율 정보 스크래핑
- ✅ 1일 1회 자동 갱신 (불필요한 요청 방지)
- ✅ JSON 파일에 영구 저장 (서버 재시작 후에도 유지)
- ✅ 주요 통화 지원 (USD, EUR, JPY, CNY 등)
- ✅ 환율 변환 기능 (외화 → 원화)

## 장점

1. **API 키 불필요** - 네이버 금융 페이지를 직접 파싱
2. **실시간 환율** - 네이버 금융의 최신 환율 정보
3. **영구 저장** - JSON 파일로 저장되어 서버 재시작 후에도 유지
4. **자동 캐싱** - 1일 1회만 갱신하여 서버 부하 최소화

## 설치

필요한 패키지 설치:
```bash
pip install beautifulsoup4 lxml requests
```

## 사용법

### 기본 사용

```python
from currency import get_exchange_rate_service

# 서비스 인스턴스
service = get_exchange_rate_service()

# USD 환율 조회
usd_rate = service.get_usd_rate()
print(f"USD: {usd_rate}원")

# 특정 통화 환율 조회
eur_rate = service.get_rate('EUR')
print(f"EUR: {eur_rate}원")
```

### 환율 변환

```python
# 100 USD를 원화로 변환
krw = service.convert_to_krw(100, 'USD')
print(f"100 USD = {krw}원")
```

### 전체 환율 정보 조회

```python
# 모든 통화 환율 조회
all_rates = service.get_all_rates()

for currency_code, info in all_rates.items():
    print(f"{info['currency_name']} ({currency_code}): {info['rate']}원")
```

### 강제 업데이트

```python
# 캐시 무시하고 즉시 업데이트
service.force_update()
```

### 캐시 정보 확인

```python
# 캐시 상태 확인
cache_info = service.get_cache_info()
print(f"마지막 업데이트: {cache_info['last_update']}")
print(f"다음 업데이트: {cache_info['next_update']}")
print(f"캐시된 통화 수: {cache_info['cached_currencies']}")
```

## API 응답 데이터 구조

```python
{
    'USD': {
        'currency_code': 'USD',
        'currency_name': '미국 USD',
        'rate': 1426.30,
        'last_update': '2025-10-08T12:00:00'
    },
    ...
}
```

## 지원 통화

네이버 금융에서 제공하는 주요 통화:
- USD (미국 달러)
- EUR (유로)
- JPY (일본 엔 100단위)
- CNY (중국 위안)
- GBP (영국 파운드)
- AUD (호주 달러)
- CAD (캐나다 달러)
- CHF (스위스 프랑)
- HKD (홍콩 달러)
- 기타 다수

## 캐싱 정책

- **캐시 유효기간**: 24시간 (1일)
- **저장 위치**: `currency_cache/exchange_rates.json`
- **자동 갱신**: 캐시 만료 시 자동으로 네이버 금융 페이지 파싱
- **영구 저장**: JSON 파일로 저장되어 서버 재시작 후에도 유지

## 디렉토리 구조

```
backend/currency/
├── __init__.py                    # 모듈 초기화
├── exchange_rate_service.py       # 메인 서비스
├── test_exchange_rate.py          # 테스트 스크립트
├── README.md                      # 사용 가이드
└── currency_cache/                # 캐시 디렉토리 (자동 생성)
    └── exchange_rates.json        # 환율 캐시 파일
```

## 테스트

테스트 스크립트 실행:
```bash
cd backend/currency
python test_exchange_rate.py
```

## 에러 처리

```python
# 환율 조회 실패 시 None 반환
rate = service.get_rate('INVALID')
if rate is None:
    print("환율 정보를 가져올 수 없습니다.")
```

## 주의사항

1. **네트워크 연결**: 네이버 금융 페이지 접근을 위해 인터넷 연결 필요
2. **HTML 구조 변경**: 네이버 금융 페이지 구조가 변경되면 파싱 로직 수정 필요
3. **요청 빈도**: 1일 1회만 갱신하여 네이버 서버 부하 최소화
4. **캐시 파일**: `.gitignore`에 `currency_cache/` 추가 권장

## 트러블슈팅

### 환율 데이터를 찾을 수 없음
```
⚠️ 환율 데이터를 찾을 수 없습니다.
```
→ 네이버 금융 페이지 HTML 구조가 변경되었을 가능성
→ 네트워크 연결 확인

### 특정 통화 조회 실패
```
⚠️ XXX 환율 정보를 찾을 수 없습니다.
```
→ 네이버 금융에서 해당 통화를 제공하지 않거나 코드 매핑 필요
→ `code_map`에 통화 추가 필요

## 예제 출력

```
✅ 환율 조회 서비스가 초기화되었습니다.
🔄 환율 정보를 업데이트합니다...
💾 캐시 파일 저장 완료: currency_cache/exchange_rates.json
✅ 환율 정보 업데이트 완료 (4개 통화)

USD 환율: 1,426.30원
EUR 환율: 1,657.93원
JPY 환율: 935.62원
CNY 환율: 199.55원
```

## 라이선스

이 모듈은 네이버 금융의 공개 정보를 파싱합니다. 상업적 용도로 사용 시 네이버 이용약관을 확인하세요.

