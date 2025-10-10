from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import uuid
import io
import pandas as pd
from dataclasses import asdict

# pp 패키지에서 데이터 처리 클래스와 모델 import
from pp import (
    TransactionParser,
    AccountInfo,
    StockHolding,
    AccountBalance,
    DividendInfo,
    InterestInfo,
    TradingPeriodReturn,
    AccountBalanceDetail,
    TotalBalance,
    YearlyReturnsDetail
)

# Yahoo API 임포트
try:
    from yahoo import get_yahoo_price_service
    from yahoo.yahoo_client import YahooClient
    YAHOO_AVAILABLE = True
    yahoo_client = YahooClient()
except ImportError:
    YAHOO_AVAILABLE = False
    yahoo_client = None

app = FastAPI(title="Stock Portfolio API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 백엔드 디렉토리 기준 경로
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

# CSV 파일 저장 디렉토리
CSV_STORAGE_DIR = os.path.join(BACKEND_DIR, "csv_data")
CURRENT_CSV_FILE = os.path.join(CSV_STORAGE_DIR, "current_portfolio.csv")

# 파싱된 데이터 캐시 디렉토리
PARSED_DATA_DIR = os.path.join(BACKEND_DIR, "parsed_data")
PARSED_DATA_FILE = os.path.join(PARSED_DATA_DIR, "portfolio_data.json")

# 디렉토리 생성
os.makedirs(CSV_STORAGE_DIR, exist_ok=True)
os.makedirs(PARSED_DATA_DIR, exist_ok=True)

# TransactionParser 인스턴스 (단일 인스턴스로 변경)
current_parser: Optional[TransactionParser] = None

def parse_and_cache_data(parser: TransactionParser):
    """모든 데이터를 파싱하고 JSON으로 캐싱"""
    try:
        print("📊 데이터 파싱 시작...")
        
        # 전체 잔액 정보
        total_balance = parser.get_total_balance()
        
        # 주식 보유 목록
        holdings = parser.get_all_stock_holdings()
        holdings_with_price = [h for h in holdings if h.current_price > 0]
        
        # 주식 포트폴리오 통계
        total_stock_cost = sum(h.total_cost for h in holdings_with_price)
        total_stock_value = sum(h.current_value for h in holdings_with_price)
        total_unrealized_gain = total_stock_value - total_stock_cost
        
        # 수익률 계산
        stock_return_rate = (total_unrealized_gain / total_stock_cost * 100) if total_stock_cost > 0 else 0
        
        # 수익/손실 종목 수
        gain_holdings = [h for h in holdings_with_price if h.unrealized_gain_loss >= 0]
        loss_holdings = [h for h in holdings_with_price if h.unrealized_gain_loss < 0]
        
        # 자산 배분
        cash_ratio = (total_balance.total_cash_balance / total_balance.total_balance * 100) if total_balance.total_balance > 0 else 0
        stock_ratio = (total_balance.total_stock_value / total_balance.total_balance * 100) if total_balance.total_balance > 0 else 0
        
        # 포트폴리오 요약 데이터 생성
        portfolio_summary = {
            "total_assets": {
                "cash_balance": total_balance.total_cash_balance,
                "stock_value": total_balance.total_stock_value,
                "total_balance": total_balance.total_balance,
                "account_count": total_balance.account_count
            },
            "stock_portfolio": {
                "total_investment": total_stock_cost,
                "current_value": total_stock_value,
                "unrealized_gain_loss": total_unrealized_gain,
                "return_rate": stock_return_rate,
                "total_holdings": len(holdings_with_price),
                "gain_holdings": len(gain_holdings),
                "loss_holdings": len(loss_holdings)
            },
            "asset_allocation": {
                "cash_ratio": cash_ratio,
                "stock_ratio": stock_ratio
            }
        }
        
        # 포트폴리오 성과 데이터 생성
        holdings_sorted = sorted(holdings_with_price, key=lambda x: x.unrealized_gain_loss_rate, reverse=True)
        top_performers = holdings_sorted[:5]
        bottom_performers = holdings_sorted[-5:]
        
        account_performance = {}
        for holding in holdings_with_price:
            if holding.account not in account_performance:
                account_performance[holding.account] = {
                    "holdings": [],
                    "total_investment": 0,
                    "total_value": 0,
                    "total_gain_loss": 0
                }
            account_performance[holding.account]["holdings"].append(asdict(holding))
            account_performance[holding.account]["total_investment"] += holding.total_cost
            account_performance[holding.account]["total_value"] += holding.current_value
        
        for account, data in account_performance.items():
            data["total_gain_loss"] = data["total_value"] - data["total_investment"]
            data["return_rate"] = (data["total_gain_loss"] / data["total_investment"] * 100) if data["total_investment"] > 0 else 0
        
        portfolio_performance = {
            "top_performers": [
                {
                    "security": h.security,
                    "account": h.account,
                    "shares": h.shares,
                    "investment": h.total_cost,
                    "current_value": h.current_value,
                    "gain_loss": h.unrealized_gain_loss,
                    "return_rate": h.unrealized_gain_loss_rate
                } for h in top_performers
            ],
            "bottom_performers": [
                {
                    "security": h.security,
                    "account": h.account,
                    "shares": h.shares,
                    "investment": h.total_cost,
                    "current_value": h.current_value,
                    "gain_loss": h.unrealized_gain_loss,
                    "return_rate": h.unrealized_gain_loss_rate
                } for h in bottom_performers
            ],
            "account_performance": {
                account: {
                    "holdings_count": len(data["holdings"]),
                    "total_investment": data["total_investment"],
                    "total_value": data["total_value"],
                    "total_gain_loss": data["total_gain_loss"],
                    "return_rate": data["return_rate"]
                } for account, data in account_performance.items()
            }
        }
        
        # 포트폴리오 리스크 데이터 생성
        total_value = sum(h.current_value for h in holdings_with_price)
        total_gain = sum(h.unrealized_gain_loss for h in gain_holdings)
        total_loss = sum(h.unrealized_gain_loss for h in loss_holdings)
        
        max_loss_holding = min(holdings_with_price, key=lambda x: x.unrealized_gain_loss) if loss_holdings else None
        max_gain_holding = max(holdings_with_price, key=lambda x: x.unrealized_gain_loss) if gain_holdings else None
        
        holdings_by_value = sorted(holdings_with_price, key=lambda x: x.current_value, reverse=True)
        top5_concentration = sum(h.current_value for h in holdings_by_value[:5]) / total_value * 100 if total_value > 0 else 0
        
        portfolio_risk = {
            "risk_metrics": {
                "total_holdings": len(holdings_with_price),
                "gain_holdings_count": len(gain_holdings),
                "loss_holdings_count": len(loss_holdings),
                "win_rate": len(gain_holdings) / len(holdings_with_price) * 100 if holdings_with_price else 0
            },
            "gain_loss_analysis": {
                "total_gain": total_gain,
                "total_loss": total_loss,
                "net_gain_loss": total_gain + total_loss,
                "max_gain": {
                    "security": max_gain_holding.security,
                    "account": max_gain_holding.account,
                    "gain_loss": max_gain_holding.unrealized_gain_loss,
                    "return_rate": max_gain_holding.unrealized_gain_loss_rate
                } if max_gain_holding else None,
                "max_loss": {
                    "security": max_loss_holding.security,
                    "account": max_loss_holding.account,
                    "gain_loss": max_loss_holding.unrealized_gain_loss,
                    "return_rate": max_loss_holding.unrealized_gain_loss_rate
                } if max_loss_holding else None
            },
            "concentration": {
                "top5_concentration": top5_concentration,
                "top_holdings": [
                    {
                        "security": h.security,
                        "current_value": h.current_value,
                        "portfolio_weight": h.current_value / total_value * 100 if total_value > 0 else 0
                    } for h in holdings_by_value[:5]
                ]
            }
        }
        
        # 모든 필요한 데이터 파싱
        cached_data = {
            "portfolio_summary": portfolio_summary,
            "portfolio_performance": portfolio_performance,
            "portfolio_risk": portfolio_risk,
            "accounts": [asdict(acc) for acc in parser.get_accounts()],
            "holdings": [asdict(h) for h in holdings],
            "balances": [asdict(b) for b in parser.get_all_account_balances()],
            "total_balance": asdict(total_balance),
            "yearly_returns": [asdict(yr) for yr in parser.get_yearly_returns()],
            "dividends": [asdict(d) for d in parser.get_all_dividends()],
            "interest": [asdict(i) for i in parser.get_all_interest()],
        }
        
        # 계좌별 상세 정보도 추가
        accounts_detailed = parser.get_accounts()
        accounts_by_owner_and_type = {}
        
        # 먼저 모든 보유 종목 가져오기 (현재가 포함)
        all_holdings = parser.get_all_stock_holdings()
        holdings_by_account = {}
        for h in all_holdings:
            if h.account not in holdings_by_account:
                holdings_by_account[h.account] = []
            holdings_by_account[h.account].append(h)
        
        for account_info in accounts_detailed:
            owner = account_info.owner
            account_type = account_info.account_type
            account_name = account_info.account_name
            
            if owner not in accounts_by_owner_and_type:
                accounts_by_owner_and_type[owner] = {}
            if account_type not in accounts_by_owner_and_type[owner]:
                accounts_by_owner_and_type[owner][account_type] = []
            
            # 계좌별 보유 종목 및 잔액
            holdings = holdings_by_account.get(account_name, [])
            balance = parser.get_account_balance(account_name)
            
            total_investment = sum(h.total_cost for h in holdings)
            stock_value = sum(h.current_value for h in holdings)
            total_gain_loss = sum(h.unrealized_gain_loss for h in holdings)
            
            account_detail = {
                "account_name": account_type,
                "full_account_name": account_name,
                "owner": owner,
                "broker": account_info.broker,
                "balance": balance.cash_balance,
                "stock_value": stock_value,
                "total_balance": balance.cash_balance + stock_value,
                "total_investment": total_investment,
                "total_gain_loss": total_gain_loss,
                "holdings": [asdict(h) for h in holdings]
            }
            
            accounts_by_owner_and_type[owner][account_type].append(account_detail)
        
        cached_data["accounts_detailed"] = {
            "accounts_by_owner_and_type": accounts_by_owner_and_type
        }
        
        # 소유자별 포트폴리오 요약 데이터 생성
        owner_summary = {}
        
        # 소유자 우선순위
        owner_order = {'혜란': 1, '유신': 2, '민호': 3}
        # 계좌타입 우선순위
        account_type_order = {'연금저축': 1, 'ISA': 2, '종합매매': 3, '종합매매 해외': 4}
        
        for owner, account_types in accounts_by_owner_and_type.items():
            if owner not in owner_summary:
                owner_summary[owner] = {}
            
            for account_type, accounts in account_types.items():
                summary = {
                    'cash_balance': sum(acc['balance'] for acc in accounts),
                    'stock_value': sum(acc['stock_value'] for acc in accounts),
                    'total_balance': sum(acc['total_balance'] for acc in accounts),
                    'total_investment': sum(acc['total_investment'] for acc in accounts),
                    'total_gain_loss': sum(acc['total_gain_loss'] for acc in accounts),
                    'account_count': len(accounts)
                }
                owner_summary[owner][account_type] = summary
        
        # 정렬된 소유자별 포트폴리오
        sorted_owner_summary = []
        for owner in sorted(owner_summary.keys(), key=lambda x: owner_order.get(x, 999)):
            account_types_list = []
            for account_type in sorted(owner_summary[owner].keys(), key=lambda x: account_type_order.get(x, 999)):
                summary = owner_summary[owner][account_type]
                return_rate = (summary['total_gain_loss'] / summary['total_investment'] * 100) if summary['total_investment'] > 0 else 0
                account_types_list.append({
                    'accountType': account_type,
                    'cash_balance': summary['cash_balance'],
                    'stock_value': summary['stock_value'],
                    'total_balance': summary['total_balance'],
                    'total_investment': summary['total_investment'],
                    'total_gain_loss': summary['total_gain_loss'],
                    'account_count': summary['account_count'],
                    'return_rate': return_rate
                })
            
            # 소유자별 합계 계산
            owner_total = {
                'cash_balance': sum(at['cash_balance'] for at in account_types_list),
                'stock_value': sum(at['stock_value'] for at in account_types_list),
                'total_balance': sum(at['total_balance'] for at in account_types_list),
                'total_investment': sum(at['total_investment'] for at in account_types_list),
                'total_gain_loss': sum(at['total_gain_loss'] for at in account_types_list)
            }
            
            sorted_owner_summary.append({
                'owner': owner,
                'accountTypes': account_types_list,
                'total': owner_total
            })
        
        # portfolio_summary에 owner_summary 추가
        cached_data["portfolio_summary"]["owner_summary"] = sorted_owner_summary
        cached_data["owner_summary"] = sorted_owner_summary
        
        # JSON 파일로 저장
        with open(PARSED_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 데이터 파싱 완료 및 캐시 저장: {PARSED_DATA_FILE}")
        return cached_data
        
    except Exception as e:
        print(f"⚠️ 데이터 파싱 실패: {e}")
        raise

def load_existing_csv():
    """서버 시작 시 기존 CSV 파일 로드"""
    global current_parser
    
    if os.path.exists(CURRENT_CSV_FILE):
        try:
            print(f"기존 CSV 파일 로드 중: {CURRENT_CSV_FILE}")
            current_parser = TransactionParser(CURRENT_CSV_FILE, yahoo_client=yahoo_client)
            print(f"✅ CSV 파일 로드 완료")
            
            # 데이터 파싱 및 캐싱
            parse_and_cache_data(current_parser)
        except Exception as e:
            print(f"⚠️ CSV 파일 로드 실패: {e}")
            current_parser = None
    else:
        print("기존 CSV 파일이 없습니다. CSV 파일을 업로드해주세요.")

# 계좌 정보 파싱 유틸리티 함수들
def parse_account_info(account_name: str) -> Dict[str, str]:
    """
    계좌명에서 소유자, 증권사, 계좌타입을 추출
    예: "민호 토스 종합매매 해외 예수금" -> {"owner": "민호", "broker": "토스", "account_type": "종합매매 해외"}
    """
    # "예수금" 제거
    clean_name = account_name.replace(" 예수금", "").replace(" 예수", "")
    
    # 공백으로 분할
    parts = clean_name.split()
    
    if len(parts) >= 3:
        owner = parts[0]  # 첫 번째: 소유자
        broker = parts[1]  # 두 번째: 증권사
        # 나머지: 계좌 타입
        account_type = " ".join(parts[2:])
        
        return {
            "owner": owner,
            "broker": broker,
            "account_type": account_type
        }
    
    # 파싱 실패 시 기본값 반환
    return {
        "owner": "알 수 없음",
        "broker": "알 수 없음", 
        "account_type": clean_name
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

@app.get("/")
async def root():
    return {"message": "포트폴리오 분석 API가 실행 중입니다.", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Server is running"}

# Pydantic 응답 모델 (dataclass와 동일한 구조)
class AccountInfoResponse(BaseModel):
    account_name: str
    account_type: str

class StockHoldingResponse(BaseModel):
    security: str
    shares: int
    account: str
    avg_price: float = 0.0
    total_cost: float = 0.0
    current_price: float = 0.0
    current_value: float = 0.0
    unrealized_gain_loss: float = 0.0
    unrealized_gain_loss_rate: float = 0.0

class DividendInfoResponse(BaseModel):
    account: str
    security: str
    total_dividend: float

class InterestInfoResponse(BaseModel):
    account: str
    total_interest: float

class TradingPeriodReturnResponse(BaseModel):
    account: str
    total_return: float
    return_percentage: float

class AccountBalanceResponse(BaseModel):
    account: str
    cash_balance: float
    stock_value: float
    total_balance: float

class TotalBalanceResponse(BaseModel):
    total_cash_balance: float
    total_stock_value: float
    total_balance: float
    account_count: int

class YearlyReturnsDetailResponse(BaseModel):
    year: int
    total_dividend: float
    total_sell_profit: float  # 매도 차익
    total_sell_revenue: float  # 전체 매도 금액
    total_sell_cost: float  # 전체 매도 원가
    total_interest: float
    total_returns: float
    by_security: Dict[str, Dict[str, float]]
    by_owner_and_account: Dict[str, Any]

# Yahoo API 응답 모델
class StockPriceResponse(BaseModel):
    symbol: str
    normalized_symbol: str
    current_price: float
    previous_close: float
    change_amount: float
    change_rate: float
    volume: int
    market_cap: int
    currency: str
    market: str
    sector: str
    industry: str
    updated_at: str

class MarketStatusResponse(BaseModel):
    timestamp: str
    markets: Dict[str, Any]

class SymbolSearchResponse(BaseModel):
    name: str
    symbol: str
    market: str

class SessionInfoResponse(BaseModel):
    session_id: str
    message: str
    cache_size: int
    total_sessions: int

# CSV 파일 업로드 API
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """CSV 파일을 디스크에 저장하고 로드"""
    global current_parser
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")
    
    try:
        # CSV 파일 내용 읽기
        csv_content = await file.read()
        csv_text = csv_content.decode('utf-8')
        
        # 디스크에 저장
        with open(CURRENT_CSV_FILE, 'w', encoding='utf-8') as f:
            f.write(csv_text)
        
        # TransactionParser 인스턴스 생성
        current_parser = TransactionParser(CURRENT_CSV_FILE, yahoo_client=yahoo_client)
        
        # 데이터 파싱 및 캐싱
        parse_and_cache_data(current_parser)
        
        return {
            "message": "CSV 파일이 성공적으로 업로드되고 파싱되었습니다.",
            "file_size": len(csv_text),
            "file_path": CURRENT_CSV_FILE,
            "parsed_data_path": PARSED_DATA_FILE
        }
    except Exception as e:
        current_parser = None
        raise HTTPException(status_code=400, detail=f"CSV 파일 처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/data/parsed")
async def get_parsed_data():
    """파싱된 전체 데이터를 JSON으로 반환"""
    if os.path.exists(PARSED_DATA_FILE):
        try:
            with open(PARSED_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"파싱된 데이터 로드 실패: {str(e)}")
    else:
        raise HTTPException(status_code=404, detail="파싱된 데이터가 없습니다. CSV 파일을 업로드해주세요.")

@app.get("/cache/info")
async def get_cache_info():
    """현재 CSV 파일 정보 조회"""
    if os.path.exists(CURRENT_CSV_FILE) and current_parser is not None:
        file_size = os.path.getsize(CURRENT_CSV_FILE)
        has_parsed_data = os.path.exists(PARSED_DATA_FILE)
        return {
            "total_sessions": 1,
            "total_cache_size": file_size,
            "total_cache_size_mb": round(file_size / 1024 / 1024, 2),
            "has_data": True,
            "has_parsed_data": has_parsed_data,
            "sessions": ["current"],
            "csv_file": CURRENT_CSV_FILE,
            "parsed_data_file": PARSED_DATA_FILE if has_parsed_data else None
        }
    else:
        return {
            "total_sessions": 0,
            "total_cache_size": 0,
            "total_cache_size_mb": 0.0,
            "has_data": False,
            "has_parsed_data": False,
            "sessions": [],
            "csv_file": None,
            "parsed_data_file": None
        }

@app.delete("/cache/{session_id}")
async def clear_session_cache(session_id: str):
    """현재 CSV 파일 삭제 (세션 ID는 무시됨 - 하위 호환성 유지)"""
    global current_parser
    
    # 현재 파서 초기화
    current_parser = None
    
    # CSV 파일 삭제
    csv_deleted = False
    if os.path.exists(CURRENT_CSV_FILE):
        try:
            os.remove(CURRENT_CSV_FILE)
            csv_deleted = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CSV 파일 삭제 실패: {str(e)}")
    
    # 파싱된 데이터 파일 삭제
    parsed_deleted = False
    if os.path.exists(PARSED_DATA_FILE):
        try:
            os.remove(PARSED_DATA_FILE)
            parsed_deleted = True
        except Exception as e:
            print(f"⚠️ 파싱 데이터 삭제 실패: {e}")
    
    if csv_deleted or parsed_deleted:
        return {"message": "캐시 파일이 삭제되었습니다. 새로운 파일을 업로드할 수 있습니다."}
    return {"message": "삭제할 캐시 파일이 없습니다."}

@app.delete("/cache/clear")
async def clear_all_cache():
    """현재 CSV 파일 삭제 (새로운 CSV 업로드 준비)"""
    global current_parser
    
    # 현재 파서 초기화
    current_parser = None
    
    # CSV 파일 삭제
    csv_deleted = False
    if os.path.exists(CURRENT_CSV_FILE):
        try:
            os.remove(CURRENT_CSV_FILE)
            csv_deleted = True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"CSV 파일 삭제 실패: {str(e)}")
    
    # 파싱된 데이터 파일 삭제
    parsed_deleted = False
    if os.path.exists(PARSED_DATA_FILE):
        try:
            os.remove(PARSED_DATA_FILE)
            parsed_deleted = True
        except Exception as e:
            print(f"⚠️ 파싱 데이터 삭제 실패: {e}")
    
    if csv_deleted or parsed_deleted:
        return {"message": "캐시 파일이 삭제되었습니다. 새로운 파일을 업로드할 수 있습니다."}
    return {"message": "삭제할 캐시 파일이 없습니다."}

def get_parser(session_id: str = None) -> TransactionParser:
    """현재 TransactionParser 인스턴스를 가져옴 (session_id는 무시됨 - 하위 호환성 유지)"""
    global current_parser
    
    if current_parser is None:
        raise HTTPException(status_code=404, detail="CSV 파일이 로드되지 않았습니다. CSV 파일을 업로드해주세요.")
    
    return current_parser

# API 엔드포인트들
@app.get("/accounts/{session_id}", response_model=List[AccountInfoResponse])
async def get_accounts(session_id: str):
    """모든 계좌 목록 반환 (정규화된 계좌)"""
    try:
        parser = get_parser(session_id)
        accounts = parser.get_accounts()
        return [AccountInfoResponse(
            account_name=acc.account_name,
            account_type=acc.account_type
        ) for acc in accounts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/holdings/all/{session_id}", response_model=List[StockHoldingResponse])
async def get_all_stock_holdings(session_id: str):
    """전체 주식 보유 목록"""
    try:
        parser = get_parser(session_id)
        holdings = parser.get_all_stock_holdings()
        return [StockHoldingResponse(
            security=h.security,
            shares=h.shares,
            account=h.account,
            avg_price=h.avg_price,
            total_cost=h.total_cost,
            current_price=h.current_price,
            current_value=h.current_value,
            unrealized_gain_loss=h.unrealized_gain_loss,
            unrealized_gain_loss_rate=h.unrealized_gain_loss_rate
        ) for h in holdings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/holdings/account/{session_id}/{account_name}", response_model=List[StockHoldingResponse])
async def get_holdings_by_account(session_id: str, account_name: str):
    """특정 계좌의 주식 보유 목록"""
    try:
        parser = get_parser(session_id)
        holdings = parser.get_holdings_by_account(account_name)
        return [StockHoldingResponse(
            security=h.security,
            shares=h.shares,
            account=h.account,
            avg_price=h.avg_price,
            total_cost=h.total_cost,
            current_price=h.current_price,
            current_value=h.current_value,
            unrealized_gain_loss=h.unrealized_gain_loss,
            unrealized_gain_loss_rate=h.unrealized_gain_loss_rate
        ) for h in holdings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/dividends/all/{session_id}", response_model=List[DividendInfoResponse])
async def get_all_dividends(session_id: str):
    """전체 배당 수익 목록"""
    try:
        parser = get_parser(session_id)
        dividends = parser.get_all_dividends()
        return [DividendInfoResponse(
            account=d.account,
            security=d.security,
            total_dividend=d.total_dividend
        ) for d in dividends]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/dividends/account/{session_id}/{account_name}", response_model=List[DividendInfoResponse])
async def get_dividends_by_account(session_id: str, account_name: str):
    """특정 계좌의 배당 수익 목록"""
    try:
        parser = get_parser(session_id)
        dividends = parser.get_dividends_by_account(account_name)
        return [DividendInfoResponse(
            account=d.account,
            security=d.security,
            total_dividend=d.total_dividend
        ) for d in dividends]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/interest/all/{session_id}", response_model=List[InterestInfoResponse])
async def get_all_interest(session_id: str):
    """전체 이자 수익 목록"""
    try:
        parser = get_parser(session_id)
        interest_list = parser.get_all_interest()
        return [InterestInfoResponse(
            account=i.account,
            total_interest=i.total_interest
        ) for i in interest_list]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/returns/all/{session_id}", response_model=List[TradingPeriodReturnResponse])
async def get_all_returns(session_id: str):
    """전체 거래 기간별 수익 목록"""
    try:
        parser = get_parser(session_id)
        returns = parser.get_all_returns()
        return [TradingPeriodReturnResponse(
            account=r.account,
            total_return=r.total_return,
            return_percentage=r.return_percentage
        ) for r in returns]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/balances/all/{session_id}", response_model=List[AccountBalanceResponse])
async def get_all_account_balances(session_id: str):
    """모든 계좌의 잔액 정보"""
    try:
        parser = get_parser(session_id)
        balances = parser.get_all_account_balances()
        return [AccountBalanceResponse(
            account=b.account,
            cash_balance=b.cash_balance,
            stock_value=b.stock_value,
            total_balance=b.total_balance
        ) for b in balances]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/balances/account/{session_id}/{account_name}", response_model=AccountBalanceResponse)
async def get_account_balance(session_id: str, account_name: str):
    """특정 계좌의 잔액 정보"""
    try:
        parser = get_parser(session_id)
        balance = parser.get_account_balance(account_name)
        return AccountBalanceResponse(
            account=balance.account,
            cash_balance=balance.cash_balance,
            stock_value=balance.stock_value,
            total_balance=balance.total_balance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/balances/total/{session_id}", response_model=TotalBalanceResponse)
async def get_total_balance(session_id: str):
    """전체 잔액 정보"""
    try:
        parser = get_parser(session_id)
        total_balance = parser.get_total_balance()
        return TotalBalanceResponse(
            total_cash_balance=total_balance.total_cash_balance,
            total_stock_value=total_balance.total_stock_value,
            total_balance=total_balance.total_balance,
            account_count=total_balance.account_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

# Yahoo Finance API 엔드포인트들
@app.get("/yahoo/price/{symbol}", response_model=StockPriceResponse)
async def get_stock_price(symbol: str):
    """단일 주식 가격 조회"""
    if not YAHOO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Yahoo Finance API가 사용할 수 없습니다.")
    
    try:
        yahoo_service = get_yahoo_price_service()
        price_data = yahoo_service.get_stock_price(symbol)
        
        if not price_data:
            raise HTTPException(status_code=404, detail=f"주식 정보를 찾을 수 없습니다: {symbol}")
        
        return StockPriceResponse(**price_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가격 조회 실패: {str(e)}")

@app.post("/yahoo/prices", response_model=Dict[str, StockPriceResponse])
async def get_multiple_stock_prices(symbols: List[str]):
    """여러 주식 가격 조회"""
    if not YAHOO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Yahoo Finance API가 사용할 수 없습니다.")
    
    try:
        yahoo_service = get_yahoo_price_service()
        prices = yahoo_service.get_multiple_stock_prices(symbols)
        
        return {symbol: StockPriceResponse(**data) for symbol, data in prices.items()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"가격 조회 실패: {str(e)}")

@app.get("/yahoo/search", response_model=List[SymbolSearchResponse])
async def search_stocks(query: str, limit: int = 10):
    """주식 검색"""
    if not YAHOO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Yahoo Finance API가 사용할 수 없습니다.")
    
    try:
        yahoo_service = get_yahoo_price_service()
        results = yahoo_service.search_stocks(query, limit)
        
        return [SymbolSearchResponse(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

@app.get("/yahoo/market-status", response_model=MarketStatusResponse)
async def get_market_status():
    """시장 상태 조회"""
    if not YAHOO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Yahoo Finance API가 사용할 수 없습니다.")
    
    try:
        yahoo_service = get_yahoo_price_service()
        status = yahoo_service.get_market_status()
        
        return MarketStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"시장 상태 조회 실패: {str(e)}")

@app.get("/yahoo/validate/{symbol}")
async def validate_symbol(symbol: str):
    """심볼 유효성 검증"""
    if not YAHOO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Yahoo Finance API가 사용할 수 없습니다.")
    
    try:
        yahoo_service = get_yahoo_price_service()
        is_valid = yahoo_service.validate_symbol(symbol)
        
        return {"symbol": symbol, "valid": is_valid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"심볼 검증 실패: {str(e)}")

@app.get("/yahoo/symbol-info/{symbol}")
async def get_symbol_info(symbol: str):
    """심볼 정보 조회"""
    if not YAHOO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Yahoo Finance API가 사용할 수 없습니다.")
    
    try:
        yahoo_service = get_yahoo_price_service()
        info = yahoo_service.get_symbol_info(symbol)
        
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"심볼 정보 조회 실패: {str(e)}")

# 포트폴리오 요약 API 엔드포인트들
@app.get("/portfolio/summary/{session_id}")
async def get_portfolio_summary(session_id: str):
    """포트폴리오 전체 요약"""
    try:
        # 캐시된 데이터가 있으면 사용
        if os.path.exists(PARSED_DATA_FILE):
            try:
                with open(PARSED_DATA_FILE, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    if 'portfolio_summary' in cached_data:
                        return cached_data['portfolio_summary']
            except Exception as e:
                print(f"⚠️ 캐시된 데이터 로드 실패: {e}")
        
        # 캐시가 없으면 실시간 계산
        parser = get_parser(session_id)
        
        # 전체 잔액 정보
        total_balance = parser.get_total_balance()
        
        # 주식 보유 목록
        holdings = parser.get_all_stock_holdings()
        holdings_with_price = [h for h in holdings if h.current_price > 0]
        
        # 주식 포트폴리오 통계
        total_stock_cost = sum(h.total_cost for h in holdings_with_price)
        total_stock_value = sum(h.current_value for h in holdings_with_price)
        total_unrealized_gain = total_stock_value - total_stock_cost
        
        # 수익률 계산
        stock_return_rate = (total_unrealized_gain / total_stock_cost * 100) if total_stock_cost > 0 else 0
        
        # 수익/손실 종목 수
        gain_holdings = [h for h in holdings_with_price if h.unrealized_gain_loss >= 0]
        loss_holdings = [h for h in holdings_with_price if h.unrealized_gain_loss < 0]
        
        # 자산 배분
        cash_ratio = (total_balance.total_cash_balance / total_balance.total_balance * 100) if total_balance.total_balance > 0 else 0
        stock_ratio = (total_balance.total_stock_value / total_balance.total_balance * 100) if total_balance.total_balance > 0 else 0
        
        return {
            "total_assets": {
                "cash_balance": total_balance.total_cash_balance,
                "stock_value": total_balance.total_stock_value,
                "total_balance": total_balance.total_balance,
                "account_count": total_balance.account_count
            },
            "stock_portfolio": {
                "total_investment": total_stock_cost,
                "current_value": total_stock_value,
                "unrealized_gain_loss": total_unrealized_gain,
                "return_rate": stock_return_rate,
                "total_holdings": len(holdings_with_price),
                "gain_holdings": len(gain_holdings),
                "loss_holdings": len(loss_holdings)
            },
            "asset_allocation": {
                "cash_ratio": cash_ratio,
                "stock_ratio": stock_ratio
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 요약 생성 실패: {str(e)}")

@app.get("/portfolio/performance/{session_id}")
async def get_portfolio_performance(session_id: str):
    """포트폴리오 성과 분석"""
    try:
        parser = get_parser(session_id)
        holdings = parser.get_all_stock_holdings()
        holdings_with_price = [h for h in holdings if h.current_price > 0]
        
        # 수익률 기준 정렬
        holdings_sorted = sorted(holdings_with_price, key=lambda x: x.unrealized_gain_loss_rate, reverse=True)
        
        # TOP/BOTTOM 5
        top_performers = holdings_sorted[:5]
        bottom_performers = holdings_sorted[-5:]
        
        # 계좌별 성과
        account_performance = {}
        for holding in holdings_with_price:
            if holding.account not in account_performance:
                account_performance[holding.account] = {
                    "holdings": [],
                    "total_investment": 0,
                    "total_value": 0,
                    "total_gain_loss": 0
                }
            
            account_performance[holding.account]["holdings"].append(holding)
            account_performance[holding.account]["total_investment"] += holding.total_cost
            account_performance[holding.account]["total_value"] += holding.current_value
        
        # 계좌별 수익률 계산
        for account, data in account_performance.items():
            data["total_gain_loss"] = data["total_value"] - data["total_investment"]
            data["return_rate"] = (data["total_gain_loss"] / data["total_investment"] * 100) if data["total_investment"] > 0 else 0
        
        return {
            "top_performers": [
                {
                    "security": h.security,
                    "account": h.account,
                    "shares": h.shares,
                    "investment": h.total_cost,
                    "current_value": h.current_value,
                    "gain_loss": h.unrealized_gain_loss,
                    "return_rate": h.unrealized_gain_loss_rate
                } for h in top_performers
            ],
            "bottom_performers": [
                {
                    "security": h.security,
                    "account": h.account,
                    "shares": h.shares,
                    "investment": h.total_cost,
                    "current_value": h.current_value,
                    "gain_loss": h.unrealized_gain_loss,
                    "return_rate": h.unrealized_gain_loss_rate
                } for h in bottom_performers
            ],
            "account_performance": {
                account: {
                    "holdings_count": len(data["holdings"]),
                    "total_investment": data["total_investment"],
                    "total_value": data["total_value"],
                    "total_gain_loss": data["total_gain_loss"],
                    "return_rate": data["return_rate"]
                } for account, data in account_performance.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 성과 분석 실패: {str(e)}")

@app.get("/portfolio/risk/{session_id}")
async def get_portfolio_risk(session_id: str):
    """포트폴리오 위험 분석"""
    try:
        parser = get_parser(session_id)
        holdings = parser.get_all_stock_holdings()
        holdings_with_price = [h for h in holdings if h.current_price > 0]
        
        # 손실/수익 종목 분석
        gain_holdings = [h for h in holdings_with_price if h.unrealized_gain_loss >= 0]
        loss_holdings = [h for h in holdings_with_price if h.unrealized_gain_loss < 0]
        
        # 손실/수익 금액
        total_gain = sum(h.unrealized_gain_loss for h in gain_holdings)
        total_loss = sum(h.unrealized_gain_loss for h in loss_holdings)
        
        # 최대 손실 종목
        max_loss_holding = min(holdings_with_price, key=lambda x: x.unrealized_gain_loss) if loss_holdings else None
        
        # 최대 수익 종목
        max_gain_holding = max(holdings_with_price, key=lambda x: x.unrealized_gain_loss) if gain_holdings else None
        
        # 종목별 집중도 (상위 5개 종목의 비중)
        holdings_by_value = sorted(holdings_with_price, key=lambda x: x.current_value, reverse=True)
        total_value = sum(h.current_value for h in holdings_with_price)
        top5_concentration = sum(h.current_value for h in holdings_by_value[:5]) / total_value * 100 if total_value > 0 else 0
        
        return {
            "risk_metrics": {
                "total_holdings": len(holdings_with_price),
                "gain_holdings_count": len(gain_holdings),
                "loss_holdings_count": len(loss_holdings),
                "win_rate": len(gain_holdings) / len(holdings_with_price) * 100 if holdings_with_price else 0
            },
            "gain_loss_analysis": {
                "total_gain": total_gain,
                "total_loss": total_loss,
                "net_gain_loss": total_gain + total_loss
            },
            "extreme_performers": {
                "max_gain": {
                    "security": max_gain_holding.security,
                    "account": max_gain_holding.account,
                    "gain_loss": max_gain_holding.unrealized_gain_loss,
                    "return_rate": max_gain_holding.unrealized_gain_loss_rate
                } if max_gain_holding else None,
                "max_loss": {
                    "security": max_loss_holding.security,
                    "account": max_loss_holding.account,
                    "gain_loss": max_loss_holding.unrealized_gain_loss,
                    "return_rate": max_loss_holding.unrealized_gain_loss_rate
                } if max_loss_holding else None
            },
            "concentration_risk": {
                "top5_concentration_ratio": top5_concentration,
                "top5_holdings": [
                    {
                        "security": h.security,
                        "account": h.account,
                        "value": h.current_value,
                        "ratio": h.current_value / total_value * 100 if total_value > 0 else 0
                    } for h in holdings_by_value[:5]
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"포트폴리오 위험 분석 실패: {str(e)}")

# 필터링 API 엔드포인트들
@app.get("/portfolio/filters/{session_id}")
async def get_portfolio_filters(session_id: str):
    """포트폴리오 필터 옵션 조회"""
    try:
        parser = get_parser(session_id)
        filters = get_account_filters(parser)
        return filters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"필터 옵션 조회 실패: {str(e)}")

@app.get("/portfolio/summary-filtered/{session_id}")
async def get_portfolio_summary_filtered(
    session_id: str,
    owner: Optional[str] = None,
    broker: Optional[str] = None,
    account_type: Optional[str] = None
):
    """필터링된 포트폴리오 요약"""
    try:
        parser = get_parser(session_id)
        
        # 필터링된 계좌 정보 가져오기
        accounts = parser.get_accounts()
        account_balances = parser.get_all_account_balances()
        
        # 필터 적용
        filtered_accounts = []
        filtered_balances = []
        
        for account in accounts:
            account_info = parse_account_info(account.account_name)
            if should_include_account(account_info, owner, broker, account_type):
                filtered_accounts.append(account)
        
        for balance in account_balances:
            account_info = parse_account_info(balance.account)
            if should_include_account(account_info, owner, broker, account_type):
                filtered_balances.append(balance)
        
        # 필터링된 계좌로 요약 계산
        total_cash_balance = sum(bal.cash_balance for bal in filtered_balances)
        total_stock_value = sum(bal.stock_value for bal in filtered_balances)
        total_assets = sum(bal.total_balance for bal in filtered_balances)
        
        # 주식 보유 정보에서 수익 계산
        holdings = parser.get_all_stock_holdings()
        filtered_holdings = []
        for holding in holdings:
            account_info = parse_account_info(holding.account)
            if should_include_account(account_info, owner, broker, account_type):
                filtered_holdings.append(holding)
        
        total_return_value = sum(h.unrealized_gain_loss for h in filtered_holdings)
        total_investment = sum(h.total_cost for h in filtered_holdings)
        total_return_percentage = (total_return_value / total_investment * 100) if total_investment > 0 else 0
        
        # 자산 배분 계산
        stock_allocation_percentage = (total_stock_value / total_assets * 100) if total_assets > 0 else 0
        cash_allocation_percentage = (total_cash_balance / total_assets * 100) if total_assets > 0 else 0
        
        summary = {
            "total_assets": total_assets,
            "total_cash_balance": total_cash_balance,
            "total_stock_value": total_stock_value,
            "total_return_value": total_return_value,
            "total_return_percentage": total_return_percentage,
            "total_dividend_interest_income": 0,  # TODO: 배당/이자 수익 계산
            "stock_allocation_percentage": stock_allocation_percentage,
            "cash_allocation_percentage": cash_allocation_percentage,
            "filtered_accounts": {
                "accounts": [{"account_name": acc.account_name, "account_type": acc.account_type} 
                           for acc in filtered_accounts],
                "balances": [{"account": bal.account, "total_balance": bal.total_balance} 
                           for bal in filtered_balances]
            },
            "filters_applied": {
                "owner": owner,
                "broker": broker,
                "account_type": account_type
            }
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"필터링된 포트폴리오 요약 생성 실패: {str(e)}")

@app.get("/portfolio/performance-filtered/{session_id}")
async def get_portfolio_performance_filtered(
    session_id: str,
    owner: Optional[str] = None,
    broker: Optional[str] = None,
    account_type: Optional[str] = None
):
    """필터링된 포트폴리오 성과 분석"""
    try:
        parser = get_parser(session_id)
        
        # 필터링된 주식 보유 정보 가져오기
        holdings = parser.get_all_stock_holdings()
        
        # 필터 적용하여 계좌별로 그룹화
        filtered_holdings_by_account = {}
        for holding in holdings:
            account_info = parse_account_info(holding.account)
            if should_include_account(account_info, owner, broker, account_type):
                if holding.account not in filtered_holdings_by_account:
                    filtered_holdings_by_account[holding.account] = []
                filtered_holdings_by_account[holding.account].append(holding)
        
        # 성과 분석 계산
        account_performance = {}
        for account_name, account_holdings in filtered_holdings_by_account.items():
            account_info = parse_account_info(account_name)
            total_investment = sum(h.total_cost for h in account_holdings)
            total_value = sum(h.current_value for h in account_holdings)
            total_gain_loss = sum(h.unrealized_gain_loss for h in account_holdings)
            
            account_performance[account_name] = {
                "total_investment": total_investment,
                "total_value": total_value,
                "total_gain_loss": total_gain_loss,
                "return_rate": (total_gain_loss / total_investment * 100) if total_investment > 0 else 0,
                "holdings_count": len(account_holdings),
                "account_info": account_info
            }
        
        return {
            "account_performance": account_performance,
            "total_accounts": len(filtered_holdings_by_account),
            "filters_applied": {
                "owner": owner,
                "broker": broker,
                "account_type": account_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"필터링된 포트폴리오 성과 분석 실패: {str(e)}")

@app.get("/transactions/{session_id}")
async def get_all_transactions(session_id: str):
    """전체 거래 내역 조회"""
    try:
        parser = get_parser(session_id)
        
        # 거래 데이터 가져오기
        df = parser.get_dataframe()
        
        # 필요한 컬럼만 선택하고 정렬
        # 컬럼명 매핑 (영어 -> 한국어)
        column_mapping = {
            'Date': '거래일',
            'Type': '거래구분', 
            'Security': '종목명',
            'Shares': '수량',
            'Quote': '단가',
            'Amount': '금액',
            'Note': '비고',
            'Cash Account': '계좌명'
        }
        
        # 컬럼명 변경
        df_mapped = df.rename(columns=column_mapping)
        
        # 필요한 컬럼만 선택하고 정렬
        transactions = df_mapped[['거래일', '계좌명', '거래구분', '종목명', '수량', '단가', '금액', '비고']].copy()
        transactions = transactions.sort_values(['거래일', '계좌명'], ascending=[False, True])
        
        # NaN 값을 빈 문자열로 변경
        transactions = transactions.fillna('')
        
        # 딕셔너리 형태로 변환
        transactions_list = transactions.to_dict('records')
        
        return {
            "transactions": transactions_list,
            "total_count": len(transactions_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"거래 내역 조회 실패: {str(e)}")

@app.get("/portfolio/accounts-detailed/{session_id}")
async def get_accounts_detailed(session_id: str):
    """계좌별 상세 정보 및 보유 종목 조회"""
    try:
        parser = get_parser(session_id)
        
        # 계좌 정보 가져오기
        accounts = parser.get_accounts()
        account_balances = parser.get_all_account_balances()
        holdings = parser.get_all_stock_holdings()
        
        # 소유자별, 계좌타입별 그룹화
        accounts_by_owner_and_type = {}
        
        for account in accounts:
            account_info = parse_account_info(account.account_name)
            owner = account_info["owner"]
            account_type = account_info["account_type"]
            
            # 소유자별 그룹화
            if owner not in accounts_by_owner_and_type:
                accounts_by_owner_and_type[owner] = {}
            
            # 계좌타입별 그룹화
            if account_type not in accounts_by_owner_and_type[owner]:
                accounts_by_owner_and_type[owner][account_type] = []
            
            # 계좌 잔액 정보 찾기
            balance_info = None
            for balance in account_balances:
                if balance.account == account.account_name:
                    balance_info = balance
                    break
            
            # 계좌 보유 종목 찾기
            account_holdings = []
            total_current_value = 0  # 실시간 가격 기반 총 주식 가치
            for holding in holdings:
                if holding.account == account.account_name:
                    account_holdings.append({
                        "security": holding.security,
                        "shares": holding.shares,
                        "avg_price": holding.avg_price,
                        "total_cost": holding.total_cost,
                        "current_price": holding.current_price,
                        "current_value": holding.current_value,
                        "unrealized_gain_loss": holding.unrealized_gain_loss,
                        "unrealized_gain_loss_rate": holding.unrealized_gain_loss_rate
                    })
                    total_current_value += holding.current_value
            
            # 소유자 이름 제거한 계좌명 생성
            clean_account_name = account.account_name.replace(account_info["owner"] + " ", "")
            
            # 현금 잔액
            cash_balance = balance_info.cash_balance if balance_info else 0
            
            # 총 잔액 = 현금 잔액 + 실시간 주식 가치
            total_balance = cash_balance + total_current_value
            
            accounts_by_owner_and_type[owner][account_type].append({
                "account_name": clean_account_name,
                "full_account_name": account.account_name,
                "owner": account_info["owner"],
                "broker": account_info["broker"],
                "balance": cash_balance,
                "stock_value": total_current_value,
                "total_balance": total_balance,
                "holdings": account_holdings
            })
        
        # 소유자별, 계좌타입별로 투자금과 손익 계산
        for owner, owner_accounts in accounts_by_owner_and_type.items():
            for account_type, account_list in owner_accounts.items():
                for account in account_list:
                    total_investment = sum(h["total_cost"] for h in account["holdings"])
                    total_gain_loss = sum(h["unrealized_gain_loss"] for h in account["holdings"])
                    
                    account["total_investment"] = total_investment
                    account["total_gain_loss"] = total_gain_loss
        
        return {
            "accounts_by_owner_and_type": accounts_by_owner_and_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"계좌별 상세 정보 조회 실패: {str(e)}")

def should_include_account(account_info: Dict[str, str], owner: Optional[str], broker: Optional[str], account_type: Optional[str]) -> bool:
    """계좌가 필터 조건에 맞는지 확인"""
    if owner and account_info["owner"] != owner:
        return False
    if broker and account_info["broker"] != broker:
        return False
    if account_type and account_info["account_type"] != account_type:
        return False
    return True

@app.get("/returns/yearly/{session_id}", response_model=List[YearlyReturnsDetailResponse])
async def get_yearly_returns(session_id: str):
    """연도별 수익 내역 조회 (배당금, 매도 차익, 이자)"""
    try:
        parser = get_parser(session_id)
        yearly_returns = parser.get_yearly_returns()
        
        return [YearlyReturnsDetailResponse(
            year=yr.year,
            total_dividend=yr.total_dividend,
            total_sell_profit=yr.total_sell_profit,
            total_sell_revenue=yr.total_sell_revenue,
            total_sell_cost=yr.total_sell_cost,
            total_interest=yr.total_interest,
            total_returns=yr.total_returns,
            by_security=yr.by_security,
            by_owner_and_account=yr.by_owner_and_account
        ) for yr in yearly_returns]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연도별 수익 내역 조회 실패: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 기존 CSV 파일 로드"""
    load_existing_csv()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

