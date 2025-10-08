# Currency Exchange Rate Module

한국수출입은행 환율 조회 API를 사용하는 환율 서비스 모듈입니다.

## 기능

- ✅ 한국수출입은행 공식 환율 API 연동
- ✅ 1일 1회 자동 캐싱 (불필요한 API 호출 방지)
- ✅ 다양한 통화 지원 (USD, EUR, JPY 등)
- ✅ 여러 환율 타입 지원 (기준율, 매수율, 매도율)
- ✅ 환율 변환 기능 (외화 → 원화)

## 설정

### 1. API 키 발급

1. [한국수출입은행 오픈 API](https://www.koreaexim.go.kr/ir/HPHKIR020M01) 접속
2. 회원가입 및 로그인
3. API 키 신청 및 발급

### 2. .env 파일 설정

프로젝트 루트 디렉토리의 `.env` 파일에 다음 내용 추가:

```env
# 한국수출입은행 환율 API 인증키
EXCHANGE_RATE_AUTH_KEY=your_api_key_here
```

## 사용법

### 기본 사용

```python
from currency import get_exchange_rate_service

# 서비스 인스턴스 가져오기
service = get_exchange_rate_service()

# USD 환율 조회
usd_rate = service.get_usd_rate()
print(f"USD 환율: {usd_rate}원")

# 특정 통화 환율 조회
eur_rate = service.get_rate('EUR')
print(f"EUR 환율: {eur_rate}원")

# 환율 타입 지정
usd_buy = service.get_rate('USD', 'buy')   # 살 때
usd_sell = service.get_rate('USD', 'sell') # 팔 때
```

### 환율 변환

```python
# 100 USD를 원화로 변환
krw_amount = service.convert_to_krw(100, 'USD')
print(f"100 USD = {krw_amount}원")
```

### 전체 환율 정보 조회

```python
# 모든 통화 환율 조회
all_rates = service.get_all_rates()

for currency_code, info in all_rates.items():
    print(f"{info['currency_name']} ({currency_code}): {info['base_rate']}원")
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
        'currency_name': '미국 달러',
        'buy_rate': 1330.5,      # 살 때 환율
        'sell_rate': 1340.5,     # 팔 때 환율
        'base_rate': 1335.5,     # 기준 환율
        'last_update': '2025-10-08T12:00:00'
    },
    ...
}
```

## 지원 통화

주요 지원 통화 (한국수출입은행 기준):
- USD (미국 달러)
- EUR (유로)
- JPY(100) (일본 엔 100단위)
- CNY (중국 위안)
- GBP (영국 파운드)
- CHF (스위스 프랑)
- CAD (캐나다 달러)
- AUD (호주 달러)
- 기타 다수

## 캐싱 정책

- **캐시 유효기간**: 24시간 (1일)
- **자동 갱신**: 캐시 만료 시 자동으로 API 호출
- **메모리 저장**: 서버 재시작 시 캐시 초기화

## 에러 처리

```python
# 환율 조회 실패 시 None 반환
rate = service.get_rate('INVALID')
if rate is None:
    print("환율 정보를 가져올 수 없습니다.")
```

## 주의사항

1. **API 키 보안**: `.env` 파일을 Git에 커밋하지 마세요 (`.gitignore`에 추가)
2. **API 호출 제한**: 한국수출입은행 API의 호출 제한을 확인하세요
3. **영업일**: 주말/공휴일에는 전일 환율이 제공될 수 있습니다
4. **통화 코드**: 일부 통화는 단위가 포함됩니다 (예: `JPY(100)`)

## 트러블슈팅

### API 키 오류
```
⚠️ EXCHANGE_RATE_AUTH_KEY가 .env 파일에 설정되지 않았습니다.
```
→ `.env` 파일에 `EXCHANGE_RATE_AUTH_KEY` 설정 확인

### 환율 조회 실패
```
❌ 환율 API 호출 실패
```
→ 네트워크 연결 및 API 키 유효성 확인

### 통화 코드 없음
```
⚠️ XXX 환율 정보를 찾을 수 없습니다.
```
→ 지원되는 통화 코드인지 확인

