"""
파서 관련 유틸리티 함수
"""
from typing import Dict, List
from pp import TransactionParser

def parse_account_info(account_name: str) -> Dict[str, str]:
    """
    계좌명에서 소유자, 증권사, 계좌타입을 추출
    예: "민호 토스 종합매매 해외" -> {"owner": "민호", "broker": "토스", "account_type": "종합매매 해외"}
    """
    # "예수금" 제거
    clean_name = account_name.replace(" 예수금", "").replace(" 예수", "")
    
    # 공백으로 분할
    parts = clean_name.split()
    
    if len(parts) >= 3:
        owner = parts[0]  # 첫 번째: 소유자
        broker = parts[1]  # 두 번째: 증권사
        account_type = " ".join(parts[2:])  # 나머지: 계좌 타입
        
        return {
            "owner": owner,
            "broker": broker,
            "account_type": account_type
        }
    elif len(parts) == 2:
        return {
            "owner": parts[0],
            "broker": parts[1],
            "account_type": "기본"
        }
    else:
        return {
            "owner": "알 수 없음",
            "broker": account_name,
            "account_type": "기본"
        }

def get_account_filters(parser: TransactionParser) -> Dict[str, List[str]]:
    """모든 계좌에서 필터 옵션들을 추출"""
    owners = set()
    brokers = set()
    account_types = set()
    
    # 모든 계좌 정보 추출
    accounts = parser.get_accounts()
    for account in accounts:
        account_info = parse_account_info(account.account_name)
        owners.add(account_info["owner"])
        brokers.add(account_info["broker"])
        account_types.add(account_info["account_type"])
    
    return {
        "owners": sorted(list(owners)),
        "brokers": sorted(list(brokers)),
        "account_types": sorted(list(account_types))
    }

