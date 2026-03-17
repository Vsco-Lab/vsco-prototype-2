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
    """보고서를 마크다운, HTML, PDF로 저장 (시각화 포함)"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 시각화 차트 생성
    print("[app] 시각화 차트 생성 중...")
    from tools.chart_generator import generate_all_charts
    chart_paths = generate_all_charts()
    print(f"[app] 차트 {len(chart_paths)}개 생성 완료")

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

    # PDF 저장 (시각화 포함)
    pdf_path = os.path.join(OUTPUT_DIR, f"report_{timestamp}.pdf")
    generate_pdf(report, pdf_path, chart_paths)
    print(f"[app] PDF 보고서 저장: {pdf_path}")


def generate_pdf(md_content: str, output_path: str, chart_paths: list = None):
    """마크다운을 PDF로 변환 (fpdf2 + NanumGothic + 시각화 차트)"""
    import re
    from fpdf import FPDF

    font_dir = os.path.join(os.path.dirname(__file__), "docs")
    font_regular = os.path.join(font_dir, "NanumGothic.ttf")
    font_bold = os.path.join(font_dir, "NanumGothicBold.ttf")

    if not os.path.exists(font_regular):
        print("[app] NanumGothic 폰트 다운로드 중...")
        import urllib.request
        urllib.request.urlretrieve(
            "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf",
            font_regular,
        )
        urllib.request.urlretrieve(
            "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf",
            font_bold,
        )

    # 차트 → 섹션 매핑 (H3 제목 키워드 → 차트 파일명)
    chart_map = {}
    if chart_paths:
        for p in chart_paths:
            fname = os.path.basename(p)
            chart_map[fname] = p

    # 섹션 키워드 → 해당 섹션 끝에 삽입할 차트
    section_charts = {
        "캐즘": "ev_sales_trend.png",
        "ESS 시장": "ess_market_growth.png",
        "사업 실적": "financial_comparison.png",
        "전략 비교": "market_share_comparison.png",
        "LG에너지솔루션 SWOT": "swot_matrix_lg.png",
        "CATL SWOT": "swot_matrix_catl.png",
        "SWOT 비교 종합": "swot_radar.png",
    }

    def _try_insert_chart(heading_text):
        """H2/H3 제목에 매칭되는 차트가 있으면 삽입"""
        for keyword, chart_file in section_charts.items():
            if keyword in heading_text and chart_file in chart_map:
                path = chart_map.pop(chart_file)
                if os.path.exists(path):
                    pdf.ln(5)
                    pdf.image(path, x=15, w=180)
                    pdf.ln(8)
                return

    pdf = FPDF()
    pdf.add_font("Korean", "", font_regular)
    pdf.add_font("Korean", "B", font_bold)
    pdf.set_auto_page_break(auto=True, margin=20)

    lines = md_content.split("\n")
    in_table = False
    table_headers = []
    table_rows = []
    is_first_h1 = True
    in_reference = False
    last_h2 = ""
    last_h3 = ""

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_table and table_rows:
                _render_table(pdf, table_headers, table_rows)
                in_table = False
                table_headers = []
                table_rows = []
            if pdf.page > 0:
                pdf.ln(3)
            continue

        if re.match(r"^\|[-\s|:]+\|$", stripped):
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if not in_table:
                in_table = True
                table_headers = cells
            else:
                table_rows.append(cells)
            continue

        if in_table:
            _render_table(pdf, table_headers, table_rows)
            in_table = False
            table_headers = []
            table_rows = []

        # H1
        if stripped.startswith("# ") and not stripped.startswith("## "):
            # 이전 H3 차트 삽입
            if last_h3:
                _try_insert_chart(last_h3)
                last_h3 = ""
            if last_h2:
                _try_insert_chart(last_h2)
                last_h2 = ""

            if is_first_h1:
                pdf.add_page()
                pdf.ln(40)
                pdf.set_font("Korean", "B", 28)
                pdf.set_text_color(26, 26, 46)
                pdf.multi_cell(0, 14, stripped[2:], align="C")
                pdf.ln(10)
                pdf.set_font("Korean", "", 14)
                pdf.set_text_color(108, 117, 125)
                pdf.multi_cell(0, 10, "LG에너지솔루션 vs CATL\n포트폴리오 다각화 전략 비교", align="C")
                pdf.ln(30)
                pdf.set_font("Korean", "", 11)
                pdf.set_text_color(73, 80, 87)
                pdf.cell(0, 8, "2026. 03. 17", align="C", new_x="LMARGIN", new_y="NEXT")
                is_first_h1 = False
            else:
                pdf.add_page()
                pdf.set_font("Korean", "B", 18)
                pdf.set_text_color(26, 26, 46)
                pdf.cell(0, 12, stripped[2:], new_x="LMARGIN", new_y="NEXT")
                pdf.set_draw_color(26, 26, 46)
                pdf.set_line_width(0.5)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(6)

            in_reference = "REFERENCE" in stripped.upper()

        # H2
        elif stripped.startswith("## "):
            if last_h3:
                _try_insert_chart(last_h3)
                last_h3 = ""
            if last_h2:
                _try_insert_chart(last_h2)

            h2_text = stripped[3:]
            last_h2 = h2_text
            pdf.ln(4)
            pdf.set_font("Korean", "B", 14)
            pdf.set_text_color(0, 119, 182)
            pdf.cell(0, 10, h2_text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

            if "REFERENCE" in h2_text.upper():
                in_reference = True

        # H3
        elif stripped.startswith("### "):
            if last_h3:
                _try_insert_chart(last_h3)

            h3_text = stripped[4:]
            last_h3 = h3_text
            pdf.ln(3)
            pdf.set_font("Korean", "B", 11)
            pdf.set_text_color(51, 51, 51)
            pdf.cell(0, 8, h3_text, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        elif stripped == "---":
            pdf.ln(5)

        # Reference 섹션 들여쓰기 처리
        elif in_reference:
            pdf.set_font("Korean", "", 9)
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
            text = re.sub(r"\*(.*?)\*", r"\1", text)
            if stripped.startswith("- ") or stripped.startswith("* "):
                text = text[2:]
                pdf.set_text_color(73, 80, 87)
                pdf.cell(5)
                pdf.multi_cell(0, 5.5, f"•  {text}")
                pdf.ln(1.5)
            elif stripped.startswith("####") or stripped.startswith("**"):
                # 카테고리 헤더 (기관 보고서, 웹페이지 등)
                text = stripped.replace("####", "").replace("**", "").strip()
                pdf.ln(3)
                pdf.set_font("Korean", "B", 10)
                pdf.set_text_color(26, 26, 46)
                pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            else:
                pdf.set_text_color(73, 80, 87)
                pdf.cell(5)
                pdf.multi_cell(0, 5.5, text)
                pdf.ln(1.5)

        # 리스트
        elif stripped.startswith("- ") or stripped.startswith("* "):
            pdf.set_font("Korean", "", 10)
            pdf.set_text_color(51, 51, 51)
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped[2:])
            pdf.cell(8)
            pdf.multi_cell(0, 6, f"  •  {text}")
            pdf.ln(1)

        # 일반 텍스트
        else:
            pdf.set_font("Korean", "", 10)
            pdf.set_text_color(51, 51, 51)
            text = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
            pdf.multi_cell(0, 6, text)
            pdf.ln(1)

    if in_table and table_rows:
        _render_table(pdf, table_headers, table_rows)

    # 마지막 섹션 차트 삽입
    if last_h3:
        _try_insert_chart(last_h3)
    if last_h2:
        _try_insert_chart(last_h2)

    # 매핑 안 된 나머지 차트가 있으면 부록으로
    remaining = [p for p in chart_map.values() if os.path.exists(p)]
    if remaining:
        pdf.add_page()
        pdf.set_font("Korean", "B", 16)
        pdf.set_text_color(26, 26, 46)
        pdf.cell(0, 12, "부록: 추가 시각화 자료", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
        for path in remaining:
            pdf.image(path, x=15, w=180)
            pdf.ln(10)

    pdf.output(output_path)


def _render_table(pdf, headers, rows):
    """PDF 테이블 렌더링 헬퍼"""
    if not headers:
        return
    n_cols = len(headers)
    col_w = (pdf.w - 20) / n_cols

    pdf.set_font("Korean", "B", 8)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    for h in headers:
        pdf.cell(col_w, 7, h[:22], border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Korean", "", 8)
    pdf.set_text_color(51, 51, 51)
    for i, row in enumerate(rows):
        pdf.set_fill_color(249, 249, 249) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        for cell in row:
            pdf.cell(col_w, 6, cell[:25], border=1, fill=True, align="C")
        pdf.ln()
    pdf.ln(4)


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
