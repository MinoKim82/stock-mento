from pp import TransactionParser
import pandas as pd
import re

parser = TransactionParser('csv_data/current_portfolio.csv')
df = parser.get_dataframe()

account = '민호 토스 종합매매'
cash_balance = 0.0

print(f'\n{"=" * 140}')
print(f'계좌: {account} - 전체 거래 내역')
print(f'{"=" * 140}\n')

# Cash Account 거래
cash_df = df[(df['Cash Account'] == account) & (df['Currency'] == 'KRW')].sort_values('Date')

print('📌 Cash Account 거래:')
print(f"{'날짜':12s} {'시간':8s} | {'거래타입':25s} | {'종목':20s} | {'수량':>8s} | {'단가':>12s} | {'금액':>15s} | {'잔액':>15s}")
print('-' * 140)

for _, row in cash_df.iterrows():
    trans_type = row['Type']
    amount = row['Amount']
    security = row['Security'] if pd.notna(row['Security']) else ''
    shares = f"{row['Shares']:.0f}" if pd.notna(row['Shares']) else ''
    quote = f"{row['Quote']:,.0f}" if pd.notna(row['Quote']) else ''
    date = row['Date'].date()
    time = row['Date'].strftime('%H:%M:%S')
    
    if pd.notna(amount):
        if trans_type in ['Dividend', 'Sell', 'Deposit', 'Interest']:
            cash_balance += amount
            sign = '+'
        elif trans_type in ['Buy', 'Removal', 'Transfer (Outbound)']:
            cash_balance -= amount
            sign = '-'
        else:
            continue
        
        print(f"{date} {time} | {trans_type:25s} | {security:20s} | {shares:>8s} | {quote:>12s} | {sign}{amount:>14,.0f} | {cash_balance:>15,.0f}")

print(f'\n✅ Cash Account 처리 후 잔액: {cash_balance:,.0f}원\n')

# Offset Account 거래
offset_df = df[(df['Offset Account'] == account) & (df['Type'] == 'Transfer (Outbound)')].sort_values('Date')

print('📌 Offset Account 거래 (Transfer Inbound):')
print(f"{'날짜':12s} {'시간':8s} | {'거래타입':25s} | {'출발계좌':30s} | {'통화':5s} | {'금액':>15s} | {'잔액':>15s}")
print('-' * 140)

for _, row in offset_df.iterrows():
    amount = row['Amount']
    currency = row['Currency']
    from_account = row['Cash Account']
    note = row.get('Note', '')
    date = row['Date'].date()
    time = row['Date'].strftime('%H:%M:%S')
    
    if pd.notna(amount):
        # USD → KRW 환전
        if '해외' in from_account and currency == 'USD':
            if '환율' in str(note):
                usd_match = re.search(r'달러\s+([\d,\.]+)', str(note))
                rate_match = re.search(r'환율\s+([\d,\.]+)', str(note))
                fee_match = re.search(r'환전 수수료\s+([\d,]+)', str(note))
                
                if usd_match and rate_match:
                    usd_amount = float(usd_match.group(1).replace(',', ''))
                    exchange_rate = float(rate_match.group(1).replace(',', ''))
                    exchange_fee = float(fee_match.group(1).replace(',', '')) if fee_match else 0
                    krw_amount = (usd_amount * exchange_rate) - exchange_fee
                    cash_balance += krw_amount
                    
                    print(f"{date} {time} | Transfer (Inbound)       | {from_account:30s} | {currency:5s} | +{krw_amount:>14,.0f} | {cash_balance:>15,.0f}")
                    print(f"{'':12s} {'':8s} |   💱 USD {usd_amount:,.2f} × 환율 {exchange_rate:,.2f} - 수수료 {exchange_fee:,.0f}원")
        # KRW → KRW 이체
        elif currency == 'KRW':
            cash_balance += amount
            print(f"{date} {time} | Transfer (Inbound)       | {from_account:30s} | {currency:5s} | +{amount:>14,.0f} | {cash_balance:>15,.0f}")

print(f'\n{"=" * 140}')
print(f'✅ 최종 잔액: {cash_balance:,.0f}원')
print(f'🎯 목표 잔액: 327,062원')
print(f'📊 차이: {cash_balance - 327062:,.0f}원')
print(f'{"=" * 140}\n')

