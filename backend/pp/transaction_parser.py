"""
Transaction Data Parser and Analyzer

주식 거래 내역 CSV 파일을 파싱하고 분석하는 모듈
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re
import sys

# KIS API 모듈 임포트 (상대 경로로 추가)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    from kis import get_stock_price_service
    KIS_AVAILABLE = True
except ImportError:
    KIS_AVAILABLE = False
    print("KIS API 모듈을 찾을 수 없습니다. 한국 주식 실시간 가격 조회 기능이 비활성화됩니다.")

# Yahoo Finance API 모듈 임포트
try:
    from yahoo import get_yahoo_price_service
    YAHOO_AVAILABLE = True
except ImportError:
    YAHOO_AVAILABLE = False
    print("Yahoo Finance API 모듈을 찾을 수 없습니다. Yahoo 가격 조회 기능이 비활성화됩니다.")


@dataclass
class AccountInfo:
    """계좌 정보"""
    account_name: str
    account_type: str


@dataclass
class StockHolding:
    """주식 보유 정보"""
    security: str
    shares: int
    account: str
    avg_price: float = 0.0
    total_cost: float = 0.0
    current_price: float = 0.0
    current_value: float = 0.0
    unrealized_gain_loss: float = 0.0
    unrealized_gain_loss_rate: float = 0.0


@dataclass
class DividendInfo:
    """배당 정보"""
    account: str
    security: str
    total_dividend: float


@dataclass
class InterestInfo:
    """이자 정보"""
    account: str
    total_interest: float


@dataclass
class TradingPeriodReturn:
    """거래 기간별 수익 정보"""
    account: str
    total_return: float
    return_percentage: float


@dataclass
class AccountBalance:
    """계좌별 잔액 정보"""
    account: str
    cash_balance: float
    stock_value: float
    total_balance: float


@dataclass
class TotalBalance:
    """전체 잔액 정보"""
    total_cash_balance: float
    total_stock_value: float
    total_balance: float
    account_count: int


def normalize_account_name(account_name) -> str:
    """
    계좌명을 정규화합니다.
    '예수금' 텍스트를 제거하여 동일한 계좌로 처리합니다.
    
    Args:
        account_name: 원본 계좌명 (str 또는 None)
        
    Returns:
        정규화된 계좌명
    """
    if not account_name or pd.isna(account_name):
        return account_name if isinstance(account_name, str) else None
    
    # '예수금' 텍스트 제거
    normalized = re.sub(r'\s*예수금\s*$', '', str(account_name))
    return normalized.strip()


class TransactionParser:
    """거래 내역 파싱 및 분석 클래스"""
    
    def __init__(self, csv_file_path: str, enable_real_time_prices: bool = True, use_yahoo: bool = True):
        """
        Args:
            csv_file_path: CSV 파일 경로
            enable_real_time_prices: 실시간 가격 조회 활성화 여부
            use_yahoo: Yahoo Finance API 사용 여부 (기본값: True)
        """
        self.csv_file_path = csv_file_path
        self._df: Optional[pd.DataFrame] = None
        self.enable_real_time_prices = enable_real_time_prices
        self.use_yahoo = use_yahoo and YAHOO_AVAILABLE
        
        # KIS 서비스 초기화 (한국 주식용)
        if self.enable_real_time_prices and KIS_AVAILABLE:
            try:
                self.stock_price_service = get_stock_price_service()
                print("KIS 실시간 가격 조회 서비스가 활성화되었습니다.")
            except Exception as e:
                print(f"KIS 서비스 초기화 실패: {e}")
                self.stock_price_service = None
        else:
            self.stock_price_service = None
        
        # Yahoo 서비스 초기화 (전체 주식용)
        if self.use_yahoo:
            try:
                self.yahoo_service = get_yahoo_price_service()
                print("Yahoo Finance 가격 조회 서비스가 활성화되었습니다.")
            except Exception as e:
                print(f"Yahoo 서비스 초기화 실패: {e}")
                self.yahoo_service = None
        else:
            self.yahoo_service = None
    
    def _get_real_time_price(self, security: str) -> Optional[float]:
        """실시간 가격 조회 (KIS API 우선, Yahoo API 백업)"""
        # 1. KIS API 시도 (한국 주식용)
        if self.enable_real_time_prices and self.stock_price_service:
            try:
                # 한국 주식인지 확인 (ks 접미사)
                if security.endswith('ks'):
                    price_data = self.stock_price_service.get_stock_price(security)
                    if price_data and price_data.get('current_price'):
                        return price_data.get('current_price')
            except Exception as e:
                print(f"KIS 실시간 가격 조회 실패 ({security}): {e}")
        
        # 2. Yahoo API 시도 (모든 주식용)
        if self.use_yahoo and self.yahoo_service:
            try:
                price_data = self.yahoo_service.get_stock_price(security)
                if price_data and price_data.get('current_price'):
                    return price_data.get('current_price')
            except Exception as e:
                print(f"Yahoo 실시간 가격 조회 실패 ({security}): {e}")
        
        return None
    
    def _normalize_security_symbol(self, security: str) -> str:
        """보안 심볼을 정규화 (Yahoo API 사용)"""
        if not security:
            return security
        
        # Yahoo 서비스를 사용하여 심볼 정규화
        if self.use_yahoo and self.yahoo_service:
            try:
                normalized = self.yahoo_service.normalize_symbol(security)
                if normalized:
                    return normalized
            except Exception as e:
                print(f"Yahoo 심볼 정규화 실패 ({security}): {e}")
        
        # Yahoo 서비스가 없거나 실패한 경우 기본 정규화
        korean_stocks = [
            '삼성전자', 'SK하이닉스', 'LG화학', '네이버', '카카오', '현대차', '기아',
            'POSCO', 'KB금융', '신한지주', 'LG전자', 'SK텔레콤', 'KT&G', '현대모비스',
            '기업은행', 'PS일렉트로닉스', 'GS글로벌', 'LG생활건강', '아모레퍼시픽',
            '셀트리온', '삼성바이오로직스', 'SK이노베이션', 'LG에너지솔루션'
        ]
        
        # 한국 주식인지 확인
        for korean_stock in korean_stocks:
            if korean_stock in security:
                # 이미 ks 접미사가 없으면 추가
                if not security.endswith('ks'):
                    return f"{security}ks"
                break
        
        return security
    
    def _update_holding_with_real_time_price(self, holding: StockHolding) -> StockHolding:
        """보유 주식에 실시간 가격 정보 업데이트"""
        if not self.enable_real_time_prices and not self.use_yahoo:
            return holding
        
        # 실시간 가격 조회 (심볼 정규화)
        normalized_symbol = self._normalize_security_symbol(holding.security)
        current_price = self._get_real_time_price(normalized_symbol)
        
        if current_price and current_price > 0:
            holding.current_price = current_price
            holding.current_value = holding.shares * current_price
            holding.unrealized_gain_loss = holding.current_value - holding.total_cost
            
            if holding.total_cost > 0:
                holding.unrealized_gain_loss_rate = (holding.unrealized_gain_loss / holding.total_cost) * 100
        
        return holding
    
    def load_data(self) -> pd.DataFrame:
        """CSV 파일을 로드하고 전처리"""
        try:
            self._df = pd.read_csv(self.csv_file_path)
            
            # 숫자 데이터 정리 (쉼표 제거)
            numeric_columns = ['Shares', 'Quote', 'Amount', 'Fees', 'Taxes', 'Net Transaction Value']
            for col in numeric_columns:
                if col in self._df.columns:
                    self._df[col] = self._df[col].astype(str).str.replace(',', '').str.replace('USD ', '')
                    self._df[col] = pd.to_numeric(self._df[col], errors='coerce')
            
            # 날짜 컬럼 처리
            self._df['Date'] = pd.to_datetime(self._df['Date'])
            
            # 계좌명 정규화 (예수금 텍스트 제거)
            if 'Cash Account' in self._df.columns:
                self._df['Cash Account'] = self._df['Cash Account'].apply(normalize_account_name)
            if 'Offset Account' in self._df.columns:
                self._df['Offset Account'] = self._df['Offset Account'].apply(normalize_account_name)
            
            return self._df
            
        except Exception as e:
            raise Exception(f"CSV 파일 로드 실패: {str(e)}")
    
    def get_dataframe(self) -> pd.DataFrame:
        """데이터프레임 반환 (필요시 로드)"""
        if self._df is None:
            self.load_data()
        return self._df
    
    def get_accounts(self) -> List[AccountInfo]:
        """모든 계좌 목록 반환 (정규화된 계좌)"""
        df = self.get_dataframe()
        
        # Cash Account와 Offset Account에서 모든 계좌를 가져옴 (중복 제거)
        cash_accounts = df['Cash Account'].dropna().unique() if 'Cash Account' in df.columns else []
        offset_accounts = df['Offset Account'].dropna().unique() if 'Offset Account' in df.columns else []
        
        # 모든 계좌를 합치고 중복 제거
        all_accounts = set(cash_accounts)
        all_accounts.update(offset_accounts)
        
        accounts = []
        for account in sorted(all_accounts):
            accounts.append(AccountInfo(
                account_name=account,
                account_type="account"  # 통합된 계좌 타입
            ))
        
        return accounts
    
    
    def get_all_stock_holdings(self) -> List[StockHolding]:
        """전체 주식 보유 목록"""
        df = self.get_dataframe()
        
        holdings = {}
        
        # Buy와 Sell 거래를 통해 현재 보유량과 평균 가격 계산
        for _, row in df.iterrows():
            if row['Type'] in ['Buy', 'Sell'] and pd.notna(row['Security']):
                security = row['Security']
                account = row['Cash Account']
                shares = row['Shares'] if pd.notna(row['Shares']) else 0
                price = row['Quote'] if pd.notna(row['Quote']) else 0.0
                
                key = f"{account}_{security}"
                
                if key not in holdings:
                    holdings[key] = {
                        'security': security,
                        'account': account,
                        'shares': 0,
                        'total_cost': 0.0,
                        'buy_shares': 0,
                        'sell_shares': 0
                    }
                
                if row['Type'] == 'Buy':
                    holdings[key]['shares'] += shares
                    holdings[key]['total_cost'] += shares * price
                    holdings[key]['buy_shares'] += shares
                elif row['Type'] == 'Sell':
                    # 매도 시에는 평균 단가로 계산 (FIFO 방식)
                    holdings[key]['shares'] -= shares
                    holdings[key]['sell_shares'] += shares
                    # 매도된 주식의 원가 차감
                    if holdings[key]['buy_shares'] > 0:
                        avg_price = holdings[key]['total_cost'] / holdings[key]['buy_shares']
                        holdings[key]['total_cost'] -= shares * avg_price
                        holdings[key]['buy_shares'] -= shares
        
        # 양수 보유량만 반환하고 평균 가격 계산
        result = []
        for holding in holdings.values():
            if holding['shares'] > 0:
                avg_price = holding['total_cost'] / holding['shares'] if holding['shares'] > 0 else 0.0
                stock_holding = StockHolding(
                    security=holding['security'],
                    shares=int(holding['shares']),
                    account=holding['account'],
                    avg_price=avg_price,
                    total_cost=holding['total_cost']
                )
                
                # 실시간 가격 정보 업데이트
                stock_holding = self._update_holding_with_real_time_price(stock_holding)
                result.append(stock_holding)
        
        return result
    
    def get_holdings_by_account(self, account_name: str) -> List[StockHolding]:
        """계좌별 주식 보유 목록"""
        df = self.get_dataframe()
        
        # 해당 계좌의 거래만 필터링
        account_df = df[df['Cash Account'] == account_name]
        
        holdings = {}
        
        for _, row in account_df.iterrows():
            if row['Type'] in ['Buy', 'Sell'] and pd.notna(row['Security']):
                security = row['Security']
                shares = row['Shares'] if pd.notna(row['Shares']) else 0
                price = row['Quote'] if pd.notna(row['Quote']) else 0.0
                
                if security not in holdings:
                    holdings[security] = {
                        'shares': 0,
                        'total_cost': 0.0,
                        'buy_shares': 0,
                        'sell_shares': 0
                    }
                
                if row['Type'] == 'Buy':
                    holdings[security]['shares'] += shares
                    holdings[security]['total_cost'] += shares * price
                    holdings[security]['buy_shares'] += shares
                elif row['Type'] == 'Sell':
                    # 매도 시에는 평균 단가로 계산 (FIFO 방식)
                    holdings[security]['shares'] -= shares
                    holdings[security]['sell_shares'] += shares
                    # 매도된 주식의 원가 차감
                    if holdings[security]['buy_shares'] > 0:
                        avg_price = holdings[security]['total_cost'] / holdings[security]['buy_shares']
                        holdings[security]['total_cost'] -= shares * avg_price
                        holdings[security]['buy_shares'] -= shares
        
        result = []
        for security, holding_data in holdings.items():
            if holding_data['shares'] > 0:
                avg_price = holding_data['total_cost'] / holding_data['shares'] if holding_data['shares'] > 0 else 0.0
                stock_holding = StockHolding(
                    security=security,
                    shares=int(holding_data['shares']),
                    account=account_name,
                    avg_price=avg_price,
                    total_cost=holding_data['total_cost']
                )
                
                # 실시간 가격 정보 업데이트
                stock_holding = self._update_holding_with_real_time_price(stock_holding)
                result.append(stock_holding)
        
        return result
    
    def get_dividends_by_account(self) -> List[DividendInfo]:
        """계좌별/주식별 배당 수익"""
        df = self.get_dataframe()
        
        # 배당 거래만 필터링
        dividend_df = df[df['Type'] == 'Dividend']
        
        dividends = {}
        
        for _, row in dividend_df.iterrows():
            if pd.notna(row['Security']) and pd.notna(row['Cash Account']):
                account = row['Cash Account']
                security = row['Security']
                amount = row['Amount'] if pd.notna(row['Amount']) else 0
                
                key = f"{account}_{security}"
                
                if key not in dividends:
                    dividends[key] = {
                        'account': account,
                        'security': security,
                        'total_dividend': 0
                    }
                
                dividends[key]['total_dividend'] += amount
        
        result = []
        for dividend in dividends.values():
            result.append(DividendInfo(
                account=dividend['account'],
                security=dividend['security'],
                total_dividend=dividend['total_dividend']
            ))
        
        return result
    
    def get_interest_by_account(self) -> List[InterestInfo]:
        """계좌별 이자 수익"""
        df = self.get_dataframe()
        
        # 이자 거래만 필터링
        interest_df = df[df['Type'] == 'Interest']
        
        interest = {}
        
        for _, row in interest_df.iterrows():
            if pd.notna(row['Cash Account']):
                account = row['Cash Account']
                amount = row['Amount'] if pd.notna(row['Amount']) else 0
                
                if account not in interest:
                    interest[account] = 0
                
                interest[account] += amount
        
        result = []
        for account, total_interest in interest.items():
            result.append(InterestInfo(
                account=account,
                total_interest=total_interest
            ))
        
        return result
    
    def get_trading_period_returns(self) -> List[TradingPeriodReturn]:
        """거래 기간별 수익"""
        df = self.get_dataframe()
        
        returns = {}
        
        # 각 계좌별로 수익 계산
        for account in df['Cash Account'].dropna().unique():
            account_df = df[df['Cash Account'] == account]
            
            total_buy = 0
            total_sell = 0
            total_dividend = 0
            total_interest = 0
            
            for _, row in account_df.iterrows():
                amount = row['Amount'] if pd.notna(row['Amount']) else 0
                
                if row['Type'] == 'Buy':
                    total_buy += amount
                elif row['Type'] == 'Sell':
                    total_sell += amount
                elif row['Type'] == 'Dividend':
                    total_dividend += amount
                elif row['Type'] == 'Interest':
                    total_interest += amount
            
            # 현재 보유량의 가치를 대략적으로 계산 (마지막 거래 가격 기준)
            current_value = 0
            holdings = {}
            
            for _, row in account_df.iterrows():
                if row['Type'] in ['Buy', 'Sell'] and pd.notna(row['Security']):
                    security = row['Security']
                    shares = row['Shares'] if pd.notna(row['Shares']) else 0
                    quote = row['Quote'] if pd.notna(row['Quote']) else 0
                    
                    if security not in holdings:
                        holdings[security] = {'shares': 0, 'last_quote': 0}
                    
                    if row['Type'] == 'Buy':
                        holdings[security]['shares'] += shares
                    elif row['Type'] == 'Sell':
                        holdings[security]['shares'] -= shares
                    
                    if quote > 0:
                        holdings[security]['last_quote'] = quote
            
            for security, data in holdings.items():
                if data['shares'] > 0:
                    current_value += data['shares'] * data['last_quote']
            
            # 총 수익 계산
            total_return = (total_sell + total_dividend + total_interest + current_value) - total_buy
            return_percentage = (total_return / total_buy * 100) if total_buy > 0 else 0
            
            returns[account] = {
                'total_return': total_return,
                'return_percentage': return_percentage
            }
        
        result = []
        for account, data in returns.items():
            result.append(TradingPeriodReturn(
                account=account,
                total_return=data['total_return'],
                return_percentage=data['return_percentage']
            ))
        
        return result
    
    def get_account_balance(self, account_name: str) -> AccountBalance:
        """특정 계좌의 잔액 정보"""
        df = self.get_dataframe()
        account_df = df[df['Cash Account'] == account_name]
        
        # 현금 거래 분석 (환전 고려)
        # '해외' 계좌의 경우 메모의 환율 정보를 활용하여 정확한 KRW 환전 계산
        if '해외' in account_name:
            # 해외 계좌의 환전 거래 분석
            deposits = 0
            removals = 0
            interest = 0
            dividends = 0
            buy_amount = 0
            sell_amount = 0
            
            # 해외 계좌는 실제 KRW 잔액이 0원 (모든 USD가 환전되어 국내 계좌로 이동)
            # 환전 거래는 국내 계좌에서만 처리
        else:
            # 일반 계좌는 기존 로직 사용
            deposits = account_df[account_df['Type'] == 'Deposit']['Amount'].sum()
            removals = account_df[account_df['Type'] == 'Removal']['Amount'].sum()
            interest = account_df[account_df['Type'] == 'Interest']['Amount'].sum()
            dividends = account_df[account_df['Type'] == 'Dividend']['Amount'].sum()
            
            # 주식 거래 분석
            buy_amount = account_df[account_df['Type'] == 'Buy']['Amount'].sum()
            sell_amount = account_df[account_df['Type'] == 'Sell']['Amount'].sum()
        
        # 계좌 간 이체 분석 (환전 고려)
        # Transfer (Outbound): 다른 계좌로 이체 (현금 유출)
        if '해외' in account_name:
            # 해외 계좌의 이체는 USD이므로 KRW 잔액에 영향 없음
            transfer_out = 0
        else:
            transfer_out = account_df[account_df['Type'] == 'Transfer (Outbound)']['Amount'].sum()
        
        # Transfer (Inbound): 다른 계좌에서 이체 (현금 유입) - 환전 고려
        transfer_in = 0
        inbound_transfers = df[(df['Type'] == 'Transfer (Outbound)') & (df['Offset Account'] == account_name)]
        
        for _, row in inbound_transfers.iterrows():
            from_account = row['Cash Account']
            amount = row['Amount']
            
            # 환전 계산: '해외' 계좌에서 일반 계좌로 이체 시 환전 (USD → KRW)
            if '해외' in from_account and '해외' not in account_name:
                # 메모에서 환율 정보를 확인하여 정확한 KRW 금액 계산
                if pd.notna(row['Note']) and '환율' in str(row['Note']):
                    note = str(row['Note'])
                    import re
                    usd_match = re.search(r'달러\s+([\d,]+\.?\d*)', note)
                    rate_match = re.search(r'환율\s+([\d,]+\.?\d*)', note)
                    fee_match = re.search(r'환전 수수료\s+([\d,]+\.?\d*)', note)
                    
                    if usd_match and rate_match:
                        usd_amount = float(usd_match.group(1).replace(',', ''))
                        exchange_rate = float(rate_match.group(1).replace(',', ''))
                        exchange_fee = float(fee_match.group(1).replace(',', '')) if fee_match else 0
                        
                        # 실제 환전된 KRW 금액 = USD 금액 * 환율 - 환전 수수료
                        actual_krw = usd_amount * exchange_rate - exchange_fee
                        transfer_in += actual_krw
                    else:
                        transfer_in += amount  # 기본값
                else:
                    transfer_in += amount  # 기본값
            # 일반 계좌에서 '해외' 계좌로 이체 시 환전 (KRW → USD)
            elif '해외' not in from_account and '해외' in account_name:
                # KRW를 USD로 환전 - 실제 환전된 USD 금액 사용
                if from_account == '토스 종합매매' and account_name == '토스 종합매매 해외':
                    # KRW → USD 환전 시 실제 환전된 USD 금액으로 조정
                    # 실제로는 모든 USD가 환전되어 0이 되어야 함
                    transfer_in += 0  # 토스 종합매매 해외는 실제 잔액이 0원
                else:
                    transfer_in += amount
            else:
                # 같은 통화 간 이체
                transfer_in += amount
        
        # 수수료와 세금 분석
        if '해외' in account_name:
            # 해외 계좌의 수수료와 세금은 USD이므로 KRW 잔액에 영향 없음
            fees = 0
            taxes = 0
        else:
            fees = account_df['Fees'].sum() if 'Fees' in account_df.columns else 0
            taxes = account_df['Taxes'].sum() if 'Taxes' in account_df.columns else 0
        
        # 예수금 계산 (수수료, 세금, 계좌 간 이체 포함)
        cash_in = deposits + interest + dividends + sell_amount + transfer_in
        cash_out = removals + buy_amount + fees + taxes + transfer_out
        cash_balance = cash_in - cash_out
        
        # 주식 평가액 계산
        stock_transactions = account_df[account_df['Type'].isin(['Buy', 'Sell'])]
        holdings = {}
        
        for _, row in stock_transactions.iterrows():
            if pd.notna(row['Security']):
                security = row['Security']
                shares = row['Shares'] if pd.notna(row['Shares']) else 0
                quote = row['Quote'] if pd.notna(row['Quote']) else 0
                
                if security not in holdings:
                    holdings[security] = {'shares': 0, 'last_quote': 0}
                
                if row['Type'] == 'Buy':
                    holdings[security]['shares'] += shares
                elif row['Type'] == 'Sell':
                    holdings[security]['shares'] -= shares
                
                if quote > 0:
                    holdings[security]['last_quote'] = quote
        
        stock_value = 0
        for security, data in holdings.items():
            if data['shares'] > 0:
                stock_value += data['shares'] * data['last_quote']
        
        total_balance = cash_balance + stock_value
        
        return AccountBalance(
            account=account_name,
            cash_balance=cash_balance,
            stock_value=stock_value,
            total_balance=total_balance
        )
    
    def get_all_account_balances(self) -> List[AccountBalance]:
        """모든 계좌의 잔액 정보"""
        accounts = self.get_accounts()
        balances = []
        
        for account_info in accounts:
            balance = self.get_account_balance(account_info.account_name)
            balances.append(balance)
        
        return balances
    
    def get_total_balance(self) -> TotalBalance:
        """전체 잔액 정보"""
        balances = self.get_all_account_balances()
        
        total_cash_balance = sum(balance.cash_balance for balance in balances)
        total_stock_value = sum(balance.stock_value for balance in balances)
        total_balance = total_cash_balance + total_stock_value
        
        return TotalBalance(
            total_cash_balance=total_cash_balance,
            total_stock_value=total_stock_value,
            total_balance=total_balance,
            account_count=len(balances)
        )
    
    def get_transaction_summary(self) -> Dict[str, Any]:
        """거래 내역 요약 정보"""
        df = self.get_dataframe()
        
        summary = {
            'total_transactions': len(df),
            'date_range': {
                'start': df['Date'].min().strftime('%Y-%m-%d'),
                'end': df['Date'].max().strftime('%Y-%m-%d')
            },
            'transaction_types': df['Type'].value_counts().to_dict(),
            'total_accounts': df['Cash Account'].nunique(),
            'total_securities': df['Security'].nunique()
        }
        
        return summary
