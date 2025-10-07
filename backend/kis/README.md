# 한국투자증권 API 모듈

한국투자증권 KIS API를 사용하여 한국 주식의 실시간 가격을 조회하는 모듈입니다.

## 설정 방법

### 1. .env 파일 생성

`backend/kis/` 폴더에 `.env` 파일을 생성하고 다음과 같이 설정하세요:

```env
# 한국투자증권 API 설정
KIS_USER_ID=your_actual_user_id
KIS_ACCOUNT_NO=your_actual_account_number
KIS_APP_KEY=your_actual_app_key
KIS_APP_SECRET=your_actual_app_secret

# API 엔드포인트
KIS_BASE_URL=https://openapi.koreainvestment.com:9443
KIS_REAL_BASE_URL=https://openapi.koreainvestment.com:9443

# 환경 (실전: "prod", 모의: "sandbox")
KIS_ENV=sandbox
```

### 2. 한국투자증권 API 키 발급

1. [한국투자증권 홈페이지](https://www.koreainvestment.com) 접속
2. 계좌 개설 및 로그인
3. KIS Developers 메뉴에서 API 키 발급
4. 발급받은 정보를 .env 파일에 입력

### 3. 사용 방법

```python
from kis import get_stock_price_service
from pp import TransactionParser

# 실시간 가격 조회 활성화
parser = TransactionParser('pp/All_transactions.csv', enable_real_time_prices=True)

# 주식 보유 목록 조회 (실시간 가격 포함)
holdings = parser.get_all_stock_holdings()

for holding in holdings:
    if holding.current_price > 0:  # 실시간 가격이 조회된 경우
        print(f"{holding.security}: {holding.current_price:,.0f}원")
        print(f"평가금액: {holding.current_value:,.0f}원")
        print(f"미실현손익: {holding.unrealized_gain_loss:+,.0f}원")
        print(f"수익률: {holding.unrealized_gain_loss_rate:+.2f}%")
```

## 주요 기능

### 1. 자동 토큰 관리
- 액세스 토큰 자동 발급 및 갱신
- 24시간 유효한 토큰을 자동으로 관리
- 토큰 파일 캐싱으로 불필요한 API 호출 방지

### 2. 실시간 가격 조회
- 한국 주식의 실시간 현재가 조회
- 5분 캐시로 API 호출 최적화
- 자동 심볼 정규화 (한국 주식에 'ks' 접미사 자동 추가)

### 3. 한국 주식 자동 인식
다음과 같은 한국 주식들이 자동으로 인식됩니다:
- 삼성전자, SK하이닉스, LG화학, 네이버, 카카오
- 현대차, 기아, POSCO, KB금융, 신한지주
- LG전자, SK텔레콤, KT&G, 현대모비스
- 기업은행, PS일렉트로닉스, GS글로벌 등

### 4. 수익률 계산
- 평균 매수가 대비 현재가 수익률
- 미실현 손익 및 손익률 자동 계산
- 계좌별, 종목별 상세 분석

## API 엔드포인트

기존 API 엔드포인트들이 실시간 가격 정보를 포함하도록 확장되었습니다:

- `/holdings/all` - 전체 주식 보유 목록 (실시간 가격 포함)
- `/holdings/account/{account_name}` - 계좌별 주식 보유 목록 (실시간 가격 포함)

## 주의사항

1. **API 제한**: 한국투자증권 API는 일일 호출 제한이 있습니다.
2. **장시간**: 실시간 가격은 장시간(09:00-15:30)에만 정확한 데이터를 제공합니다.
3. **환경 설정**: 모의투자 환경에서 먼저 테스트해보시기 바랍니다.
4. **보안**: .env 파일은 절대 공개하지 마세요.

## 오류 해결

### 403 Forbidden 오류
- .env 파일의 API 키가 올바른지 확인
- API 키 발급 상태 확인
- 모의투자/실전투자 환경 설정 확인

### 토큰 발급 실패
- 네트워크 연결 상태 확인
- API 키 유효성 확인
- 한국투자증권 서버 상태 확인

### 가격 조회 실패
- 장시간 여부 확인
- 종목 코드 정확성 확인
- API 호출 제한 확인
