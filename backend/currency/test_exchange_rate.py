"""
환율 조회 서비스 테스트 스크립트

Usage:
    python test_exchange_rate.py
"""

import sys
import os

# 상위 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from currency import get_exchange_rate_service


def main():
    print("=" * 80)
    print("네이버 금융 환율 조회 서비스 테스트")
    print("=" * 80)
    print()
    
    # 서비스 인스턴스 가져오기
    service = get_exchange_rate_service()
    
    # 1. USD 환율 조회
    print("1️⃣ USD 환율 조회")
    print("-" * 80)
    usd_rate = service.get_usd_rate()
    if usd_rate:
        print(f"✅ USD 환율: {usd_rate:,.2f}원")
    else:
        print("❌ USD 환율을 가져올 수 없습니다.")
    print()
    
    # 2. 주요 통화 환율 조회
    print("2️⃣ 주요 통화 환율 조회")
    print("-" * 80)
    currencies = ['USD', 'EUR', 'JPY', 'CNY', 'GBP']
    
    for currency in currencies:
        rate = service.get_rate(currency)
        if rate:
            print(f"  {currency:10s}: {rate:>10,.2f}원")
        else:
            print(f"  {currency:10s}: 조회 실패")
    print()
    
    # 3. 환율 변환
    print("3️⃣ 환율 변환 테스트")
    print("-" * 80)
    amounts = [100, 1000, 10000]
    
    for amount in amounts:
        krw = service.convert_to_krw(amount, 'USD')
        if krw:
            print(f"  ${amount:,} USD = {krw:,.2f}원")
    print()
    
    # 4. 전체 환율 정보
    print("4️⃣ 전체 환율 정보")
    print("-" * 80)
    all_rates = service.get_all_rates()
    
    if all_rates:
        for code, info in all_rates.items():
            print(f"  {code:10s} | {info['currency_name']:30s} | {info['rate']:>10,.2f}원")
    else:
        print("  환율 정보를 가져올 수 없습니다.")
    print()
    
    # 5. 캐시 정보
    print("5️⃣ 캐시 정보")
    print("-" * 80)
    cache_info = service.get_cache_info()
    
    print(f"  캐시 파일:      {cache_info['cache_file']}")
    print(f"  마지막 업데이트: {cache_info['last_update']}")
    print(f"  다음 업데이트:   {cache_info['next_update']}")
    print(f"  캐시된 통화 수:  {cache_info['cached_currencies']}개")
    print(f"  캐시 유효기간:   {cache_info['cache_duration_hours']}시간")
    print()
    
    print("=" * 80)
    print("테스트 완료!")
    print("=" * 80)


if __name__ == "__main__":
    main()

