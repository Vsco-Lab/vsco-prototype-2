"""CATL Analysis Agent — CATL 전략 분석 (Context Bleed 방지: LG 정보 격리)"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState, ReportSection
from tools.rag_tool import rag_search
from tools.web_search_tool import search_with_bias_prevention, web_search
from prompts.research_prompts import CATL_ANALYSIS_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def catl_analysis_agent(state: GraphState) -> GraphState:
    """CATL 전략 분석 섹션 작성 (RAG + 웹 검색 강제 병행)"""
    rag_queries = [
        "CATL 2025 매출 순이익 시장점유율 실적",
        "CATL All-Domain Growth 전략 ESS",
        "CATL 나트륨이온 배터리 상용화 배터리스왑",
        "CATL 응축물질 전고체 기술 로드맵 Shenxing",
    ]

    # 1. RAG 검색 (기초 데이터)
    rag_context = []
    rag_sources = []
    for q in rag_queries:
        result = rag_search(q)
        rag_context.append(result["context"])
        rag_sources.extend(result["sources"])

    # 2. 웹 검색 (최신 자료 — 항상 실행, 편향 방지 적용)
    bias_result = search_with_bias_prevention(
        company="CATL",
        topic="포트폴리오 다각화 전략 나트륨이온 2026",
        competitor="LG에너지솔루션",
    )
    web_extra = web_search("CATL 2026 sodium-ion ESS battery swap global expansion")

    context = (
        "=== RAG 문서 기반 자료 ===\n"
        + "\n\n".join(rag_context)
        + "\n\n=== 웹 검색 최신 자료 (편향 방지 적용) ===\n"
        + bias_result["all_text"]
        + "\n\n=== 웹 검색 추가 자료 ===\n"
        + web_extra
    )

    # 3. LLM으로 섹션 작성
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(CATL_ANALYSIS_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"context": context})

    section = ReportSection(
        title="4. CATL 전략 분석",
        content=content,
        references=list(set(rag_sources)),
        status="completed",
    )

    return {**state, "catl_strategy": section}
