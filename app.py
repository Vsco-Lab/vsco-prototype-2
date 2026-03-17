"""메인 실행 스크립트"""
import os
import sys
from datetime import datetime
from state import GraphState, create_empty_section
from graph import build_graph
from ingest import load_documents, split_documents, create_vectorstore
from config import VECTORSTORE_PATH, OUTPUT_DIR


def ensure_vectorstore():
    """벡터DB가 없으면 생성"""
    index_path = os.path.join(VECTORSTORE_PATH, "index.faiss")
    if not os.path.exists(index_path):
        print("[app] 벡터DB가 없습니다. 생성 중...")
        docs = load_documents()
        chunks = split_documents(docs)
        create_vectorstore(chunks)
    else:
        print("[app] 벡터DB 확인 완료")


def create_initial_state() -> GraphState:
    """초기 상태 생성"""
    return GraphState(
        messages=[],
        market_background=create_empty_section("2. 시장 배경"),
        lg_strategy=create_empty_section("3. LG에너지솔루션 전략 분석"),
        catl_strategy=create_empty_section("4. CATL 전략 분석"),
        comparison_swot=create_empty_section("5. 핵심 전략 비교 및 SWOT 분석"),
        summary="",
        full_report="",
        references=[],
        next_agent="",
        revision_count=0,
        quality_feedback="",
        quality_passed=False,
    )


def save_report(report: str):
    """보고서를 마크다운 및 HTML로 저장"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Markdown 저장
    md_path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[app] 마크다운 보고서 저장: {md_path}")

    # HTML 저장
    html_path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.html")
    html_content = generate_html(report)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[app] HTML 보고서 저장: {html_path}")


def generate_html(md_content: str) -> str:
    """마크다운을 HTML로 변환"""
    try:
        import markdown
        body = markdown.markdown(md_content, extensions=["tables", "fenced_code"])
    except ImportError:
        body = f"<pre>{md_content}</pre>"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>배터리 시장 전략 분석 보고서</title>
<style>
  body {{ font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; color: #333; }}
  h1 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 8px; }}
  h2 {{ color: #1a1a2e; border-bottom: 2px solid #1a1a2e; padding-bottom: 6px; margin-top: 36px; }}
  h3 {{ color: #0077b6; border-bottom: 1px solid #e0e0e0; padding-bottom: 4px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }}
  th {{ background: #1a1a2e; color: white; padding: 8px; }}
  td {{ border: 1px solid #ddd; padding: 6px 10px; }}
  tr:nth-child(even) {{ background: #f9f9f9; }}
  strong {{ color: #1a1a2e; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    print("=" * 60)
    print("  배터리 시장 전략 분석 보고서 생성 시스템")
    print("  LG에너지솔루션 vs CATL")
    print("=" * 60)

    # 1. 벡터DB 확인
    ensure_vectorstore()

    # 2. 그래프 빌드
    print("\n[app] 그래프 빌드 중...")
    graph = build_graph()

    # 3. 초기 상태
    state = create_initial_state()

    # 4. 그래프 실행
    print("[app] 분석 시작...\n")
    final_state = graph.invoke(state)

    # 5. 결과 저장
    report = final_state.get("full_report", "")
    if report:
        save_report(report)
        print(f"\n[app] 품질 검증: {'PASS' if final_state.get('quality_passed') else 'REVISE'}")
        print(f"[app] 재작업 횟수: {final_state.get('revision_count', 0)}")
        print("\n[app] 완료!")
    else:
        print("\n[app] 보고서 생성 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()
