"""Market Research Agent — 글로벌 배터리 시장 환경 분석"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState, ReportSection
from tools.rag_tool import rag_search
from tools.web_search_tool import web_search
from prompts.research_prompts import MARKET_RESEARCH_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def market_research_agent(state: GraphState) -> GraphState:
    """시장 배경 분석 섹션 작성 (RAG + 웹 검색 강제 병행)"""
    rag_queries = [
        "글로벌 전기차 캐즘 현황 판매량 성장률",
        "ESS 에너지저장장치 시장 규모 성장 전망",
        "배터리 산업 패러다임 전환 기술 다변화",
        "배터리 원자재 리튬 가격 IRA 정책 변화",
    ]

    web_queries = [
        "글로벌 전기차 판매량 2026 캐즘 최신",
        "ESS 에너지저장장치 시장 성장 2026 AI 데이터센터",
        "배터리 원자재 리튬 니켈 가격 2026 전망",
        "트럼프 IRA 전기차 보조금 정책 변화 2026",
    ]

    # 1. RAG 검색 (기초 데이터)
    rag_context = []
    rag_sources = []
    for q in rag_queries:
        result = rag_search(q)
        rag_context.append(result["context"])
        rag_sources.extend(result["sources"])

    # 2. 웹 검색 (최신 자료 — 항상 실행)
    web_context = []
    for q in web_queries:
        web_result = web_search(q)
        web_context.append(web_result)

    context = (
        "=== RAG 문서 기반 자료 ===\n"
        + "\n\n".join(rag_context)
        + "\n\n=== 웹 검색 최신 자료 ===\n"
        + "\n\n".join(web_context)
    )

    # 3. LLM으로 섹션 작성
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(MARKET_RESEARCH_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"context": context})

    section = ReportSection(
        title="2. 시장 배경",
        content=content,
        references=list(set(rag_sources)),
        status="completed",
    )

    return {**state, "market_background": section}
