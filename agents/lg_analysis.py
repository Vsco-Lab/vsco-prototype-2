"""LG Analysis Agent — LG에너지솔루션 전략 분석 (Context Bleed 방지: CATL 정보 격리)"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState, ReportSection
from tools.rag_tool import rag_search
from tools.web_search_tool import search_with_bias_prevention
from prompts.research_prompts import LG_ANALYSIS_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def lg_analysis_agent(state: GraphState) -> GraphState:
    """LG에너지솔루션 전략 분석 섹션 작성"""
    queries = [
        "LG에너지솔루션 2025 매출 영업이익 실적",
        "LG에너지솔루션 밸류 시프트 ESS 전략",
        "LG에너지솔루션 46시리즈 원통형 로봇 배터리",
        "LG에너지솔루션 전고체 기술 로드맵 LFP",
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
            company="LG에너지솔루션",
            topic="포트폴리오 다각화 전략",
            competitor="CATL",
        )
        all_context.append(f"[웹 검색 결과]\n{web_result['all_text']}")

    context = "\n\n---\n\n".join(all_context)

    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(LG_ANALYSIS_PROMPT)
    chain = prompt | llm | StrOutputParser()
    content = chain.invoke({"context": context})

    section = ReportSection(
        title="3. LG에너지솔루션 전략 분석",
        content=content,
        references=list(set(all_sources)),
        status="completed",
    )

    return {**state, "lg_strategy": section}
