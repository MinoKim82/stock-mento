from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import tempfile
import uuid
import shutil
from pathlib import Path

# pp 패키지에서 데이터 처리 클래스와 모델 import
from pp import (
    TransactionParser,
    AccountInfo,
    StockHolding,
    DividendInfo,
    InterestInfo,
    TradingPeriodReturn,
    AccountBalance,
    TotalBalance
)

# Yahoo API 임포트
try:
    from yahoo import get_yahoo_price_service
    YAHOO_AVAILABLE = True
except ImportError:
    YAHOO_AVAILABLE = False

app = FastAPI(title="Stock Portfolio API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙을 위한 설정
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# 업로드된 파일들을 저장할 임시 디렉토리
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 세션별 TransactionParser 인스턴스를 저장하는 딕셔너리
parsers: Dict[str, TransactionParser] = {}

# CSV 파일 업로드 및 세션 관리 API
@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """CSV 파일을 업로드하고 세션 ID를 반환"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")
    
    # 세션 ID 생성
    session_id = str(uuid.uuid4())
    
    # 파일 저장
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}.csv")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # TransactionParser 인스턴스 생성
        parser = TransactionParser(file_path, enable_real_time_prices=True, use_yahoo=True)
        parsers[session_id] = parser
        
        return {"session_id": session_id, "message": "CSV 파일이 성공적으로 업로드되었습니다."}
    except Exception as e:
        # 파일 삭제
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"CSV 파일 처리 중 오류가 발생했습니다: {str(e)}")

def get_parser(session_id: str) -> TransactionParser:
    """세션 ID로 TransactionParser 인스턴스를 가져옴"""
    if session_id not in parsers:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다. CSV 파일을 다시 업로드해주세요.")
    return parsers[session_id]

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

@app.get("/")
async def root():
    return {"message": "Stock Portfolio API"}

@app.get("/summary")
async def get_transaction_summary():
    """거래 내역 요약 정보"""
    try:
        summary = parser.get_transaction_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/balances/all", response_model=List[AccountBalanceResponse])
async def get_all_account_balances():
    """모든 계좌의 잔액 정보"""
    try:
        balances = parser.get_all_account_balances()
        return [AccountBalanceResponse(
            account=balance.account,
            cash_balance=balance.cash_balance,
            stock_value=balance.stock_value,
            total_balance=balance.total_balance
        ) for balance in balances]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/balances/account/{account_name}", response_model=AccountBalanceResponse)
async def get_account_balance(account_name: str):
    """특정 계좌의 잔액 정보"""
    try:
        balance = parser.get_account_balance(account_name)
        return AccountBalanceResponse(
            account=balance.account,
            cash_balance=balance.cash_balance,
            stock_value=balance.stock_value,
            total_balance=balance.total_balance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/balances/total", response_model=TotalBalanceResponse)
async def get_total_balance():
    """전체 잔액 정보"""
    try:
        total_balance = parser.get_total_balance()
        return TotalBalanceResponse(
            total_cash_balance=total_balance.total_cash_balance,
            total_stock_value=total_balance.total_stock_value,
            total_balance=total_balance.total_balance,
            account_count=total_balance.account_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

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


@app.get("/holdings/all", response_model=List[StockHoldingResponse])
async def get_all_stock_holdings():
    """전체 주식 보유 목록"""
    try:
        holdings = parser.get_all_stock_holdings()
        return [StockHoldingResponse(
            security=holding.security,
            shares=holding.shares,
            account=holding.account
        ) for holding in holdings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/holdings/by-account/{account_name}", response_model=List[StockHoldingResponse])
async def get_holdings_by_account(account_name: str):
    """계좌별 주식 보유 목록"""
    try:
        holdings = parser.get_holdings_by_account(account_name)
        return [StockHoldingResponse(
            security=holding.security,
            shares=holding.shares,
            account=holding.account
        ) for holding in holdings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/dividends/by-account", response_model=List[DividendInfoResponse])
async def get_dividends_by_account():
    """계좌별/주식별 배당 수익"""
    try:
        dividends = parser.get_dividends_by_account()
        return [DividendInfoResponse(
            account=div.account,
            security=div.security,
            total_dividend=div.total_dividend
        ) for div in dividends]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/interest/by-account", response_model=List[InterestInfoResponse])
async def get_interest_by_account():
    """계좌별 이자 수익"""
    try:
        interests = parser.get_interest_by_account()
        return [InterestInfoResponse(
            account=interest.account,
            total_interest=interest.total_interest
        ) for interest in interests]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 처리 실패: {str(e)}")

@app.get("/returns/trading-period", response_model=List[TradingPeriodReturnResponse])
async def get_trading_period_returns():
    """거래 기간별 수익"""
    try:
        returns = parser.get_trading_period_returns()
        return [TradingPeriodReturnResponse(
            account=ret.account,
            total_return=ret.total_return,
            return_percentage=ret.return_percentage
        ) for ret in returns]
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
@app.get("/portfolio/summary")
async def get_portfolio_summary():
    """포트폴리오 전체 요약"""
    try:
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

@app.get("/portfolio/performance")
async def get_portfolio_performance():
    """포트폴리오 성과 분석"""
    try:
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

@app.get("/portfolio/risk")
async def get_portfolio_risk():
    """포트폴리오 위험 분석"""
    try:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
