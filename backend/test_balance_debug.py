from pp import TransactionParser
import pandas as pd

parser = TransactionParser('csv_data/current_portfolio.csv')
df = parser.get_dataframe()

account = '민호 토스 종합매매'
cash_balance = 0.0

print(f'계좌: {account}')
print('=' * 100)

# 1. Cash Account 거래
cash_df = df[(df['Cash Account'] == account) & (df['Currency'] == 'KRW')]

print('\n1️⃣  Cash Account 거래:')
for _, row in cash_df.iterrows():
    trans_type = row['Type']
    amount = row['Amount']
    
    if pd.notna(amount):
        old_balance = cash_balance
        if trans_type in ['Dividend', 'Deposit', 'Interest']:
            cash_balance += amount
            print(f'  {row["Date"].date()} | {trans_type:20s} | +{amount:>12,.0f} | 잔액: {cash_balance:>15,.0f}')
        elif trans_type in ['Removal', 'Transfer (Outbound)']:
            cash_balance -= amount
            print(f'  {row["Date"].date()} | {trans_type:20s} | -{amount:>12,.0f} | 잔액: {cash_balance:>15,.0f}')

print(f'\n  💰 Cash Account 처리 후 잔액: {cash_balance:,.0f}원')

# 2. Offset Account 거래
offset_df = df[(df['Offset Account'] == account) & (df['Currency'] == 'KRW')]

print(f'\n2️⃣  Offset Account 거래:')
for _, row in offset_df.iterrows():
    trans_type = row['Type']
    amount = row['Amount']
    security = row['Security'] if pd.notna(row['Security']) else ''
    
    if pd.notna(amount):
        old_balance = cash_balance
        if trans_type == 'Buy':
            cash_balance -= amount
            print(f'  {row["Date"].date()} | {trans_type:20s} | {security:15s} | -{amount:>12,.0f} | 잔액: {cash_balance:>15,.0f}')
        elif trans_type == 'Sell':
            cash_balance += amount
            print(f'  {row["Date"].date()} | {trans_type:20s} | {security:15s} | +{amount:>12,.0f} | 잔액: {cash_balance:>15,.0f}')

print(f'\n  💰 Offset Account 처리 후 잔액: {cash_balance:,.0f}원')

print('\n' + '=' * 100)
print(f'✅ 최종 잔액: {cash_balance:,.0f}원')
print(f'🎯 목표 잔액: 327,062원')
print(f'📊 차이: {cash_balance - 327062:,.0f}원')

