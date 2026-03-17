"""LG Analysis Agent — LG에너지솔루션 전략 분석 (Context Bleed 방지: CATL 정보 격리)"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState, ReportSection
from tools.rag_tool import rag_search
from tools.web_search_tool import search_with_bias_prevention, web_search
from prompts.research_prompts import LG_ANALYSIS_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def lg_analysis_agent(state: GraphState) -> GraphState:
    """LG에너지솔루션 전략 분석 섹션 작성 (RAG + 웹 검색 강제 병행)"""
    rag_queries = [
        "LG에너지솔루션 2025 매출 영업이익 실적",
        "LG에너지솔루션 밸류 시프트 ESS 전략",
        "LG에너지솔루션 46시리즈 원통형 로봇 배터리",
        "LG에너지솔루션 전고체 기술 로드맵 LFP",
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
        company="LG에너지솔루션",
        topic="포트폴리오 다각화 전략 ESS 2026",
        competitor="CATL",
    )
    web_extra = web_search("LG에너지솔루션 2026 실적 전망 46시리즈 로봇 배터리")

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
    prompt = ChatPromptTemplate.from_template(LG_ANALYSIS_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"context": context})

    section = ReportSection(
        title="3. LG에너지솔루션 전략 분석",
        content=content,
        references=list(set(rag_sources)),
        status="completed",
    )

    return {**state, "lg_strategy": section}
