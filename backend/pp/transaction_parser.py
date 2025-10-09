"""
Transaction Data Parser and Analyzer

주식 거래 내역 CSV 파일을 파싱하고 분석하는 모듈
"""

import pandas as pd
import re
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class AccountInfo:
    """계좌 정보"""
    account_name: str
    owner: str
    broker: str
    account_type: str


@dataclass
class StockHolding:
    """주식 보유 정보"""
    account: str
    security: str
    shares: float
    avg_price: float
    total_cost: float


@dataclass
class AccountBalance:
    """계좌 잔액 정보"""
    account: str
    cash_balance: float


@dataclass
class DividendInfo:
    """배당 수익 정보"""
    account: str
    security: str
    total_dividend: float


@dataclass
class InterestInfo:
    """이자 수익 정보"""
    account: str
    total_interest: float


@dataclass
class TradingPeriodReturn:
    """거래 기간별 수익 정보"""
    account: str
    total_return: float
    return_percentage: float


@dataclass
class AccountBalanceDetail:
    """계좌 잔액 상세 정보 (현금 + 주식)"""
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


@dataclass
class StockHoldingWithPrice:
    """주식 보유 정보 (현재 가격 포함)"""
    account: str
    security: str
    shares: float
    avg_price: float
    total_cost: float
    current_price: float
    current_value: float
    unrealized_gain_loss: float
    unrealized_gain_loss_rate: float


@dataclass
class YearlyReturnsDetail:
    """연도별 수익 내역"""
    year: int
    total_dividend: float
    total_sell_profit: float
    total_interest: float
    total_returns: float
    by_security: dict  # Dict[str, Dict[str, float]]
    by_owner_and_account: dict  # Dict[str, Dict[str, Dict[str, Dict[str, float]]]]


def normalize_account_name(account_name) -> str:
    """
    계좌명을 정규화합니다.
    '예수금' 텍스트를 제거하여 동일한 계좌로 처리합니다.
    
    Example:
        "민호 토스 종합매매 예수금" -> "민호 토스 종합매매"
    
    Args:
        account_name: 원본 계좌명
        
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
    
    def __init__(self, csv_file_path: str, yahoo_client=None):
        """
        Args:
            csv_file_path: CSV 파일 경로
            yahoo_client: Yahoo Finance API 클라이언트 (선택적)
        """
        self.csv_file_path = csv_file_path
        self._df: Optional[pd.DataFrame] = None
        self.yahoo_client = yahoo_client
    
    def load_data(self) -> pd.DataFrame:
        """
        CSV 파일을 로드하고 전처리
        
        처리 순서:
        1. CSV 파일 읽기
        2. 계좌명 정규화 (Cash Account, Offset Account에서 '예수금' 제거)
        3. Currency 컬럼 추가 (Amount에서 USD/KRW 구분)
        4. 숫자 컬럼 정리 (쉼표, 통화 코드 제거하고 숫자만 추출)
        5. 날짜 컬럼 변환
        
        Returns:
            전처리된 DataFrame
        """
        try:
            # 1. CSV 파일 읽기
            self._df = pd.read_csv(self.csv_file_path)
            
            # 2. 계좌명 정규화
            # Cash Account와 Offset Account에서 '예수금' 텍스트 제거
            # 예: "민호 토스 종합매매 예수금" -> "민호 토스 종합매매"
            if 'Cash Account' in self._df.columns:
                self._df['Cash Account'] = self._df['Cash Account'].apply(normalize_account_name)
            
            if 'Offset Account' in self._df.columns:
                self._df['Offset Account'] = self._df['Offset Account'].apply(normalize_account_name)
            
            # 3. Currency 컬럼 추가
            # Amount 값에 'USD'가 포함되어 있으면 USD, 아니면 KRW
            def extract_currency(val):
                if pd.isna(val) or val == '':
                    return 'KRW'
                if 'USD' in str(val):
                    return 'USD'
                return 'KRW'
            
            self._df['Currency'] = self._df['Amount'].apply(extract_currency)
            
            # 4. 숫자 컬럼 정리
            # 쉼표와 통화 코드(USD, KRW)를 제거하고 숫자만 추출
            numeric_columns = ['Shares', 'Quote', 'Amount', 'Fees', 'Taxes', 'Net Transaction Value']
            
            for col in numeric_columns:
                if col in self._df.columns:
                    def convert_numeric(val):
                        if pd.isna(val) or val == '':
                            return None
                        # 문자열로 변환 후 통화 코드 제거
                        val_str = str(val).replace('USD', '').replace('KRW', '').replace(',', '').strip()
                        try:
                            return float(val_str)
                        except:
                            return None
                    
                    self._df[col] = self._df[col].apply(convert_numeric)
            
            # 5. 날짜 컬럼 변환
            self._df['Date'] = pd.to_datetime(self._df['Date'])
            
            return self._df
            
        except Exception as e:
            raise Exception(f"CSV 파일 로드 실패: {str(e)}")
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        데이터프레임 반환 (필요시 로드)
        
        Returns:
            전처리된 DataFrame
        """
        if self._df is None:
            self.load_data()
        return self._df
    
    def get_accounts(self) -> List[AccountInfo]:
        """
        모든 계좌 목록 반환
        
        Cash Account와 Offset Account에 존재하는 모든 계좌를 수집하고,
        계좌명을 파싱하여 소유자, 증권사, 계좌타입으로 분리합니다.
        
        계좌명 형식: "(소유자) (증권사) (계좌타입)"
        예: "민호 토스 종합매매" -> owner="민호", broker="토스", account_type="종합매매"
        
        Returns:
            AccountInfo 리스트
        """
        df = self.get_dataframe()
        
        # Cash Account와 Offset Account에서 모든 계좌 수집
        all_accounts = set()
        
        if 'Cash Account' in df.columns:
            cash_accounts = df['Cash Account'].dropna().unique()
            all_accounts.update(cash_accounts)
        
        if 'Offset Account' in df.columns:
            offset_accounts = df['Offset Account'].dropna().unique()
            all_accounts.update(offset_accounts)
        
        # 계좌명 파싱하여 AccountInfo 생성
        account_list = []
        
        for account_name in sorted(all_accounts):
            # 계좌명을 공백으로 분리
            # 형식: "(소유자) (증권사) (계좌타입)" 또는 "(소유자) (증권사) (계좌타입) (추가정보)"
            parts = account_name.split()
            
            if len(parts) >= 3:
                owner = parts[0]
                broker = parts[1]
                account_type = ' '.join(parts[2:])  # 나머지는 모두 계좌타입으로
            elif len(parts) == 2:
                owner = parts[0]
                broker = parts[1]
                account_type = "기타"
            elif len(parts) == 1:
                owner = parts[0]
                broker = "기타"
                account_type = "기타"
            else:
                owner = "기타"
                broker = "기타"
                account_type = "기타"
            
            account_list.append(AccountInfo(
                account_name=account_name,
                owner=owner,
                broker=broker,
                account_type=account_type
            ))
        
        return account_list
    
    def get_holdings_by_account(self, account_name: str) -> List[StockHolding]:
        """
        특정 계좌의 보유 종목 반환
        
        Buy/Sell 거래를 분석하여 현재 보유 중인 주식과 평균 매입가를 계산합니다.
        
        계산 로직:
        1. 날짜순으로 거래를 정렬
        2. Buy: 보유 수량 증가, 총 비용 증가
        3. Sell: 보유 수량 감소, 평균 단가 기준으로 총 비용 감소
        4. 보유 수량 > 0인 종목만 반환
        
        Args:
            account_name: 계좌명
            
        Returns:
            StockHolding 리스트 (보유 수량 > 0)
        """
        df = self.get_dataframe()
        
        # 해당 계좌의 거래만 필터링하고 날짜순 정렬
        account_df = df[df['Cash Account'] == account_name].sort_values('Date')
        
        # 종목별 보유 내역
        holdings = {}
        
        for _, row in account_df.iterrows():
            if row['Type'] not in ['Buy', 'Sell']:
                continue
            
            if pd.isna(row['Security']):
                continue
            
            security = row['Security']
            shares = row['Shares'] if pd.notna(row['Shares']) else 0
            price = row['Quote'] if pd.notna(row['Quote']) else 0.0
            
            # 종목이 처음 나타나면 초기화
            if security not in holdings:
                holdings[security] = {
                    'shares': 0,
                    'total_cost': 0.0
                }
            
            if row['Type'] == 'Buy':
                # 매수: 수량과 비용 증가
                holdings[security]['shares'] += shares
                holdings[security]['total_cost'] += shares * price
                
            elif row['Type'] == 'Sell':
                # 매도: 평균 단가로 비용 감소
                if holdings[security]['shares'] > 0:
                    # 현재 평균 단가 계산
                    avg_price = holdings[security]['total_cost'] / holdings[security]['shares']
                    # 매도된 주식의 원가 차감
                    holdings[security]['total_cost'] -= shares * avg_price
                
                # 수량 감소
                holdings[security]['shares'] -= shares
        
        # 보유 수량 > 0인 종목만 StockHolding으로 변환
        result = []
        for security, data in holdings.items():
            if data['shares'] > 0:
                avg_price = data['total_cost'] / data['shares'] if data['shares'] > 0 else 0.0
                
                result.append(StockHolding(
                    account=account_name,
                    security=security,
                    shares=data['shares'],
                    avg_price=avg_price,
                    total_cost=data['total_cost']
                ))
        
        return result
    
    def get_all_holdings(self) -> List[StockHolding]:
        """
        모든 계좌의 보유 종목 반환
        
        Returns:
            모든 계좌의 StockHolding 리스트
        """
        accounts = self.get_accounts()
        all_holdings = []
        
        for account_info in accounts:
            holdings = self.get_holdings_by_account(account_info.account_name)
            all_holdings.extend(holdings)
        
        return all_holdings
    
    def get_account_balance(self, account_name: str) -> AccountBalance:
        """
        특정 계좌의 현금 잔액 계산
        
        계산 로직:
        1. 해외 계좌(USD)는 KRW 잔액 = 0으로 반환
        2. KRW 계좌만 처리
        3. Cash Account 거래:
           - 입금(+): Dividend, Deposit, Interest
           - 출금(-): Removal, Transfer (Outbound)
        4. Offset Account 거래 (Buy/Sell):
           - Buy: 예수금에서 출금(-) - Amount 사용
           - Sell: 예수금으로 입금(+) - Amount 사용
        5. Transfer Inbound (다른 계좌에서 입금):
           - USD → KRW 환전: Note에서 환율 정보 파싱
           - KRW → KRW: Amount 그대로 사용
        
        Args:
            account_name: 계좌명
            
        Returns:
            AccountBalance (현금 잔액)
        """
        df = self.get_dataframe()
        
        # 해외 계좌는 USD이므로 KRW 잔액 = 0
        if '해외' in account_name:
            return AccountBalance(
                account=account_name,
                cash_balance=0.0
            )
        
        cash_balance = 0.0
        
        # 1. Cash Account 거래 처리 (모든 타입)
        # Interest, Buy, Sell, Dividend는 Net Transaction Value 사용
        # Deposit, Removal, Transfer (Outbound)는 Amount 사용
        cash_df = df[(df['Cash Account'] == account_name) & (df['Currency'] == 'KRW')]
        
        for _, row in cash_df.iterrows():
            trans_type = row['Type']
            amount = row['Amount']
            net_value = row['Net Transaction Value']
            
            if pd.notna(amount) or pd.notna(net_value):
                # Net Transaction Value 사용 거래
                if trans_type in ['Interest', 'Sell', 'Dividend'] and pd.notna(net_value):
                    # 입금: Net Transaction Value (Fee, Tax 차감된 금액)
                    cash_balance += net_value
                elif trans_type == 'Buy' and pd.notna(net_value):
                    # 출금: Net Transaction Value (Fee, Tax 포함된 금액)
                    cash_balance -= net_value
                # Amount 사용 거래
                elif trans_type == 'Deposit' and pd.notna(amount):
                    cash_balance += amount
                elif trans_type in ['Removal', 'Transfer (Outbound)'] and pd.notna(amount):
                    cash_balance -= amount
        
        # 2. Offset Account 거래 처리 (Transfer만)
        # Transfer (Outbound)가 Offset Account에 있으면 Transfer Inbound (다른 계좌에서 입금)
        offset_df = df[(df['Offset Account'] == account_name) & (df['Type'] == 'Transfer (Outbound)')]
        
        for _, row in offset_df.iterrows():
            amount = row['Amount']
            currency = row['Currency']
            from_account = row['Cash Account']
            note = row.get('Note', '')
            
            if pd.notna(amount):
                # USD → KRW 환전
                if '해외' in from_account and currency == 'USD':
                    if '환율' in str(note):
                        # Note 형식: "USD 3,065.06 KRW 4,287,974 환율 1,388.99 환전 수수료 18,690"
                        krw_match = re.search(r'KRW\s+([\d,]+)', str(note))
                        
                        if krw_match:
                            # Note에서 KRW 금액 직접 사용
                            krw_amount = float(krw_match.group(1).replace(',', ''))
                            cash_balance += krw_amount
                # KRW → KRW 이체
                elif currency == 'KRW':
                    cash_balance += amount
        
        return AccountBalance(
            account=account_name,
            cash_balance=cash_balance
        )
    
    def get_all_balances(self) -> List[AccountBalance]:
        """
        모든 계좌의 잔액 반환
        
        Returns:
            AccountBalance 리스트
        """
        accounts = self.get_accounts()
        balances = []
        
        for account_info in accounts:
            balance = self.get_account_balance(account_info.account_name)
            balances.append(balance)
        
        return balances
    
    def get_all_dividends(self) -> List[DividendInfo]:
        """
        모든 배당 수익 반환
        
        Returns:
            DividendInfo 리스트
        """
        df = self.get_dataframe()
        dividend_df = df[df['Type'] == 'Dividend'].copy()
        
        # 계좌 및 종목별 배당금 합계
        result = []
        for (account, security), group in dividend_df.groupby(['Cash Account', 'Security']):
            total_dividend = group['Net Transaction Value'].sum()
            result.append(DividendInfo(
                account=account,
                security=security if pd.notna(security) else '기타',
                total_dividend=total_dividend
            ))
        
        return result
    
    def get_dividends_by_account(self, account_name: str) -> List[DividendInfo]:
        """
        특정 계좌의 배당 수익 반환
        
        Args:
            account_name: 계좌명
            
        Returns:
            DividendInfo 리스트
        """
        df = self.get_dataframe()
        dividend_df = df[(df['Type'] == 'Dividend') & (df['Cash Account'] == account_name)].copy()
        
        result = []
        for security, group in dividend_df.groupby('Security'):
            total_dividend = group['Net Transaction Value'].sum()
            result.append(DividendInfo(
                account=account_name,
                security=security if pd.notna(security) else '기타',
                total_dividend=total_dividend
            ))
        
        return result
    
    def get_all_interest(self) -> List[InterestInfo]:
        """
        모든 이자 수익 반환
        
        Returns:
            InterestInfo 리스트
        """
        df = self.get_dataframe()
        interest_df = df[df['Type'] == 'Interest'].copy()
        
        result = []
        for account, group in interest_df.groupby('Cash Account'):
            total_interest = group['Net Transaction Value'].sum()
            result.append(InterestInfo(
                account=account,
                total_interest=total_interest
            ))
        
        return result
    
    def get_all_returns(self) -> List[TradingPeriodReturn]:
        """
        모든 거래 기간별 수익 반환
        
        Returns:
            TradingPeriodReturn 리스트
        """
        df = self.get_dataframe()
        
        result = []
        accounts = self.get_accounts()
        
        for account_info in accounts:
            account_name = account_info.account_name
            account_df = df[df['Cash Account'] == account_name]
            
            # 매도 수익 계산
            sell_df = account_df[account_df['Type'] == 'Sell']
            total_sell_amount = sell_df['Net Transaction Value'].sum() if len(sell_df) > 0 else 0
            
            # 매수 비용 계산
            buy_df = account_df[account_df['Type'] == 'Buy']
            total_buy_cost = buy_df['Net Transaction Value'].sum() if len(buy_df) > 0 else 0
            
            if total_buy_cost > 0:
                total_return = total_sell_amount - total_buy_cost
                return_percentage = (total_return / total_buy_cost) * 100
            else:
                total_return = 0
                return_percentage = 0
            
            result.append(TradingPeriodReturn(
                account=account_name,
                total_return=total_return,
                return_percentage=return_percentage
            ))
        
        return result
    
    def get_all_account_balances(self) -> List[AccountBalanceDetail]:
        """
        모든 계좌의 상세 잔액 반환 (현금 + 주식 가치)
        
        Returns:
            AccountBalanceDetail 리스트
        """
        accounts = self.get_accounts()
        result = []
        
        for account_info in accounts:
            account_name = account_info.account_name
            
            # 현금 잔액
            cash_balance_obj = self.get_account_balance(account_name)
            cash_balance = cash_balance_obj.cash_balance
            
            # 주식 가치 (보유 종목의 총 비용)
            holdings = self.get_holdings_by_account(account_name)
            stock_value = sum(h.total_cost for h in holdings)
            
            total_balance = cash_balance + stock_value
            
            result.append(AccountBalanceDetail(
                account=account_name,
                cash_balance=cash_balance,
                stock_value=stock_value,
                total_balance=total_balance
            ))
        
        return result
    
    def get_total_balance(self) -> TotalBalance:
        """
        전체 잔액 정보 반환
        
        Returns:
            TotalBalance
        """
        account_balances = self.get_all_account_balances()
        
        total_cash = sum(b.cash_balance for b in account_balances)
        total_stock = sum(b.stock_value for b in account_balances)
        total = total_cash + total_stock
        
        return TotalBalance(
            total_cash_balance=total_cash,
            total_stock_value=total_stock,
            total_balance=total,
            account_count=len(account_balances)
        )
    
    def get_all_stock_holdings(self) -> List[StockHoldingWithPrice]:
        """
        모든 주식 보유 정보 반환 (현재 가격 포함)
        
        yahoo_client가 제공된 경우 실시간 가격 조회, 아니면 0으로 반환
        
        Returns:
            StockHoldingWithPrice 리스트
        """
        holdings = self.get_all_holdings()
        result = []
        
        # 실시간 가격 조회 (yahoo_client가 있는 경우)
        price_cache = {}
        if self.yahoo_client:
            # 유니크한 종목 목록 추출
            unique_securities = list(set(h.security for h in holdings))
            
            # 배치로 가격 조회
            for security in unique_securities:
                try:
                    price_info = self.yahoo_client.get_stock_info(security)
                    if price_info:
                        price_cache[security] = price_info.get('current_price', 0)
                    else:
                        price_cache[security] = 0
                except Exception as e:
                    print(f"가격 조회 오류 ({security}): {e}")
                    price_cache[security] = 0
        
        for h in holdings:
            # 현재 가격 조회 (캐시에서 또는 0)
            current_price = price_cache.get(h.security, 0) if price_cache else 0
            current_value = h.shares * current_price
            unrealized_gain_loss = current_value - h.total_cost
            unrealized_gain_loss_rate = (unrealized_gain_loss / h.total_cost * 100) if h.total_cost > 0 else 0
            
            result.append(StockHoldingWithPrice(
                account=h.account,
                security=h.security,
                shares=h.shares,
                avg_price=h.avg_price,
                total_cost=h.total_cost,
                current_price=current_price,
                current_value=current_value,
                unrealized_gain_loss=unrealized_gain_loss,
                unrealized_gain_loss_rate=unrealized_gain_loss_rate
            ))
        
        return result
    
    def get_yearly_returns(self) -> List[YearlyReturnsDetail]:
        """
        연도별 수익 내역 반환
        
        Returns:
            YearlyReturnsDetail 리스트
        """
        df = self.get_dataframe()
        
        # 연도 추출
        df['Year'] = df['Date'].dt.year
        
        yearly_results = []
        
        for year in sorted(df['Year'].unique()):
            year_df = df[df['Year'] == year]
            
            # 배당금
            dividend_df = year_df[year_df['Type'] == 'Dividend']
            total_dividend = dividend_df['Net Transaction Value'].sum() if len(dividend_df) > 0 else 0
            
            # 이자
            interest_df = year_df[year_df['Type'] == 'Interest']
            total_interest = interest_df['Net Transaction Value'].sum() if len(interest_df) > 0 else 0
            
            # 매도 차익 (매도 금액 - 매도한 주식의 원가)
            sell_df = year_df[year_df['Type'] == 'Sell']
            total_sell_revenue = sell_df['Net Transaction Value'].sum() if len(sell_df) > 0 else 0
            # 간단하게 매도 금액만 계산 (실제 차익은 별도 계산 필요)
            total_sell_profit = total_sell_revenue
            
            # 총 수익
            total_returns = total_dividend + total_interest + total_sell_profit
            
            # 종목별 수익
            by_security = {}
            for security, group in dividend_df.groupby('Security'):
                sec_name = security if pd.notna(security) else '기타'
                if sec_name not in by_security:
                    by_security[sec_name] = {
                        'dividend': 0,
                        'sell_profit': 0,
                        'interest': 0
                    }
                by_security[sec_name]['dividend'] += group['Net Transaction Value'].sum()
            
            for security, group in sell_df.groupby('Security'):
                sec_name = security if pd.notna(security) else '기타'
                if sec_name not in by_security:
                    by_security[sec_name] = {
                        'dividend': 0,
                        'sell_profit': 0,
                        'interest': 0
                    }
                by_security[sec_name]['sell_profit'] += group['Net Transaction Value'].sum()
            
            # 소유자 및 계좌 타입별 수익
            by_owner_and_account = {}
            accounts = self.get_accounts()
            
            for account_info in accounts:
                account_name = account_info.account_name
                owner = account_info.owner
                account_type = account_info.account_type
                
                if owner not in by_owner_and_account:
                    by_owner_and_account[owner] = {}
                if account_type not in by_owner_and_account[owner]:
                    by_owner_and_account[owner][account_type] = {}
                
                account_df = year_df[year_df['Cash Account'] == account_name]
                
                dividend_sum = account_df[account_df['Type'] == 'Dividend']['Net Transaction Value'].sum()
                sell_sum = account_df[account_df['Type'] == 'Sell']['Net Transaction Value'].sum()
                interest_sum = account_df[account_df['Type'] == 'Interest']['Net Transaction Value'].sum()
                
                if dividend_sum > 0 or sell_sum > 0 or interest_sum > 0:
                    by_owner_and_account[owner][account_type][account_name] = {
                        'dividend': dividend_sum if pd.notna(dividend_sum) else 0,
                        'sell_profit': sell_sum if pd.notna(sell_sum) else 0,
                        'interest': interest_sum if pd.notna(interest_sum) else 0,
                        'total': (dividend_sum if pd.notna(dividend_sum) else 0) + 
                                (sell_sum if pd.notna(sell_sum) else 0) + 
                                (interest_sum if pd.notna(interest_sum) else 0)
                    }
            
            yearly_results.append(YearlyReturnsDetail(
                year=int(year),
                total_dividend=total_dividend,
                total_sell_profit=total_sell_profit,
                total_interest=total_interest,
                total_returns=total_returns,
                by_security=by_security,
                by_owner_and_account=by_owner_and_account
            ))
        
        return yearly_results

