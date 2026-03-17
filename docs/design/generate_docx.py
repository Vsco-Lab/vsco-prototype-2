"""설계 산출물 docx 생성 스크립트"""
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import os

doc = Document()

# ── 스타일 설정 ──
style = doc.styles['Normal']
style.font.name = '맑은 고딕'
style.font.size = Pt(10)
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.space_after = Pt(4)

for level in range(1, 4):
    h = doc.styles[f'Heading {level}']
    h.font.name = '맑은 고딕'
    h.font.color.rgb = RGBColor(0x1a, 0x1a, 0x2e)

def add_table(doc, headers, rows, col_widths=None):
    """테이블 추가 헬퍼"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 헤더
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.bold = True
                run.font.size = Pt(9)
        # 헤더 배경색
        shading = cell._element.get_or_add_tcPr()
        bg = shading.makeelement(qn('w:shd'), {
            qn('w:fill'): '1a1a2e',
            qn('w:val'): 'clear'
        })
        shading.append(bg)
        for p in cell.paragraphs:
            for run in p.runs:
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # 데이터
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)

    doc.add_paragraph()  # 간격
    return table

def add_note(doc, text):
    """회색 배경 노트"""
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x6c, 0x75, 0x7d)
    run.italic = True

# ═══════════════════════════════════════════
# 표지
# ═══════════════════════════════════════════
for _ in range(6):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('배터리 시장 전략 분석\nMulti-Agent 시스템 설계서')
run.font.size = Pt(28)
run.bold = True
run.font.color.rgb = RGBColor(0x1a, 0x1a, 0x2e)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('LG에너지솔루션 vs CATL\n포트폴리오 다각화 전략 비교')
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(0x6c, 0x75, 0x7d)

for _ in range(6):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('VSCo Prototype v2')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x49, 0x50, 0x57)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('2026.03.17')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(0x49, 0x50, 0x57)

doc.add_page_break()

# ═══════════════════════════════════════════
# 목차
# ═══════════════════════════════════════════
doc.add_heading('목차', level=1)
toc_items = [
    '1. Workflow',
    '   1.1 Goal',
    '   1.2 Criteria (성공 기준)',
    '   1.3 Task 분해',
    '   1.4 Control Strategy',
    '2. System Architecture',
    '   2.1 Agent 구성',
    '   2.2 Agent 상세 정의',
    '3. RAG 설계',
    '   3.1 RAG 대상 문서',
    '   3.2 Embedding 모델',
    '   3.3 벡터DB 및 청킹',
    '   3.4 Agentic RAG 흐름',
    '4. 확증 편향 방지 전략',
    '5. State & Graph',
    '   5.1 GraphState 정의',
    '   5.2 LangGraph 노드 & 엣지',
    '   5.3 상태 전이 흐름',
    '6. 보고서 목차 (초안)',
    '7. Tech Stack',
    '8. 디렉토리 구조',
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.2
    for run in p.runs:
        run.font.size = Pt(10)

doc.add_page_break()

# ═══════════════════════════════════════════
# 1. Workflow
# ═══════════════════════════════════════════
doc.add_heading('1. Workflow', level=1)

doc.add_heading('1.1 Goal', level=2)
p = doc.add_paragraph()
run = p.add_run(
    '전기차 캐즘 여파 속에서 LG에너지솔루션과 CATL의 포트폴리오 다각화 전략을 조사하고, '
    '두 기업의 전략적 차이점과 강약점을 객관적 데이터 기반으로 비교 분석하는 '
    '"배터리 시장 전략 분석 보고서"를 Multi-Agent 기반으로 자동 생성한다.'
)

doc.add_heading('1.2 Criteria (성공 기준)', level=2)
add_table(doc,
    ['#', '성공 기준', '검증 방법'],
    [
        ['C1', '시장 배경, 기업별 전략, SWOT 비교, 시사점 전부 포함', '목차 대조'],
        ['C2', '정량 데이터(매출, 점유율, 캐파 등) 기반 분석', '수치 인용 ≥ 20'],
        ['C3', 'SWOT이 내부(S/W) + 외부(O/T)로 구분', '구조 검증'],
        ['C4', '확증 편향 없이 양사 균형 서술', '긍/부정 30~70% 범위'],
        ['C5', 'SUMMARY(1/2p) + REFERENCE(실활용 자료만)', '형식 검증'],
        ['C6', '출처 형식 준수 (기관보고서/학술논문/웹페이지)', '포맷 검증'],
    ],
    col_widths=[1.5, 9, 4.5]
)

doc.add_heading('1.3 Task 분해', level=2)
add_table(doc,
    ['Task', '설명', '의존성', '담당 Agent'],
    [
        ['T1', '글로벌 배터리 시장 배경 분석', '없음', 'Market Research'],
        ['T2', 'LG에너지솔루션 전략·실적·기술 분석', '없음', 'LG Analysis'],
        ['T3', 'CATL 전략·실적·기술 분석', '없음', 'CATL Analysis'],
        ['T4', '양사 전략 비교 + SWOT 도출', 'T1, T2, T3', 'Comparison'],
        ['T5', '보고서 통합 + SUMMARY/REFERENCE 생성', 'T1~T4', 'Report Writer'],
        ['T6', 'Criteria 검증 + 편향 검토', 'T5', 'Quality Review'],
    ],
    col_widths=[1.5, 6, 3, 4.5]
)

doc.add_heading('1.4 Control Strategy', level=2)
p = doc.add_paragraph()
run = p.add_run('Supervisor 패턴')
run.bold = True
p.add_run(
    '을 채택한다. Supervisor Agent가 전체 파이프라인을 제어하며, '
    '각 Task를 담당 Agent에게 위임하고, 결과를 수신한 뒤 다음 단계 진행 여부를 판단한다.'
)

add_table(doc,
    ['단계', '실행 방식', '설명'],
    [
        ['T1', '순차', '시장 배경 먼저 확보'],
        ['T2 + T3', '병렬', '두 기업 분석은 독립적이므로 동시 실행'],
        ['T4', '순차', 'T1~T3 결과 필요'],
        ['T5', '순차', 'T1~T4 결과 필요'],
        ['T6', '순차', '보고서 완성 후 검증'],
        ['재작업', '조건부 루프', 'QA 미통과 시 최대 2회 재작업'],
    ],
    col_widths=[3, 3, 9]
)

doc.add_page_break()

# ═══════════════════════════════════════════
# 2. System Architecture
# ═══════════════════════════════════════════
doc.add_heading('2. System Architecture', level=1)

add_note(doc, '📎 다이어그램: docs/01_system_architecture.drawio')

# drawio에서 export한 PNG가 있으면 삽입
arch_img = os.path.join(os.path.dirname(__file__), '01_system_architecture.png')
if os.path.exists(arch_img):
    doc.add_picture(arch_img, width=Inches(5.5))
    last_paragraph = doc.paragraphs[-1]
    last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('[System Architecture 다이어그램 — drawio 파일 참조]')
    run.italic = True
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_paragraph()

doc.add_heading('2.1 Agent 구성 (7개)', level=2)
p = doc.add_paragraph('Supervisor가 전체 흐름을 제어하며, 6개 하위 Agent에게 Task를 위임한다.')

add_table(doc,
    ['Agent', '역할', '도구', '입력 → 출력'],
    [
        ['Supervisor', '오케스트레이터, 라우팅', '—', '사용자 요청 → 최종 보고서'],
        ['Market Research', '시장 환경 분석 (T1)', 'RAG, Web Search', '질의 → 시장 배경 섹션'],
        ['LG Analysis', 'LG에너지솔루션 분석 (T2)', 'RAG, Web Search', '질의 → LG 전략 섹션'],
        ['CATL Analysis', 'CATL 분석 (T3)', 'RAG, Web Search', '질의 → CATL 전략 섹션'],
        ['Comparison', '비교 + SWOT (T4)', 'RAG', 'T1~T3 결과 → 비교/SWOT 섹션'],
        ['Report Writer', '보고서 통합 (T5)', '—', 'T1~T4 결과 → 완성 보고서'],
        ['Quality Review', '품질 검증 (T6)', '—', '보고서 초안 → PASS / REVISE'],
    ],
    col_widths=[3, 4, 3, 5]
)

doc.add_heading('2.2 기업별 Agent 분리 설계 (Context Bleed 방지)', level=2)

p = doc.add_paragraph()
p.add_run(
    '본 시스템에서 LG에너지솔루션과 CATL 분석을 하나의 Agent로 통합하지 않고 '
    '별도 Agent로 분리한 이유는 '
)
run = p.add_run('Context Bleed(문맥 오염)')
run.bold = True
p.add_run(' 방지 때문이다.')

doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('문제 정의: ')
run.bold = True
p.add_run(
    '하나의 Agent가 파라미터만 바꿔가며 두 기업을 순차 분석할 경우, '
    'State 내부에 이전 기업의 분석 정보가 잔존하여 다음 기업 분석 시 오염이 발생할 수 있다. '
    '예를 들어, LG에너지솔루션의 ESS 전략 데이터가 CATL 분석 결과에 혼입되거나, '
    '반대로 CATL의 나트륨이온 전략이 LG에너지솔루션 섹션에 잘못 인용될 수 있다.'
)

doc.add_paragraph()
p = doc.add_paragraph()
run = p.add_run('설계 대응:')
run.bold = True

add_table(doc,
    ['설계 항목', '적용 내용'],
    [
        ['Agent 분리', 'LG Analysis Agent와 CATL Analysis Agent를 독립 노드로 구성'],
        ['State 격리', '각 Agent 출력을 lg_strategy, catl_strategy로 별도 필드에 저장'],
        ['RAG 문서 분리', 'LG Agent → 02_LG에너지솔루션.md / CATL Agent → 03_CATL.md'],
        ['병렬 실행', '서로 의존하지 않으므로 병렬 실행 가능'],
    ],
    col_widths=[4, 11]
)

p = doc.add_paragraph(
    '이를 통해 각 기업의 분석 결과가 독립적으로 생성되며, 문맥 오염 없이 '
    'Comparison Agent에서 비로소 양사 데이터가 합쳐져 비교 분석이 이루어진다.'
)

doc.add_heading('2.3 Agent 상세 정의', level=2)

agents_detail = [
    ('Supervisor Agent', [
        '전체 파이프라인 제어 (오케스트레이터)',
        'next_agent 값에 따라 conditional routing',
        '각 Agent 결과의 status 필드 확인 후 다음 단계 결정',
        '재작업: revision_count < 2일 때만 REVISE, 초과 시 강제 PASS',
        '종료 조건: quality_passed == True 또는 revision_count >= 2',
    ]),
    ('Market Research Agent', [
        '글로벌 배터리 시장 환경 분석 → "시장 배경" 챕터 작성',
        '분석 항목: 전기차 캐즘, ESS 성장, 산업 패러다임, 원자재 동향',
        '도구: RAG (01_글로벌_배터리_시장_환경.md), Web Search',
    ]),
    ('LG Analysis Agent', [
        'LG에너지솔루션 전략 분석 → 해당 챕터 작성',
        '분석 항목: 2025 실적, 밸류시프트 전략, ESS/원통형/신시장, 기술 로드맵, 핵심 경쟁력',
        '도구: RAG (02_LG에너지솔루션_전략_분석.md), Web Search',
    ]),
    ('CATL Analysis Agent', [
        'CATL 전략 분석 → 해당 챕터 작성',
        '분석 항목: 2025 실적, All-Domain Growth, 나트륨이온/ESS/배터리스왑, 기술 로드맵, 핵심 경쟁력',
        '도구: RAG (03_CATL_전략_분석.md), Web Search',
    ]),
    ('Comparison Agent', [
        'T1~T3 결과 종합 → 양사 비교 + SWOT 도출',
        '비교 4개 축: 사업 포트폴리오 / 기술 / 지역 / 리스크 대응',
        'SWOT: 내부(S/W) + 외부(O/T) 구분 필수',
        '도구: RAG (04_양사_비교_데이터.md, 05_리스크_외부_환경.md)',
    ]),
    ('Report Writer Agent', [
        'SUMMARY 작성 (핵심 요약, 1/2페이지 이내)',
        'T1~T4 섹션을 목차 순서로 통합, 문체 통일, 중복 제거',
        'REFERENCE 작성 (실제 인용 자료만, 과제 지정 포맷 준수)',
        '도구: 없음 (입력 텍스트만 사용)',
    ]),
    ('Quality Review Agent', [
        'Criteria C1~C6 항목별 PASS/FAIL 판정',
        '확증 편향 감사: 양사별 긍/부정 비율 → 30~70% 범위 확인',
        '데이터 정합성: 수치 오류, 출처 누락 확인',
        '출력: {"quality_passed": bool, "feedback": str}',
    ]),
]

for title, items in agents_detail:
    p = doc.add_paragraph()
    run = p.add_run(title)
    run.bold = True
    run.font.size = Pt(11)
    for item in items:
        doc.add_paragraph(item, style='List Bullet')

doc.add_page_break()

# ═══════════════════════════════════════════
# 3. RAG 설계
# ═══════════════════════════════════════════
doc.add_heading('3. RAG 설계', level=1)

add_note(doc, '📎 다이어그램: docs/02_rag_pipeline.drawio')

rag_img = os.path.join(os.path.dirname(__file__), '02_rag_pipeline.png')
if os.path.exists(rag_img):
    doc.add_picture(rag_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('[RAG Pipeline 다이어그램 — drawio 파일 참조]')
    run.italic = True
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_paragraph()

doc.add_heading('3.1 RAG 대상 문서 (총 5개, ~95 페이지)', level=2)
add_table(doc,
    ['#', '파일명', '페이지', '주요 용도', '사용 Agent'],
    [
        ['1', '01_글로벌_배터리_시장_환경.md', '~15p', '시장 배경', 'Market Research'],
        ['2', '02_LG에너지솔루션_전략_분석.md', '~16p', 'LG 전략', 'LG Analysis'],
        ['3', '03_CATL_전략_분석.md', '~21p', 'CATL 전략', 'CATL Analysis'],
        ['4', '04_양사_비교_데이터.md', '~17p', '비교 데이터', 'Comparison'],
        ['5', '05_리스크_외부_환경.md', '~20p', '리스크', 'Comparison'],
    ],
    col_widths=[1, 5, 1.5, 3, 3.5]
)

doc.add_heading('3.2 Embedding 모델 선정', level=2)
add_table(doc,
    ['항목', '내용'],
    [
        ['모델', 'intfloat/multilingual-e5-large'],
        ['선정 이유', '한국어+영어 혼합 문서 대응, 오픈소스(무료), MTEB 벤치마크 상위'],
        ['대안', 'BAAI/bge-m3 (다국어), jhgan/ko-sroberta-multitask (한국어)'],
        ['벡터 차원', '1024'],
        ['최대 토큰', '512'],
    ],
    col_widths=[4, 11]
)

doc.add_heading('3.3 벡터DB 및 청킹', level=2)
add_table(doc,
    ['항목', '설정', '근거'],
    [
        ['벡터DB', 'FAISS', '로컬 실행, 설치 간편, 소규모 문서에 적합'],
        ['청킹', 'RecursiveCharacterTextSplitter', '섹션 구조 유지'],
        ['청크 크기', '1,000자', '한국어 기준 충분한 문맥'],
        ['오버랩', '200자', '청크 경계 정보 손실 방지'],
        ['검색', 'Similarity Search (top-k=5)', '관련 청크 5개 반환'],
        ['메타데이터', '문서명 + 섹션 제목', '출처 추적용'],
    ],
    col_widths=[3, 5, 7]
)

doc.add_heading('3.4 Agentic RAG 흐름', level=2)
flow_items = [
    'Agent가 질의를 생성한다.',
    'Query Rewriting: LLM이 질의를 검색 최적화 형태로 변환한다.',
    'FAISS에서 top-k=5 유사도 검색을 수행한다.',
    '관련성 판단: LLM이 검색 결과가 질의에 충분히 답할 수 있는지 판단한다.',
    '충분한 경우 → RAG 결과만으로 답변을 생성한다.',
    '부족한 경우 → Serper.dev Web Search로 보충 검색 후, RAG + 웹 결과를 통합하여 답변을 생성한다.',
]
for i, item in enumerate(flow_items, 1):
    doc.add_paragraph(f'{i}. {item}')

doc.add_page_break()

# ═══════════════════════════════════════════
# 4. 확증 편향 방지 전략
# ═══════════════════════════════════════════
doc.add_heading('4. 확증 편향 방지 전략', level=1)

add_note(doc, '📎 다이어그램: docs/03_bias_prevention.drawio')

bias_img = os.path.join(os.path.dirname(__file__), '03_bias_prevention.png')
if os.path.exists(bias_img):
    doc.add_picture(bias_img, width=Inches(5.5))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
else:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('[Bias Prevention 다이어그램 — drawio 파일 참조]')
    run.italic = True
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('Step 1. Dual-Direction Search (양방향 검색)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph('각 기업에 대해 긍정/부정 검색을 반드시 쌍으로 실행한다.')
doc.add_paragraph('• 긍정 검색: "{기업명} 성과 강점 성장 실적"')
doc.add_paragraph('• 부정 검색: "{기업명} 리스크 약점 과제 우려 적자"')
doc.add_paragraph('→ LG에너지솔루션 2회 + CATL 2회 = 기업당 최소 4회 검색')
doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('Step 2. Cross-Validation (교차 검증)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph('한 기업의 강점 주장을 상대 기업 관점에서 재검증한다.')
doc.add_paragraph('• 예: "LG에너지솔루션 북미 우위" → "CATL 북미 우회 전략" 추가 검색')
doc.add_paragraph('• 양쪽 정보를 병렬 제시하여 독자가 판단할 수 있도록 한다.')
doc.add_paragraph()

p = doc.add_paragraph()
run = p.add_run('Step 3. Balance Audit (Quality Review Agent)')
run.bold = True
run.font.size = Pt(12)
doc.add_paragraph('최종 보고서에서 양사별 긍정/부정 서술 비율을 계산한다.')
doc.add_paragraph('• 30~70% 범위 내: PASS')
doc.add_paragraph('• 범위 이탈: REVISE (해당 섹션 재작성 지시)')

doc.add_page_break()

# ═══════════════════════════════════════════
# 5. State & Graph
# ═══════════════════════════════════════════
doc.add_heading('5. State & Graph', level=1)

doc.add_heading('5.1 GraphState 정의', level=2)

code = """class ReportSection(TypedDict):
    title: str              # 섹션 제목
    content: str            # 마크다운 내용
    references: List[str]   # 참고 자료
    status: str             # "pending" | "completed" | "revision_needed"

class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    market_background: ReportSection
    lg_strategy: ReportSection
    catl_strategy: ReportSection
    comparison_swot: ReportSection
    summary: str
    full_report: str
    references: List[str]
    next_agent: str         # Supervisor 라우팅 대상
    revision_count: int     # 재작업 횟수 (max 2)
    quality_feedback: str
    quality_passed: bool"""

p = doc.add_paragraph()
run = p.add_run(code)
run.font.name = 'Consolas'
run.font.size = Pt(8.5)

doc.add_heading('5.2 LangGraph 노드 & 엣지', level=2)

code2 = """workflow = StateGraph(GraphState)

# 노드 등록
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("market_research", market_research_agent)
workflow.add_node("lg_analysis", lg_analysis_agent)
workflow.add_node("catl_analysis", catl_analysis_agent)
workflow.add_node("comparison", comparison_agent)
workflow.add_node("report_writer", report_writer_agent)
workflow.add_node("quality_review", quality_review_agent)

# Supervisor → 각 Agent (conditional routing)
workflow.set_entry_point("supervisor")
workflow.add_conditional_edges("supervisor", route_next_agent, {
    "market_research": "market_research",
    "lg_analysis": "lg_analysis",
    "catl_analysis": "catl_analysis",
    "comparison": "comparison",
    "report_writer": "report_writer",
    "quality_review": "quality_review",
    "FINISH": END,
})

# 각 Agent → Supervisor (복귀)
for node in ["market_research", "lg_analysis", "catl_analysis",
             "comparison", "report_writer", "quality_review"]:
    workflow.add_edge(node, "supervisor")

graph = workflow.compile()"""

p = doc.add_paragraph()
run = p.add_run(code2)
run.font.name = 'Consolas'
run.font.size = Pt(8.5)

doc.add_heading('5.3 상태 전이 흐름', level=2)
transitions = [
    ('[START] revision_count=0',),
    ('[Supervisor] → "market_research"',),
    ('[Market Research] → market_background.status = "completed"',),
    ('[Supervisor] → "lg_analysis" → "catl_analysis" (병렬 가능)',),
    ('[LG + CATL Analysis] → 각 status = "completed"',),
    ('[Supervisor] → "comparison"',),
    ('[Comparison] → comparison_swot.status = "completed"',),
    ('[Supervisor] → "report_writer"',),
    ('[Report Writer] → full_report 생성',),
    ('[Supervisor] → "quality_review"',),
    ('[Quality Review] PASS → "FINISH" → [END]',),
    ('[Quality Review] REVISE → revision_count++ → Supervisor → 재실행 (max 2)',),
]
for t in transitions:
    p = doc.add_paragraph(t[0])
    for run in p.runs:
        run.font.name = 'Consolas'
        run.font.size = Pt(9)

doc.add_page_break()

# ═══════════════════════════════════════════
# 6. 보고서 목차
# ═══════════════════════════════════════════
doc.add_heading('6. 보고서 목차 (초안)', level=1)

outline = [
    ('1. SUMMARY', '전체 보고서 핵심 요약 (1/2페이지 이내)'),
    ('2. 시장 배경', ''),
    ('   2.1 글로벌 전기차 캐즘 현황', ''),
    ('   2.2 ESS 시장의 급부상', ''),
    ('   2.3 배터리 산업 패러다임 전환', ''),
    ('   2.4 원자재 및 정책 환경 변화', ''),
    ('3. LG에너지솔루션 전략 분석', ''),
    ('   3.1 사업 실적 및 현황', ''),
    ('   3.2 밸류 시프트(Value Shift) 전략', ''),
    ('   3.3 ESS·원통형·신시장 다각화', ''),
    ('   3.4 기술 로드맵', ''),
    ('   3.5 핵심 경쟁력', ''),
    ('4. CATL 전략 분석', ''),
    ('   4.1 사업 실적 및 현황', ''),
    ('   4.2 All-Domain Growth 전략', ''),
    ('   4.3 나트륨이온·ESS·배터리스왑 다각화', ''),
    ('   4.4 기술 로드맵', ''),
    ('   4.5 핵심 경쟁력', ''),
    ('5. 핵심 전략 비교 및 SWOT 분석', ''),
    ('   5.1 전략 비교 (사업/기술/지역/리스크 대응)', ''),
    ('   5.2 LG에너지솔루션 SWOT', ''),
    ('   5.3 CATL SWOT', ''),
    ('   5.4 양사 SWOT 비교 종합', ''),
    ('6. 종합 시사점', ''),
    ('   6.1 전략적 차이점 요약', ''),
    ('   6.2 한국 배터리 산업 시사점', ''),
    ('   6.3 향후 전망', ''),
    ('7. REFERENCE', '기관 보고서 / 학술 논문 / 웹페이지'),
]
for title, desc in outline:
    p = doc.add_paragraph()
    run = p.add_run(title)
    run.bold = not title.startswith('   ')
    run.font.size = Pt(10)
    if desc:
        run2 = p.add_run(f'  — {desc}')
        run2.font.size = Pt(9)
        run2.font.color.rgb = RGBColor(0x6c, 0x75, 0x7d)
    p.paragraph_format.space_after = Pt(2)

doc.add_page_break()

# ═══════════════════════════════════════════
# 7. Tech Stack
# ═══════════════════════════════════════════
doc.add_heading('7. Tech Stack', level=1)
add_table(doc,
    ['Category', 'Details'],
    [
        ['Language', 'Python 3.11+'],
        ['Framework', 'LangGraph, LangChain'],
        ['LLM', 'GPT-4o-mini (OpenAI API)'],
        ['Embedding', 'intfloat/multilingual-e5-large (HuggingFace, 오픈소스)'],
        ['Vector DB', 'FAISS'],
        ['Web Search', 'Serper.dev (Google Search API, 무료 2,500회)'],
        ['Output', 'Markdown → PDF (WeasyPrint / md-to-pdf)'],
    ],
    col_widths=[4, 11]
)

# ═══════════════════════════════════════════
# 8. 디렉토리 구조
# ═══════════════════════════════════════════
doc.add_heading('8. 디렉토리 구조', level=1)

dir_structure = """vsco-prototype-2/
├── data/                        # RAG 문서 (5개, ~95p)
│   ├── 01_글로벌_배터리_시장_환경.md
│   ├── 02_LG에너지솔루션_전략_분석.md
│   ├── 03_CATL_전략_분석.md
│   ├── 04_양사_비교_데이터.md
│   └── 05_리스크_외부_환경.md
├── agents/                      # Agent 모듈
│   ├── supervisor.py
│   ├── market_research.py
│   ├── lg_analysis.py
│   ├── catl_analysis.py
│   ├── comparison.py
│   ├── report_writer.py
│   └── quality_review.py
├── tools/                       # 공유 도구
│   ├── rag_tool.py
│   └── web_search_tool.py
├── prompts/                     # 프롬프트 템플릿
├── vectorstore/                 # FAISS 인덱스
├── outputs/                     # 생성 보고서
├── docs/                        # 설계 문서 & 다이어그램
├── app.py                       # 메인 실행
├── graph.py                     # LangGraph 정의
├── state.py                     # State 정의
├── config.py                    # 설정
├── ingest.py                    # 문서 임베딩 & 벡터DB
├── requirements.txt
└── README.md"""

p = doc.add_paragraph()
run = p.add_run(dir_structure)
run.font.name = 'Consolas'
run.font.size = Pt(8.5)

# ═══════════════════════════════════════════
# 저장
# ═══════════════════════════════════════════
output_path = os.path.join(os.path.dirname(__file__), '설계_산출물.docx')
doc.save(output_path)
print(f'✅ 저장 완료: {output_path}')
