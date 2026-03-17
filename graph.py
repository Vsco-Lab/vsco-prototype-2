"""LangGraph 워크플로우 그래프 정의"""
from langgraph.graph import StateGraph, END
from state import GraphState
from agents.supervisor import supervisor_agent, route_next_agent
from agents.market_research import market_research_agent
from agents.lg_analysis import lg_analysis_agent
from agents.catl_analysis import catl_analysis_agent
from agents.comparison import comparison_agent
from agents.report_writer import report_writer_agent
from agents.quality_review import quality_review_agent


def build_graph():
    """Supervisor 패턴 기반 그래프 구성"""
    workflow = StateGraph(GraphState)

    # 노드 등록
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("market_research", market_research_agent)
    workflow.add_node("lg_analysis", lg_analysis_agent)
    workflow.add_node("catl_analysis", catl_analysis_agent)
    workflow.add_node("comparison", comparison_agent)
    workflow.add_node("report_writer", report_writer_agent)
    workflow.add_node("quality_review", quality_review_agent)

    # 진입점: Supervisor
    workflow.set_entry_point("supervisor")

    # Supervisor → 각 Agent (conditional routing)
    workflow.add_conditional_edges(
        "supervisor",
        route_next_agent,
        {
            "market_research": "market_research",
            "lg_analysis": "lg_analysis",
            "catl_analysis": "catl_analysis",
            "comparison": "comparison",
            "report_writer": "report_writer",
            "quality_review": "quality_review",
            "FINISH": END,
        },
    )

    # 각 Agent → Supervisor 복귀
    for node in [
        "market_research",
        "lg_analysis",
        "catl_analysis",
        "comparison",
        "report_writer",
        "quality_review",
    ]:
        workflow.add_edge(node, "supervisor")

    return workflow.compile()
