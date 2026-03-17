"""RAG 문서 5개를 하나의 PDF로 합치는 스크립트 (fpdf2)"""
import os
import re
from fpdf import FPDF

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUTPUT = os.path.join(DATA_DIR, 'RAG_전체문서.pdf')

FILES = [
    '01_글로벌_배터리_시장_환경.md',
    '02_LG에너지솔루션_전략_분석.md',
    '03_CATL_전략_분석.md',
    '04_양사_비교_데이터.md',
    '05_리스크_외부_환경.md',
]

FONT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_REGULAR = os.path.join(FONT_DIR, 'NanumGothic.ttf')
FONT_BOLD = os.path.join(FONT_DIR, 'NanumGothicBold.ttf')


class RAGDocument(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font('Korean', '', FONT_REGULAR)
        self.add_font('Korean', 'B', FONT_BOLD)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Korean', '', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, 'Battery Strategy Analysis - RAG Document', align='R')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Korean', '', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'{self.page_no()}', align='C')

    def add_cover(self):
        self.add_page()
        self.ln(60)
        self.set_font('Korean', 'B', 26)
        self.set_text_color(26, 26, 46)
        self.multi_cell(0, 14, '배터리 시장 전략 분석\nRAG Reference Document', align='C')
        self.ln(15)
        self.set_font('Korean', '', 14)
        self.set_text_color(108, 117, 125)
        self.multi_cell(0, 10, 'LG에너지솔루션 vs CATL\n포트폴리오 다각화 전략 비교', align='C')
        self.ln(40)
        self.set_font('Korean', '', 11)
        self.set_text_color(73, 80, 87)
        self.cell(0, 8, '총 5개 문서 / ~95 페이지 / 2026.03.17', align='C')

    def parse_and_render(self, md_text):
        lines = md_text.split('\n')
        in_table = False
        table_rows = []
        table_headers = []

        for line in lines:
            stripped = line.strip()

            # 빈 줄
            if not stripped:
                if in_table and table_rows:
                    self._render_table(table_headers, table_rows)
                    in_table = False
                    table_rows = []
                    table_headers = []
                self.ln(3)
                continue

            # 테이블 구분선 (|---|---|)
            if re.match(r'^\|[-\s|:]+\|$', stripped):
                continue

            # 테이블 행
            if stripped.startswith('|') and stripped.endswith('|'):
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                if not in_table:
                    in_table = True
                    table_headers = cells
                else:
                    table_rows.append(cells)
                continue

            # 테이블 종료 체크
            if in_table:
                self._render_table(table_headers, table_rows)
                in_table = False
                table_rows = []
                table_headers = []

            # H1
            if stripped.startswith('# ') and not stripped.startswith('## '):
                self.add_page()
                self.set_font('Korean', 'B', 18)
                self.set_text_color(26, 26, 46)
                title = stripped[2:]
                self.cell(0, 12, title, new_x='LMARGIN', new_y='NEXT')
                self.set_draw_color(26, 26, 46)
                self.set_line_width(0.5)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(6)
                continue

            # H2
            if stripped.startswith('## '):
                self.ln(4)
                self.set_font('Korean', 'B', 13)
                self.set_text_color(0, 119, 182)
                self.cell(0, 10, stripped[3:], new_x='LMARGIN', new_y='NEXT')
                self.set_draw_color(224, 224, 224)
                self.set_line_width(0.3)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(3)
                continue

            # H3
            if stripped.startswith('### '):
                self.ln(3)
                self.set_font('Korean', 'B', 11)
                self.set_text_color(51, 51, 51)
                self.cell(0, 8, stripped[4:], new_x='LMARGIN', new_y='NEXT')
                self.ln(2)
                continue

            # HR
            if stripped == '---':
                self.ln(5)
                self.set_draw_color(200, 200, 200)
                self.set_line_width(0.2)
                self.line(10, self.get_y(), 200, self.get_y())
                self.ln(5)
                continue

            # 리스트 항목
            if stripped.startswith('- ') or stripped.startswith('* '):
                self.set_font('Korean', '', 10)
                self.set_text_color(51, 51, 51)
                text = stripped[2:]
                # bold 처리 간이
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
                self.cell(8)
                self.multi_cell(0, 6, f'  •  {text}')
                self.ln(1)
                continue

            # 일반 텍스트
            self.set_font('Korean', '', 10)
            self.set_text_color(51, 51, 51)
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
            self.multi_cell(0, 6, text)
            self.ln(1)

        # 남은 테이블
        if in_table and table_rows:
            self._render_table(table_headers, table_rows)

    def _render_table(self, headers, rows):
        if not headers:
            return

        n_cols = len(headers)
        page_w = self.w - 20  # margins
        col_w = page_w / n_cols

        # 헤더
        self.set_font('Korean', 'B', 8)
        self.set_fill_color(26, 26, 46)
        self.set_text_color(255, 255, 255)
        for h in headers:
            self.cell(col_w, 7, h[:20], border=1, fill=True, align='C')
        self.ln()

        # 데이터
        self.set_font('Korean', '', 8)
        self.set_text_color(51, 51, 51)
        for i, row in enumerate(rows):
            if i % 2 == 0:
                self.set_fill_color(249, 249, 249)
            else:
                self.set_fill_color(255, 255, 255)
            for j, cell in enumerate(row):
                text = cell[:25] if len(cell) > 25 else cell
                self.cell(col_w, 6, text, border=1, fill=True, align='C')
            self.ln()

        self.ln(4)


# ── 생성 ──
pdf = RAGDocument()
pdf.add_cover()

for fname in FILES:
    path = os.path.join(DATA_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    pdf.parse_and_render(content)

pdf.output(OUTPUT)
print(f'✅ PDF 생성 완료: {OUTPUT}')
print(f'   총 페이지: {pdf.page_no()}')
