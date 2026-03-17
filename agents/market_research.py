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
    """시장 배경 분석 섹션 작성"""
    queries = [
        "글로벌 전기차 캐즘 현황 판매량 성장률",
        "ESS 에너지저장장치 시장 규모 성장 전망",
        "배터리 산업 패러다임 전환 기술 다변화",
        "배터리 원자재 리튬 가격 IRA 정책 변화",
    ]

    # RAG 검색
    all_context = []
    all_sources = []
    needs_web = False

    for q in queries:
        result = rag_search(q)
        all_context.append(result["context"])
        all_sources.extend(result["sources"])
        if result["needs_web"]:
            needs_web = True

    # 웹 검색 보완 (RAG 부족 시)
    if needs_web:
        web_results = web_search("글로벌 배터리 시장 2026 전망 ESS 캐즘")
        all_context.append(f"[웹 검색 결과]\n{web_results}")

    context = "\n\n---\n\n".join(all_context)

    # LLM으로 섹션 작성
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(MARKET_RESEARCH_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"context": context})

    section = ReportSection(
        title="2. 시장 배경",
        content=content,
        references=list(set(all_sources)),
        status="completed",
    )

    return {**state, "market_background": section}
