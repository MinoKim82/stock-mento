"""
API 응답 모델
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Account Models
class AccountInfoResponse(BaseModel):
    owner: str
    broker: str
    account_type: str
    account_name: str

class StockHoldingResponse(BaseModel):
    security: str
    shares: float
    average_price: float
    total_cost: float
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None

class AccountBalanceResponse(BaseModel):
    account_name: str
    balance: float

class TotalBalanceResponse(BaseModel):
    total_balance: float
    by_account: Dict[str, float]

# Income Models
class DividendInfoResponse(BaseModel):
    date: str
    account_name: str
    security: str
    amount: float

class InterestInfoResponse(BaseModel):
    date: str
    account_name: str
    amount: float

class TradingPeriodReturnResponse(BaseModel):
    account_name: str
    security: str
    total_profit_loss: float

class YearlyReturnsDetailResponse(BaseModel):
    year: int
    total_dividend: float
    total_interest: float
    total_sell_profit: float
    total_sell_revenue: float
    total_sell_cost: float
    by_owner_and_account: Dict[str, Any]

# Stock Price Models
class StockPriceResponse(BaseModel):
    symbol: str
    price: Optional[float]
    currency: str
    error: Optional[str] = None

class MarketStatusResponse(BaseModel):
    market: str
    is_open: bool
    next_open: Optional[str] = None
    next_close: Optional[str] = None

class SymbolSearchResponse(BaseModel):
    query: str
    suggestions: List[str]

# Session Models
class SessionInfoResponse(BaseModel):
    session_id: str
    message: str

class CacheInfo(BaseModel):
    csv_file: Optional[str]
    parsed_data_file: Optional[str]
    has_data: bool
    has_parsed_data: bool
    sessions: List[str]
    total_sessions: int
    total_cache_size: int
    total_cache_size_mb: float

# Chat Models
class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "gemini"

class ChatResponse(BaseModel):
    response: str
    history: List[Dict[str, Any]]

class ChatSessionInfo(BaseModel):
    session_id: str
    provider: str
    message_count: int
    storage_path: str
    created_at: Optional[str]
    updated_at: Optional[str]

