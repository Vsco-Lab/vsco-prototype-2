"""CATL Analysis Agent — CATL 전략 분석 (Context Bleed 방지: LG 정보 격리)"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState, ReportSection
from tools.rag_tool import rag_search
from tools.web_search_tool import search_with_bias_prevention
from prompts.research_prompts import CATL_ANALYSIS_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def catl_analysis_agent(state: GraphState) -> GraphState:
    """CATL 전략 분석 섹션 작성"""
    queries = [
        "CATL 2025 매출 순이익 시장점유율 실적",
        "CATL All-Domain Growth 전략 ESS",
        "CATL 나트륨이온 배터리 상용화 배터리스왑",
        "CATL 응축물질 전고체 기술 로드맵 Shenxing",
    ]

    all_context = []
    all_sources = []
    needs_web = False

    for q in queries:
        result = rag_search(q)
        all_context.append(result["context"])
        all_sources.extend(result["sources"])
        if result["needs_web"]:
            needs_web = True

    # 편향 방지 웹 검색 (긍정+부정 쌍)
    if needs_web:
        web_result = search_with_bias_prevention(
            company="CATL",
            topic="포트폴리오 다각화 전략",
            competitor="LG에너지솔루션",
        )
        all_context.append(f"[웹 검색 결과]\n{web_result['all_text']}")

    context = "\n\n---\n\n".join(all_context)

    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(CATL_ANALYSIS_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"context": context})

    section = ReportSection(
        title="4. CATL 전략 분석",
        content=content,
        references=list(set(all_sources)),
        status="completed",
    )

    return {**state, "catl_strategy": section}
