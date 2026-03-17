"""Report Writer Agent — 보고서 통합 작성"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState
from prompts.report_writer_prompt import REPORT_WRITER_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE


def report_writer_agent(state: GraphState) -> GraphState:
    """전체 분석 결과를 하나의 보고서로 통합"""
    market = state.get("market_background", {})
    lg = state.get("lg_strategy", {})
    catl = state.get("catl_strategy", {})
    comp = state.get("comparison_swot", {})

    # 모든 참고 자료 취합
    all_refs = []
    for section in [market, lg, catl, comp]:
        all_refs.extend(section.get("references", []))
    unique_refs = list(set(all_refs))

    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_template(REPORT_WRITER_PROMPT)
    chain = prompt | llm | StrOutputParser()

    full_report = chain.invoke({
        "market_content": market.get("content", ""),
        "lg_content": lg.get("content", ""),
        "catl_content": catl.get("content", ""),
        "comparison_content": comp.get("content", ""),
        "references": "\n".join(unique_refs),
    })

    return {
        **state,
        "full_report": full_report,
        "references": unique_refs,
    }
