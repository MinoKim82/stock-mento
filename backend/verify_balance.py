import pandas as pd
import re

df = pd.read_csv('csv_data/current_portfolio.csv')

# Currency 추출
def get_currency(val):
    if pd.isna(val) or val == '':
        return 'KRW'
    return 'USD' if 'USD' in str(val) else 'KRW'

df['Currency'] = df['Amount'].apply(get_currency)

# 숫자 변환
def to_num(val):
    if pd.isna(val) or val == '':
        return 0
    try:
        return float(str(val).replace('USD', '').replace(',', '').strip())
    except:
        return 0

df['Amount_Num'] = df['Amount'].apply(to_num)

# 계좌명 정규화
df['Cash Account'] = df['Cash Account'].str.replace(r'\s*예수금\s*$', '', regex=True)
df['Offset Account'] = df['Offset Account'].str.replace(r'\s*예수금\s*$', '', regex=True)

# 민호 토스 종합매매 (KRW만)
account = '민호 토스 종합매매'
account_df = df[(df['Cash Account'] == account) & (df['Currency'] == 'KRW')].copy()
account_df = account_df.sort_values('Date')

print(f'계좌: {account}')
print('=' * 120)
print()

balance = 0
print('모든 거래:')

for idx, row in account_df.iterrows():
    type_val = row['Type']
    amt = row['Amount_Num']
    date_str = pd.to_datetime(row["Date"]).strftime('%Y-%m-%d')
    security = str(row.get('Security', '')) if pd.notna(row.get('Security', '')) else ''
    
    old_balance = balance
    
    if type_val in ['Dividend', 'Sell', 'Deposit', 'Interest']:
        balance += amt
        sign = '+'
    elif type_val in ['Buy', 'Removal', 'Transfer (Outbound)']:
        balance -= amt
        sign = '-'
    else:
        continue
    
    print(f'{date_str} | {type_val:25s} | {security:20s} | {sign}{amt:>12,.0f} | 잔액: {balance:>15,.0f}')

# Transfer Inbound
print()
print('=' * 120)
print('Transfer Inbound (다른 계좌에서 입금):')
inbound = df[(df['Type'] == 'Transfer (Outbound)') & (df['Offset Account'] == account)]

for _, row in inbound.iterrows():
    if row['Currency'] == 'USD':
        note = row.get('Note', '')
        if '환율' in str(note):
            usd_match = re.search(r'달러\s+([\d,\.]+)', str(note))
            rate_match = re.search(r'환율\s+([\d,\.]+)', str(note))
            fee_match = re.search(r'환전 수수료\s+([\d,]+)', str(note))
            if usd_match and rate_match:
                usd_val = float(usd_match.group(1).replace(',', ''))
                rate_val = float(rate_match.group(1).replace(',', ''))
                fee_val = float(fee_match.group(1).replace(',', '')) if fee_match else 0
                krw_val = (usd_val * rate_val) - fee_val
                balance += krw_val
                date_str = pd.to_datetime(row["Date"]).strftime('%Y-%m-%d')
                print(f'{date_str} | USD {usd_val:,.2f} * {rate_val:,.2f} - {fee_val:,.0f}원 = +{krw_val:,.0f}원 | 잔액: {balance:,.0f}원')
    elif row['Currency'] == 'KRW':
        balance += row['Amount_Num']
        date_str = pd.to_datetime(row["Date"]).strftime('%Y-%m-%d')
        print(f'{date_str} | KRW 이체 +{row["Amount_Num"]:,.0f}원 | 잔액: {balance:,.0f}원')

print()
print('=' * 120)
print(f'✅ 최종 잔액: {balance:,.0f}원')
print(f'📊 전체 거래 수: {len(account_df)}건')

