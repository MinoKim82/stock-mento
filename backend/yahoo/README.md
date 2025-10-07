# Yahoo Finance API 모듈

Yahoo Finance API를 사용하여 한국 주식, 미국 주식 및 모든 주식의 실시간 가격을 조회하는 모듈입니다.

## 주요 기능

### 1. 전 세계 주식 가격 조회
- **한국 주식**: 삼성전자, LG화학, SK하이닉스, 네이버, 카카오 등
- **미국 주식**: Apple, Microsoft, Google, Amazon, Tesla 등
- **ETF**: SPY, QQQ, KODEX 시리즈, TIGER 시리즈 등
- **실시간 데이터**: 현재가, 등락률, 거래량, 시가총액 등

### 2. 자동 심볼 정규화
- 종목명을 Yahoo Finance 형식으로 자동 변환
- 한국 주식: `삼성전자` → `005930.KS`
- 미국 주식: `Apple` → `AAPL`
- ETF: `KODEX 200` → `069500.KS`

### 3. 캐시 시스템
- 5분 캐시로 API 호출 최적화
- 중복 요청 방지
- 자동 캐시 만료 관리

### 4. 포괄적 검색
- 종목명으로 검색 가능
- 시장별 분류 (한국, 미국, ETF)
- 실시간 유효성 검증

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install yfinance==0.2.18
```

### 2. 사용 방법

#### 기본 사용법
```python
from yahoo import get_yahoo_price_service

# 서비스 인스턴스 생성
service = get_yahoo_price_service()

# 단일 주식 가격 조회
price = service.get_current_price("삼성전자")
print(f"삼성전자 현재가: {price:,.0f}원")

# 상세 정보 조회
info = service.get_stock_price("AAPL")
print(f"Apple 현재가: ${info['current_price']:,.2f}")
print(f"등락률: {info['change_rate']:+.2f}%")
```

#### 여러 주식 조회
```python
symbols = ["삼성전자", "AAPL", "MSFT", "GOOGL"]
prices = service.get_multiple_stock_prices(symbols)

for symbol, data in prices.items():
    print(f"{symbol}: {data['current_price']:,.2f} {data['currency']}")
```

#### 주식 검색
```python
# 삼성 관련 종목 검색
results = service.search_stocks("삼성")
for result in results:
    print(f"{result['name']} ({result['symbol']}) - {result['market']}")
```

## API 엔드포인트

### 1. 단일 주식 가격 조회
```http
GET /yahoo/price/{symbol}
```
**예시**: `GET /yahoo/price/삼성전자`

**응답**:
```json
{
  "symbol": "삼성전자",
  "normalized_symbol": "005930.KS",
  "current_price": 85000.0,
  "previous_close": 84500.0,
  "change_amount": 500.0,
  "change_rate": 0.59,
  "volume": 12345678,
  "market_cap": 507000000000000,
  "currency": "KRW",
  "market": "kse_market",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "updated_at": "2024-01-15T10:30:00"
}
```

### 2. 여러 주식 가격 조회
```http
POST /yahoo/prices
Content-Type: application/json

["삼성전자", "AAPL", "MSFT"]
```

### 3. 주식 검색
```http
GET /yahoo/search?query=삼성&limit=10
```

### 4. 시장 상태 조회
```http
GET /yahoo/market-status
```

### 5. 심볼 유효성 검증
```http
GET /yahoo/validate/{symbol}
```

### 6. 심볼 정보 조회
```http
GET /yahoo/symbol-info/{symbol}
```

## 지원하는 주식 심볼

### 한국 주식 (KRW)
- **대형주**: 삼성전자, SK하이닉스, LG화학, 네이버, 카카오
- **금융주**: KB금융, 신한지주, 기업은행, 하나금융지주
- **자동차**: 현대차, 기아, 현대모비스
- **기타**: POSCO, KT&G, 아모레퍼시픽, 셀트리온

### 미국 주식 (USD)
- **기술주**: Apple, Microsoft, Google, Amazon, Tesla, Meta, Nvidia
- **금융주**: JPMorgan, Bank of America, Wells Fargo, Visa
- **소비재**: Coca Cola, PepsiCo, Procter & Gamble, Nike
- **헬스케어**: Pfizer, Merck, Johnson & Johnson

### ETF
- **미국 ETF**: SPY, QQQ, IWM, VTI
- **한국 ETF**: KODEX 200, KODEX 고배당주, TIGER 200
- **섹터 ETF**: XLK, XLF, XLV, XLE

## 고급 기능

### 1. 히스토리 데이터 조회
```python
# 1개월 히스토리
history = service.get_stock_history("삼성전자", "1mo")
print(f"1개월 전 가격: {history['data']['close']:,.0f}원")
```

### 2. 시장 상태 모니터링
```python
status = service.get_market_status()
for market, data in status['markets'].items():
    print(f"{market}: {data['price']:,.2f} ({data['change_rate']:+.2f}%)")
```

### 3. 포트폴리오 요약
```python
symbols = ["삼성전자", "AAPL", "MSFT"]
summary = service.get_portfolio_summary(symbols)
print(f"성공률: {summary['successful_quotes']}/{summary['total_symbols']}")
```

### 4. 커스텀 심볼 추가
```python
# 새로운 종목 추가
service.add_custom_symbol("새로운종목", "123456.KS", "KR")
```

## 캐시 관리

### 1. 캐시 정보 조회
```python
cache_info = service.get_cache_info()
print(f"캐시된 종목 수: {cache_info['cache_size']}")
```

### 2. 캐시 클리어
```python
# 특정 종목 캐시 클리어
service.clear_cache("삼성전자")

# 전체 캐시 클리어
service.clear_cache()
```

### 3. 배치 업데이트
```python
# 캐시 우회하여 새로 조회
symbols = ["삼성전자", "AAPL", "MSFT"]
prices = service.batch_update_prices(symbols)
```

## 오류 처리

### 1. 일반적인 오류
- **404**: 주식 정보를 찾을 수 없음
- **500**: 서버 내부 오류
- **503**: Yahoo Finance API 사용 불가

### 2. 오류 해결 방법
```python
try:
    price = service.get_current_price("존재하지않는종목")
except Exception as e:
    print(f"오류 발생: {e}")
```

## 성능 최적화

### 1. API 호출 제한
- 요청 간 0.1초 딜레이 자동 적용
- 동시 요청 수 제한

### 2. 캐시 전략
- 5분 캐시로 중복 요청 방지
- 메모리 기반 캐시로 빠른 응답

### 3. 배치 처리
- 여러 종목을 한 번에 처리
- 병렬 처리로 성능 향상

## 주의사항

1. **API 제한**: Yahoo Finance는 요청 제한이 있습니다.
2. **장시간**: 실시간 데이터는 장시간에만 정확합니다.
3. **네트워크**: 인터넷 연결이 필요합니다.
4. **데이터 지연**: 15-20분 지연이 있을 수 있습니다.

## 예시 코드

### 포트폴리오 모니터링
```python
from yahoo import get_yahoo_price_service

service = get_yahoo_price_service()

# 포트폴리오 종목
portfolio = {
    "삼성전자": 100,
    "AAPL": 50,
    "MSFT": 30
}

print("📊 포트폴리오 현황")
print("=" * 50)

total_value = 0
for symbol, shares in portfolio.items():
    price = service.get_current_price(symbol)
    if price:
        value = price * shares
        total_value += value
        print(f"{symbol}: {shares}주 × {price:,.2f} = {value:,.2f}")

print(f"\n총 평가금액: {total_value:,.2f}")
```

### 시장 대시보드
```python
# 주요 지수 현황
status = service.get_market_status()
print("📈 주요 지수 현황")
print("=" * 30)

for market, data in status['markets'].items():
    direction = "📈" if data['change'] > 0 else "📉"
    print(f"{direction} {market}: {data['price']:,.2f} ({data['change_rate']:+.2f}%)")
```

이제 Yahoo Finance API를 통해 전 세계 모든 주식의 실시간 가격을 쉽게 조회할 수 있습니다! 🌍📈
