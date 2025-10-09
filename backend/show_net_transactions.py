from pp import TransactionParser
import pandas as pd
import re

parser = TransactionParser('csv_data/current_portfolio.csv')
df = parser.get_dataframe()

account = '민호 토스 종합매매'
cash_balance = 0.0

print(f'\n{"=" * 150}')
print(f'계좌: {account} - Net Transaction Value 기준')
print(f'{"=" * 150}\n')

# Cash Account 거래
cash_df = df[(df['Cash Account'] == account) & (df['Currency'] == 'KRW')].sort_values('Date')

print('📌 Cash Account 거래:')
print(f"{'날짜':12s} | {'거래타입':20s} | {'종목':15s} | {'Amount':>15s} | {'Fee':>10s} | {'Tax':>10s} | {'Net Value':>15s} | {'사용금액':>15s} | {'잔액':>15s}")
print('-' * 150)

for _, row in cash_df.iterrows():
    trans_type = row['Type']
    amount = row['Amount']
    net_value = row['Net Transaction Value']
    fee = row['Fees'] if pd.notna(row['Fees']) else 0
    tax = row['Taxes'] if pd.notna(row['Taxes']) else 0
    security = row['Security'] if pd.notna(row['Security']) else ''
    date = row['Date'].date()
    
    used_value = 0
    sign = ''
    
    if pd.notna(amount) or pd.notna(net_value):
        # Net Transaction Value 사용 거래
        if trans_type in ['Interest', 'Sell', 'Dividend'] and pd.notna(net_value):
            cash_balance += net_value
            used_value = net_value
            sign = '+'
        elif trans_type == 'Buy' and pd.notna(net_value):
            cash_balance -= net_value
            used_value = net_value
            sign = '-'
        # Amount 사용 거래
        elif trans_type == 'Deposit' and pd.notna(amount):
            cash_balance += amount
            used_value = amount
            sign = '+'
        elif trans_type in ['Removal', 'Transfer (Outbound)'] and pd.notna(amount):
            cash_balance -= amount
            used_value = amount
            sign = '-'
        else:
            continue
        
        amt_str = f"{amount:,.0f}" if pd.notna(amount) else ""
        net_str = f"{net_value:,.0f}" if pd.notna(net_value) else ""
        fee_str = f"{fee:,.0f}" if fee > 0 else ""
        tax_str = f"{tax:,.0f}" if tax > 0 else ""
        
        print(f"{date} | {trans_type:20s} | {security:15s} | {amt_str:>15s} | {fee_str:>10s} | {tax_str:>10s} | {net_str:>15s} | {sign}{used_value:>14,.0f} | {cash_balance:>15,.0f}")

print(f'\n✅ Cash Account 처리 후 잔액: {cash_balance:,.0f}원\n')

# Offset Account 거래
offset_df = df[(df['Offset Account'] == account) & (df['Type'] == 'Transfer (Outbound)')].sort_values('Date')

print('📌 Offset Account 거래 (Transfer Inbound):')
print(f"{'날짜':12s} | {'출발계좌':30s} | {'통화':5s} | {'금액':>15s} | {'잔액':>15s}")
print('-' * 150)

for _, row in offset_df.iterrows():
    amount = row['Amount']
    currency = row['Currency']
    from_account = row['Cash Account']
    note = row.get('Note', '')
    date = row['Date'].date()
    
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
                    
                    print(f"{date} | {from_account:30s} | {currency:5s} | +{krw_amount:>14,.0f} | {cash_balance:>15,.0f}")
                    print(f"{'':12s} | 💱 USD {usd_amount:,.2f} × 환율 {exchange_rate:,.2f} - 수수료 {exchange_fee:,.0f}원")
        # KRW → KRW 이체
        elif currency == 'KRW':
            cash_balance += amount
            print(f"{date} | {from_account:30s} | {currency:5s} | +{amount:>14,.0f} | {cash_balance:>15,.0f}")

print(f'\n{"=" * 150}')
print(f'✅ 최종 잔액: {cash_balance:,.0f}원')
print(f'🎯 목표 잔액: 327,062원')
print(f'📊 차이: {cash_balance - 327062:,.0f}원')
print(f'{"=" * 150}\n')

