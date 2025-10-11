"""
포트폴리오 마크다운 생성 테스트
"""
import json
import os
from langchain_service.portfolio_document import generate_portfolio_markdown

# parsed_data.json 로드
PARSED_DATA_FILE = "parsed_data/portfolio_data.json"

if os.path.exists(PARSED_DATA_FILE):
    print(f"✅ 파일 발견: {PARSED_DATA_FILE}")
    
    with open(PARSED_DATA_FILE, 'r', encoding='utf-8') as f:
        portfolio_data = json.load(f)
    
    print(f"✅ 데이터 로드 완료")
    print(f"   - 포트폴리오 요약: {bool(portfolio_data.get('portfolio_summary'))}")
    print(f"   - 계좌 상세: {len(portfolio_data.get('accounts_detailed', []))}개")
    print(f"   - 연도별 수익: {len(portfolio_data.get('yearly_returns', []))}개")
    
    # 마크다운 생성
    print("\n📝 마크다운 생성 중...")
    markdown = generate_portfolio_markdown(portfolio_data)
    
    print(f"✅ 마크다운 생성 완료: {len(markdown)} 글자")
    
    # 미리보기 (첫 1000자)
    print("\n📄 마크다운 미리보기:")
    print("=" * 80)
    print(markdown[:1500])
    print("...")
    print("=" * 80)
    
    # 파일로 저장
    output_file = "portfolio_docs/portfolio_preview.md"
    os.makedirs("portfolio_docs", exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"\n✅ 마크다운 파일 저장: {output_file}")
    print(f"   cat {output_file} 명령으로 확인할 수 있습니다.")
    
else:
    print(f"❌ 파일이 없습니다: {PARSED_DATA_FILE}")
    print("   먼저 CSV 파일을 업로드하여 데이터를 생성해주세요.")

