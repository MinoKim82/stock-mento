"""
마크다운 파일 정리 테스트
"""
import os
import json
from pathlib import Path

# 파일 경로
backend_dir = Path(__file__).parent
parsed_data_file = backend_dir / "parsed_data" / "portfolio_data.json"
docs_dir = backend_dir / "portfolio_docs"

print("🧪 마크다운 파일 정리 테스트\n")

# Before
print("📂 Before:")
existing_files = list(docs_dir.glob("portfolio_*.md"))
print(f"   총 {len(existing_files)}개 파일")
for f in existing_files:
    print(f"   - {f.name}")

print()

# 포트폴리오 데이터 로드
with open(parsed_data_file, 'r', encoding='utf-8') as f:
    portfolio_data = json.load(f)

print("✅ 포트폴리오 데이터 로드 완료\n")

# PortfolioAnalysisChat 생성 (마크다운 생성 및 이전 파일 삭제)
from langchain_service import PortfolioAnalysisChat

print("📝 마크다운 문서 재생성...\n")

chat = PortfolioAnalysisChat(
    portfolio_data=portfolio_data,
    provider="gemini"
)

print()

# After
print("📂 After:")
remaining_files = list(docs_dir.glob("portfolio_*.md"))
print(f"   총 {len(remaining_files)}개 파일")
for f in remaining_files:
    print(f"   - {f.name}")

print()

if len(remaining_files) == 1:
    print("✅ 성공: 하나의 파일만 남음!")
    print(f"   파일: {remaining_files[0].name}")
else:
    print(f"⚠️  예상: 1개 파일, 실제: {len(remaining_files)}개 파일")

