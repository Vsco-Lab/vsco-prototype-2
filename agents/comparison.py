"""Comparison & SWOT Agent — 양사 비교 분석 및 SWOT 도출"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState, ReportSection
from tools.rag_tool import rag_search
from prompts.comparison_prompt import COMPARISON_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def comparison_agent(state: GraphState) -> GraphState:
    """양사 비교 및 SWOT 분석 섹션 작성"""
    # 이전 Agent 결과 가져오기
    lg_content = state.get("lg_strategy", {}).get("content", "")
    catl_content = state.get("catl_strategy", {}).get("content", "")
    market_content = state.get("market_background", {}).get("content", "")

    # RAG에서 비교 데이터 + 리스크 문서 검색
    queries = [
        "LG에너지솔루션 CATL 시장점유율 매출 비교",
        "LG에너지솔루션 CATL 기술 전략 비교 SWOT",
        "배터리 기업 리스크 관세 지정학 IRA",
    ]

    all_context = []
    all_sources = []
    for q in queries:
        result = rag_search(q)
        all_context.append(result["context"])
        all_sources.extend(result["sources"])

    context = "\n\n".join(all_context)

    # LLM으로 비교 분석 작성
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(COMPARISON_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({
        "lg_content": lg_content,
        "catl_content": catl_content,
        "market_content": market_content,
        "context": context,
    })

    section = ReportSection(
        title="5. 핵심 전략 비교 및 SWOT 분석",
        content=content,
        references=list(set(all_sources)),
        status="completed",
    )

    return {**state, "comparison_swot": section}
