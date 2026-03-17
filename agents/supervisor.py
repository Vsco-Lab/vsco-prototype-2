"""Supervisor Agent — 전체 파이프라인 제어"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import GraphState
from prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT
from config import LLM_MODEL, LLM_TEMPERATURE, MAX_REVISION_COUNT

AGENTS = [
    "market_research",
    "lg_analysis",
    "catl_analysis",
    "comparison",
    "report_writer",
    "quality_review",
    "FINISH",
]


def supervisor_agent(state: GraphState) -> GraphState:
    """Supervisor: 상태를 보고 다음 Agent를 결정"""

    # 품질 검증 통과 시 종료
    if state.get("quality_passed", False):
        return {**state, "next_agent": "FINISH"}

    # 재작업 횟수 초과 시 강제 종료
    if state.get("revision_count", 0) >= MAX_REVISION_COUNT:
        return {**state, "next_agent": "FINISH"}

    # 상태 기반 라우팅
    market = state.get("market_background", {})
    lg = state.get("lg_strategy", {})
    catl = state.get("catl_strategy", {})
    comp = state.get("comparison_swot", {})
    report = state.get("full_report", "")

    # 순서대로 미완료 단계 찾기
    if market.get("status") != "completed":
        next_agent = "market_research"
    elif lg.get("status") != "completed":
        next_agent = "lg_analysis"
    elif catl.get("status") != "completed":
        next_agent = "catl_analysis"
    elif comp.get("status") != "completed":
        next_agent = "comparison"
    elif not report:
        next_agent = "report_writer"
    elif not state.get("quality_passed", False):
        next_agent = "quality_review"
    else:
        next_agent = "FINISH"

    # 품질 검증에서 REVISE된 경우 피드백 기반 재라우팅
    feedback = state.get("quality_feedback", "")
    if feedback and "REVISE" in feedback:
        revision_count = state.get("revision_count", 0) + 1
        if "시장" in feedback:
            next_agent = "market_research"
        elif "LG" in feedback:
            next_agent = "lg_analysis"
        elif "CATL" in feedback:
            next_agent = "catl_analysis"
        elif "비교" in feedback or "SWOT" in feedback:
            next_agent = "comparison"
        else:
            next_agent = "report_writer"
        return {
            **state,
            "next_agent": next_agent,
            "revision_count": revision_count,
            "quality_feedback": "",
        }

    return {**state, "next_agent": next_agent}


def route_next_agent(state: GraphState) -> str:
    """Supervisor의 라우팅 함수 (conditional edge용)"""
    return state.get("next_agent", "FINISH")
