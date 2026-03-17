"""LangGraph State 정의"""
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages


class ReportSection(TypedDict):
    """보고서 개별 섹션"""
    title: str
    content: str
    references: List[str]
    status: str  # "pending" | "completed" | "revision_needed"


def create_empty_section(title: str) -> ReportSection:
    """빈 섹션 생성 헬퍼"""
    return ReportSection(
        title=title,
        content="",
        references=[],
        status="pending",
    )


class GraphState(TypedDict):
    """전체 그래프 상태"""
    # 메시지 히스토리
    messages: Annotated[list, add_messages]

    # 각 섹션 결과
    market_background: ReportSection
    lg_strategy: ReportSection
    catl_strategy: ReportSection
    comparison_swot: ReportSection

    # 보고서 최종본
    summary: str
    full_report: str
    references: List[str]

    # 제어 상태
    next_agent: str
    revision_count: int
    quality_feedback: str
    quality_passed: bool
