"""Quality Review Agent — 품질 검증 및 편향 감사"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import GraphState
from prompts.quality_review_prompt import QUALITY_REVIEW_PROMPT
from config import LLM_MODEL


def quality_review_agent(state: GraphState) -> GraphState:
    """보고서 품질 검증 및 편향 검토"""
    report = state.get("full_report", "")

    if not report:
        return {
            **state,
            "quality_passed": False,
            "quality_feedback": "REVISE: 보고서가 비어있습니다. report_writer 재실행 필요.",
        }

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(QUALITY_REVIEW_PROMPT)
    chain = prompt | llm | StrOutputParser()
    review_result = chain.invoke({"report": report})

    # PASS/REVISE 판정 파싱
    is_pass = "PASS" in review_result.split("## 최종 판정")[-1] if "## 최종 판정" in review_result else False

    if is_pass:
        return {
            **state,
            "quality_passed": True,
            "quality_feedback": review_result,
        }
    else:
        return {
            **state,
            "quality_passed": False,
            "quality_feedback": f"REVISE: {review_result}",
        }
