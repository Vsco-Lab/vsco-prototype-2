"""웹 검색 도구 비교: Tavily vs Serper.dev"""
import os
import time
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

matplotlib.rcParams['font.family'] = 'AppleGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

from dotenv import load_dotenv
load_dotenv()

os.environ["TAVILY_API_KEY"] = "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"

BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), "benchmark_results")
os.makedirs(BENCHMARK_DIR, exist_ok=True)

TEST_QUERIES = [
    "LG에너지솔루션 2026 ESS 전략 실적",
    "CATL sodium-ion battery 2026 commercialization",
    "글로벌 전기차 배터리 시장 캐즘 2026",
    "CATL 나트륨이온 배터리 상용화",
    "LG에너지솔루션 CATL 시장점유율 비교 2025",
    "배터리 ESS 시장 성장 AI 데이터센터 2026",
    "IRA 전기차 보조금 정책 변화 트럼프 2026",
    "CATL 해외 공장 유럽 인도네시아 확장",
]


def benchmark_serper():
    """Serper.dev 벤치마크"""
    from langchain_community.utilities import GoogleSerperAPIWrapper
    print("\n[Serper.dev] 벤치마크 시작...")
    search = GoogleSerperAPIWrapper(k=5)
    results = {"name": "Serper.dev"}

    times = []
    lengths = []
    for q in TEST_QUERIES:
        start = time.time()
        result = search.run(q)
        elapsed = time.time() - start
        times.append(elapsed)
        lengths.append(len(result))

    results["avg_time"] = round(np.mean(times) * 1000, 1)
    results["min_time"] = round(np.min(times) * 1000, 1)
    results["max_time"] = round(np.max(times) * 1000, 1)
    results["avg_length"] = round(np.mean(lengths))
    results["times"] = [round(t * 1000, 1) for t in times]
    results["cost"] = "무료 2,500회/월"

    print(f"  평균 응답: {results['avg_time']}ms")
    print(f"  평균 결과 길이: {results['avg_length']}자")
    return results


def benchmark_tavily():
    """Tavily 벤치마크"""
    from tavily import TavilyClient
    print("\n[Tavily] 벤치마크 시작...")
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    results = {"name": "Tavily"}

    times = []
    lengths = []
    for q in TEST_QUERIES:
        start = time.time()
        response = client.search(query=q, max_results=5)
        elapsed = time.time() - start
        times.append(elapsed)
        content = " ".join([r.get("content", "") for r in response.get("results", [])])
        lengths.append(len(content))

    results["avg_time"] = round(np.mean(times) * 1000, 1)
    results["min_time"] = round(np.min(times) * 1000, 1)
    results["max_time"] = round(np.max(times) * 1000, 1)
    results["avg_length"] = round(np.mean(lengths))
    results["times"] = [round(t * 1000, 1) for t in times]
    results["cost"] = "무료 1,000회/월"

    print(f"  평균 응답: {results['avg_time']}ms")
    print(f"  평균 결과 길이: {results['avg_length']}자")
    return results


def create_visualization(serper, tavily):
    """비교 시각화"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("웹 검색 도구 비교: Serper.dev vs Tavily", fontsize=16, fontweight="bold", y=1.02)

    names = ["Serper.dev", "Tavily"]
    colors = ["#0077b6", "#e85d04"]

    # 1. 평균 응답 시간
    ax = axes[0]
    times = [serper["avg_time"], tavily["avg_time"]]
    bars = ax.bar(names, times, color=colors, width=0.4)
    for bar, val in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f"{val}ms", ha="center", fontweight="bold", fontsize=11)
    ax.set_title("평균 응답 시간 (ms)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (ms)")
    ax.set_ylim(0, max(times) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 2. 평균 결과 길이
    ax = axes[1]
    lens = [serper["avg_length"], tavily["avg_length"]]
    bars = ax.bar(names, lens, color=colors, width=0.4)
    for bar, val in zip(bars, lens):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f"{val}자", ha="center", fontweight="bold", fontsize=11)
    ax.set_title("평균 결과 길이 (자)", fontsize=13, fontweight="bold")
    ax.set_ylabel("길이 (자)")
    ax.set_ylim(0, max(lens) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 3. 쿼리별 시간 비교
    ax = axes[2]
    x = np.arange(len(TEST_QUERIES))
    width = 0.35
    ax.bar(x - width/2, serper["times"], width, label="Serper.dev", color=colors[0])
    ax.bar(x + width/2, tavily["times"], width, label="Tavily", color=colors[1])
    ax.set_title("쿼리별 응답 시간 (ms)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (ms)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Q{i+1}" for i in range(len(TEST_QUERIES))], fontsize=9)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(BENCHMARK_DIR, "websearch_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n[시각화] 저장: {path}")
    return path


if __name__ == "__main__":
    print("=" * 50)
    print("  웹 검색 도구 비교: Serper.dev vs Tavily")
    print("=" * 50)

    serper = benchmark_serper()
    tavily = benchmark_tavily()
    create_visualization(serper, tavily)

    # JSON 저장
    raw_path = os.path.join(BENCHMARK_DIR, "websearch_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({"serper": serper, "tavily": tavily}, f, ensure_ascii=False, indent=2)

    print(f"\n[비교 요약]")
    print(f"  {'항목':<15} {'Serper.dev':<15} {'Tavily':<15}")
    print(f"  {'평균 응답':<15} {serper['avg_time']}ms{'':<8} {tavily['avg_time']}ms")
    print(f"  {'결과 길이':<15} {serper['avg_length']}자{'':<8} {tavily['avg_length']}자")
    print(f"  {'무료 한도':<15} {serper['cost']:<15} {tavily['cost']}")
    print("\n완료!")
