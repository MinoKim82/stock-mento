from pp import TransactionParser
import pandas as pd
import re

parser = TransactionParser('csv_data/current_portfolio.csv')
df = parser.get_dataframe()

account = '민호 토스 종합매매'
cash_balance = 0.0

print(f'계좌: {account}')
print('=' * 120)

# 1. Cash Account 거래
cash_df = df[(df['Cash Account'] == account) & (df['Currency'] == 'KRW')].sort_values('Date')

print('\n📌 Cash Account 거래:')
print(f"{'날짜':12s} | {'거래타입':25s} | {'종목':20s} | {'금액':>15s} | {'누적잔액':>15s}")
print('-' * 120)

for _, row in cash_df.iterrows():
    trans_type = row['Type']
    amount = row['Amount']
    security = row['Security'] if pd.notna(row['Security']) else ''
    
    if pd.notna(amount):
        if trans_type in ['Dividend', 'Deposit', 'Interest']:
            cash_balance += amount
            sign = '+'
            print(f"{row['Date'].date()} | {trans_type:25s} | {security:20s} | {sign}{amount:>14,.0f} | {cash_balance:>15,.0f}")
        elif trans_type in ['Removal', 'Transfer (Outbound)']:
            cash_balance -= amount
            sign = '-'
            print(f"{row['Date'].date()} | {trans_type:25s} | {security:20s} | {sign}{amount:>14,.0f} | {cash_balance:>15,.0f}")

print(f'\n✅ Cash Account 소계: {cash_balance:,.0f}원')

# 2. Offset Account 거래
offset_df = df[df['Offset Account'] == account].sort_values('Date')

print(f'\n📌 Offset Account 거래:')
print(f"{'날짜':12s} | {'거래타입':25s} | {'종목':20s} | {'통화':5s} | {'금액':>15s} | {'누적잔액':>15s}")
print('-' * 120)

for _, row in offset_df.iterrows():
    trans_type = row['Type']
    amount = row['Amount']
    currency = row['Currency']
    security = row['Security'] if pd.notna(row['Security']) else ''
    note = row.get('Note', '')
    
    if pd.notna(amount):
        if trans_type == 'Buy' and currency == 'KRW':
            cash_balance -= amount
            sign = '-'
            print(f"{row['Date'].date()} | {trans_type:25s} | {security:20s} | {currency:5s} | {sign}{amount:>14,.0f} | {cash_balance:>15,.0f}")
        elif trans_type == 'Sell' and currency == 'KRW':
            cash_balance += amount
            sign = '+'
            print(f"{row['Date'].date()} | {trans_type:25s} | {security:20s} | {currency:5s} | {sign}{amount:>14,.0f} | {cash_balance:>15,.0f}")
        elif trans_type == 'Transfer (Outbound)':
            from_account = row['Cash Account']
            
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
                        print(f"{row['Date'].date()} | {trans_type:25s} | USD 환전              | {currency:5s} | +{krw_amount:>14,.0f} | {cash_balance:>15,.0f}")
                        print(f"{'':12s} |   → USD {usd_amount:,.2f} × 환율 {exchange_rate:,.2f} - 수수료 {exchange_fee:,.0f}원")
            elif currency == 'KRW':
                cash_balance += amount
                sign = '+'
                print(f"{row['Date'].date()} | {trans_type:25s} | {from_account:20s} | {currency:5s} | {sign}{amount:>14,.0f} | {cash_balance:>15,.0f}")

print(f'\n✅ Offset Account 소계 포함 최종 잔액: {cash_balance:,.0f}원')
print('=' * 120)
print(f'🎯 목표 잔액: 327,062원')
print(f'📊 차이: {cash_balance - 327062:,.0f}원')

