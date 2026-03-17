"""웹 검색 도구 (Serper.dev + 확증 편향 방지)"""
from langchain_community.utilities import GoogleSerperAPIWrapper
from config import SERPER_API_KEY
import os

os.environ["SERPER_API_KEY"] = SERPER_API_KEY


def web_search(query: str, num_results: int = 5) -> str:
    """단일 웹 검색 실행"""
    search = GoogleSerperAPIWrapper(k=num_results)
    return search.run(query)


def dual_direction_search(company: str, topic: str = "") -> dict:
    """
    양방향 검색 (Dual-Direction Search)
    긍정/부정 검색을 쌍으로 실행하여 확증 편향 방지

    Args:
        company: 기업명 (예: "LG에너지솔루션", "CATL")
        topic: 검색 주제 (예: "ESS 전략", "나트륨이온")

    Returns:
        {"positive": str, "negative": str, "combined": str}
    """
    topic_str = f" {topic}" if topic else ""

    positive_query = f"{company}{topic_str} 성과 강점 성장 실적 2025 2026"
    negative_query = f"{company}{topic_str} 리스크 약점 과제 우려 적자 2025 2026"

    positive_results = web_search(positive_query)
    negative_results = web_search(negative_query)

    combined = (
        f"=== {company} 긍정적 측면 ===\n{positive_results}\n\n"
        f"=== {company} 부정적 측면 ===\n{negative_results}"
    )

    return {
        "positive": positive_results,
        "negative": negative_results,
        "combined": combined,
    }


def cross_validation_search(
    company: str, claim: str, competitor: str
) -> str:
    """
    교차 검증 (Cross-Validation)
    한 기업의 강점 주장을 상대 기업 관점에서 재검증

    Args:
        company: 주장 기업 (예: "LG에너지솔루션")
        claim: 강점 주장 (예: "북미 시장 우위")
        competitor: 상대 기업 (예: "CATL")

    Returns:
        검증 결과 텍스트
    """
    verify_query = f"{competitor} {claim} 대응 전략 2025 2026"
    return web_search(verify_query)


def search_with_bias_prevention(
    company: str, topic: str = "", competitor: str = ""
) -> dict:
    """
    편향 방지 전략이 적용된 종합 검색

    Args:
        company: 대상 기업
        topic: 검색 주제
        competitor: 상대 기업 (교차 검증용)

    Returns:
        {"dual_results": dict, "cross_validation": str, "all_text": str}
    """
    # Step 1: 양방향 검색
    dual = dual_direction_search(company, topic)

    # Step 2: 교차 검증 (상대 기업이 지정된 경우)
    cross = ""
    if competitor and topic:
        cross = cross_validation_search(company, topic, competitor)

    all_text = dual["combined"]
    if cross:
        all_text += f"\n\n=== 교차 검증: {competitor} 관점 ===\n{cross}"

    return {
        "dual_results": dual,
        "cross_validation": cross,
        "all_text": all_text,
    }
