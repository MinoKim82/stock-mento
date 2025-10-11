"""
포트폴리오 데이터를 마크다운 문서로 변환
"""
from typing import Dict, Any, List
from datetime import datetime


def generate_portfolio_markdown(portfolio_data: Dict[str, Any]) -> str:
    """
    포트폴리오 데이터를 마크다운 문서로 변환
    
    Args:
        portfolio_data: parsed_data.json 전체 데이터
        
    Returns:
        마크다운 형식의 문서
    """
    md_lines = []
    
    # 제목
    md_lines.append("# 📊 포트폴리오 분석 리포트")
    md_lines.append(f"\n생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_lines.append("---\n")
    
    # 1. 포트폴리오 요약
    md_lines.append("## 1. 💼 포트폴리오 요약\n")
    summary = portfolio_data.get("portfolio_summary", {})
    
    if summary:
        md_lines.append("### 전체 현황\n")
        
        # total_assets와 stock_portfolio에서 데이터 추출
        total_assets = summary.get("total_assets", {})
        stock_portfolio = summary.get("stock_portfolio", {})
        
        total_balance = total_assets.get("total_balance", 0)
        cash_balance = total_assets.get("cash_balance", 0)
        stock_value = total_assets.get("stock_value", 0)
        total_investment = stock_portfolio.get("total_investment", 0)
        unrealized_gain_loss = stock_portfolio.get("unrealized_gain_loss", 0)
        return_rate = stock_portfolio.get("return_rate", 0)
        
        md_lines.append(f"- **총 평가액**: ₩{total_balance:,.0f}")
        md_lines.append(f"- **총 투자금**: ₩{total_investment:,.0f}")
        md_lines.append(f"- **총 손익**: ₩{unrealized_gain_loss:,.0f}")
        md_lines.append(f"- **수익률**: {return_rate:.2f}%")
        md_lines.append(f"- **현금 잔액**: ₩{cash_balance:,.0f}")
        md_lines.append(f"- **주식 평가액**: ₩{stock_value:,.0f}\n")
        
        # 소유자별 포트폴리오
        owner_summary = summary.get("owner_summary", [])
        if owner_summary:
            md_lines.append("### 소유자별 현황\n")
            for owner_data in owner_summary:
                owner = owner_data.get("owner", "")
                total_info = owner_data.get("total", {})
                
                total_balance = total_info.get("total_balance", 0)
                total_investment = total_info.get("total_investment", 0)
                total_gain_loss = total_info.get("total_gain_loss", 0)
                return_rate = total_info.get("return_rate", 0)
                
                md_lines.append(f"\n#### {owner}")
                md_lines.append(f"- 평가액: ₩{total_balance:,.0f}")
                md_lines.append(f"- 투자금: ₩{total_investment:,.0f}")
                md_lines.append(f"- 손익: ₩{total_gain_loss:,.0f} ({return_rate:.2f}%)\n")
                
                # 계좌 타입별
                account_types = owner_data.get("accountTypes", [])
                if account_types:
                    md_lines.append(f"**{owner}의 계좌별 현황:**\n")
                    for acc_type_data in account_types:
                        acc_type = acc_type_data.get("accountType", "")
                        md_lines.append(f"- **{acc_type}**")
                        md_lines.append(f"  - 평가액: ₩{acc_type_data.get('total_balance', 0):,.0f}")
                        md_lines.append(f"  - 투자금: ₩{acc_type_data.get('total_investment', 0):,.0f}")
                        md_lines.append(f"  - 손익: ₩{acc_type_data.get('total_gain_loss', 0):,.0f} ({acc_type_data.get('return_rate', 0):.2f}%)")
    
    md_lines.append("\n---\n")
    
    # 2. 계좌별 포트폴리오
    md_lines.append("## 2. 🏦 계좌별 포트폴리오\n")
    accounts_detailed = portfolio_data.get("accounts_detailed", {})
    
    # accounts_detailed가 dict이고 'accounts_by_owner_and_type' 키가 있는 경우
    if isinstance(accounts_detailed, dict) and "accounts_by_owner_and_type" in accounts_detailed:
        accounts_by_owner = accounts_detailed["accounts_by_owner_and_type"]
    elif isinstance(accounts_detailed, list):
        # 리스트 형태인 경우 기존 로직 사용
        accounts_by_owner: Dict[str, Dict[str, List]] = {}
        for account in accounts_detailed:
            owner = account.get("owner", "미분류")
            acc_type = account.get("account_type", "기타")
            if owner not in accounts_by_owner:
                accounts_by_owner[owner] = {}
            if acc_type not in accounts_by_owner[owner]:
                accounts_by_owner[owner][acc_type] = []
            accounts_by_owner[owner][acc_type].append(account)
    else:
        accounts_by_owner = {}
    
    if accounts_by_owner:
        for owner, account_types in accounts_by_owner.items():
            md_lines.append(f"### {owner}의 계좌\n")
            
            for acc_type, type_accounts in account_types.items():
                md_lines.append(f"#### {acc_type}\n")
                
                for account in type_accounts:
                    broker = account.get("broker", "")
                    cash_balance = account.get("balance", 0)  # balance 필드 사용
                    total_investment = account.get("total_investment", 0)
                    total_value = account.get("total_balance", 0)  # total_balance 필드 사용
                    total_gain_loss = account.get("total_gain_loss", 0)
                    gain_loss_rate = (total_gain_loss / total_investment * 100) if total_investment > 0 else 0
                    
                    md_lines.append(f"**{broker} {acc_type}**\n")
                    md_lines.append(f"- 잔액: ₩{cash_balance:,.0f}")
                    md_lines.append(f"- 투자금: ₩{total_investment:,.0f}")
                    md_lines.append(f"- 현재가치: ₩{total_value:,.0f}")
                    md_lines.append(f"- 손익: ₩{total_gain_loss:,.0f} ({gain_loss_rate:.2f}%)\n")
                    
                    # 보유 종목
                    holdings = account.get("holdings", [])
                    if holdings:
                        md_lines.append("**보유 종목:**\n")
                        for holding in holdings:
                            security = holding.get("security", "")
                            shares = holding.get("shares", 0)
                            avg_price = holding.get("average_price", 0)
                            total_cost = holding.get("total_cost", 0)
                            current_price = holding.get("current_price", 0)
                            current_value = holding.get("current_value", 0)
                            gain_loss = holding.get("unrealized_gain_loss", 0)
                            gain_loss_rate_h = holding.get("unrealized_gain_loss_rate", 0)
                            
                            md_lines.append(f"- **{security}**")
                            md_lines.append(f"  - 보유수량: {shares:,.0f}주")
                            md_lines.append(f"  - 평균단가: ₩{avg_price:,.0f}")
                            md_lines.append(f"  - 투자금: ₩{total_cost:,.0f}")
                            
                            if current_price and current_price > 0:
                                md_lines.append(f"  - 현재가: ₩{current_price:,.0f}")
                                md_lines.append(f"  - 평가액: ₩{current_value:,.0f}")
                                md_lines.append(f"  - 손익: ₩{gain_loss:,.0f} ({gain_loss_rate_h:.2f}%)")
                            else:
                                md_lines.append(f"  - 현재가: 조회 불가")
                        
                        md_lines.append("")
    
    md_lines.append("\n---\n")
    
    # 3. 수익 분석
    md_lines.append("## 3. 💰 수익 분석\n")
    yearly_returns = portfolio_data.get("yearly_returns", [])
    
    if yearly_returns:
        md_lines.append("### 연도별 수익 현황\n")
        
        for year_data in yearly_returns:
            year = year_data.get("year", "")
            total_dividend = year_data.get("total_dividend", 0)
            total_sell_profit = year_data.get("total_sell_profit", 0)
            total_sell_revenue = year_data.get("total_sell_revenue", 0)
            total_sell_cost = year_data.get("total_sell_cost", 0)
            total_interest = year_data.get("total_interest", 0)
            total_return = year_data.get("total_return", 0)
            
            md_lines.append(f"#### {year}년\n")
            md_lines.append(f"- **총 수익**: ₩{total_return:,.0f}")
            md_lines.append(f"  - 배당금: ₩{total_dividend:,.0f}")
            md_lines.append(f"  - 매도 수익: ₩{total_sell_profit:,.0f}")
            md_lines.append(f"    - 매도 총액: ₩{total_sell_revenue:,.0f}")
            md_lines.append(f"    - 매도 원가: ₩{total_sell_cost:,.0f}")
            md_lines.append(f"  - 이자: ₩{total_interest:,.0f}\n")
            
            # 소유자별 수익
            by_owner = year_data.get("by_owner_and_account", {})
            if by_owner:
                md_lines.append(f"**{year}년 소유자별 수익 상세:**\n")
                
                for owner, owner_data in by_owner.items():
                    md_lines.append(f"\n##### {owner}\n")
                    
                    for acc_type, acc_accounts in owner_data.items():
                        if not acc_accounts:  # 빈 딕셔너리면 스킵
                            continue
                            
                        md_lines.append(f"**{acc_type}**\n")
                        
                        # 각 계좌별로 처리
                        for account_name, acc_data in acc_accounts.items():
                            # 계좌 이름 표시 (중복 제거)
                            display_name = account_name.replace(f"{owner} ", "")
                            md_lines.append(f"*{display_name}*\n")
                            
                            # 총 수익
                            total = acc_data.get("total", 0)
                            dividend = acc_data.get("dividend", 0)
                            interest = acc_data.get("interest", 0)
                            sell_profit = acc_data.get("sell_profit", 0)
                            sell_revenue = acc_data.get("sell_revenue", 0)
                            
                            if total != 0 or dividend != 0 or interest != 0 or sell_profit != 0:
                                md_lines.append(f"- 총 수익: ₩{total:,.0f}")
                                
                                if dividend > 0:
                                    md_lines.append(f"- 배당금: ₩{dividend:,.0f}")
                                
                                if interest > 0:
                                    md_lines.append(f"- 이자: ₩{interest:,.0f}")
                                
                                if sell_profit != 0 or sell_revenue > 0:
                                    md_lines.append(f"- 매도 수익: ₩{sell_profit:,.0f} (매도액: ₩{sell_revenue:,.0f})")
                                
                                # 종목별 상세
                                securities = acc_data.get("securities", {})
                                if securities:
                                    md_lines.append(f"\n**종목별 상세:**")
                                    for security, sec_data in securities.items():
                                        sec_dividend = sec_data.get("dividend", 0)
                                        sec_sell_profit = sec_data.get("sell_profit", 0)
                                        sec_sell_shares = sec_data.get("sell_shares", 0)
                                        
                                        if sec_dividend > 0 or sec_sell_profit != 0:
                                            md_lines.append(f"- {security}")
                                            if sec_dividend > 0:
                                                md_lines.append(f"  - 배당: ₩{sec_dividend:,.0f}")
                                            if sec_sell_profit != 0:
                                                md_lines.append(f"  - 매도 수익: ₩{sec_sell_profit:,.0f} ({sec_sell_shares}주)")
                                
                                md_lines.append("")
    
    md_lines.append("\n---\n")
    
    # 4. 성과 분석
    performance = portfolio_data.get("portfolio_performance", {})
    if performance:
        md_lines.append("## 4. 📈 성과 분석\n")
        md_lines.append(f"- 총 수익률: {performance.get('total_return_rate', 0):.2f}%")
        md_lines.append(f"- 실현 손익: ₩{performance.get('realized_gain_loss', 0):,.0f}")
        md_lines.append(f"- 미실현 손익: ₩{performance.get('unrealized_gain_loss', 0):,.0f}")
        md_lines.append(f"- 배당 수익: ₩{performance.get('dividend_income', 0):,.0f}")
        md_lines.append(f"- 이자 수익: ₩{performance.get('interest_income', 0):,.0f}\n")
    
    # 5. 리스크 분석
    risk = portfolio_data.get("portfolio_risk", {})
    if risk:
        md_lines.append("## 5. ⚠️ 리스크 분석\n")
        md_lines.append(f"- 손실 계좌 수: {risk.get('loss_accounts', 0)}개")
        md_lines.append(f"- 총 손실액: ₩{risk.get('total_loss', 0):,.0f}")
        md_lines.append(f"- 최대 손실률: {risk.get('max_loss_rate', 0):.2f}%\n")
    
    md_lines.append("\n---\n")
    md_lines.append("\n*본 리포트는 업로드된 CSV 데이터를 기반으로 자동 생성되었습니다.*\n")
    
    return "\n".join(md_lines)


def save_portfolio_markdown(portfolio_data: Dict[str, Any], output_path: str) -> str:
    """
    포트폴리오 마크다운을 파일로 저장
    
    Args:
        portfolio_data: 포트폴리오 데이터
        output_path: 저장 경로
        
    Returns:
        저장된 파일 경로
    """
    markdown_content = generate_portfolio_markdown(portfolio_data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    return output_path

