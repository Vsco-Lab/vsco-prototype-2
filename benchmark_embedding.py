"""임베딩 모델 비교 벤치마크"""
import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import DATA_DIR, RAG_FILES, CHUNK_SIZE, CHUNK_OVERLAP

matplotlib.rcParams['font.family'] = 'AppleGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), "benchmark_results")
os.makedirs(BENCHMARK_DIR, exist_ok=True)

# ── 비교 대상 임베딩 모델 ──
MODELS = [
    {
        "name": "multilingual-e5-large",
        "model_id": "intfloat/multilingual-e5-large",
        "dim": 1024,
        "desc": "다국어 대형, MTEB 상위",
    },
    {
        "name": "bge-m3",
        "model_id": "BAAI/bge-m3",
        "dim": 1024,
        "desc": "다국어, 고성능 검색 특화",
    },
    {
        "name": "ko-sroberta",
        "model_id": "jhgan/ko-sroberta-multitask",
        "dim": 768,
        "desc": "한국어 특화, 경량",
    },
]

# ── 검색 품질 평가용 쿼리 + 기대 문서 ──
EVAL_QUERIES = [
    {
        "query": "LG에너지솔루션 2025년 매출 영업이익 실적",
        "expected_source": "02_LG에너지솔루션_전략_분석.md",
    },
    {
        "query": "CATL 나트륨이온 배터리 2026 상용화",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "글로벌 ESS 에너지저장장치 시장 규모 성장",
        "expected_source": "01_글로벌_배터리_시장_환경.md",
    },
    {
        "query": "LG에너지솔루션 CATL 시장점유율 비교 격차",
        "expected_source": "04_양사_비교_데이터.md",
    },
    {
        "query": "미국 IRA 정책 변동 배터리 관세 리스크",
        "expected_source": "05_리스크_외부_환경.md",
    },
    {
        "query": "CATL ESS 글로벌 점유율 아프리카 신흥시장",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "LG에너지솔루션 46시리즈 원통형 배터리 로봇",
        "expected_source": "02_LG에너지솔루션_전략_분석.md",
    },
    {
        "query": "전기차 캐즘 HEV 하이브리드 피벗",
        "expected_source": "01_글로벌_배터리_시장_환경.md",
    },
    {
        "query": "CATL 응축물질 배터리 전고체 기술 로드맵",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "배터리 원자재 리튬 니켈 가격 변동 공급망",
        "expected_source": "05_리스크_외부_환경.md",
    },
]


def load_and_chunk():
    """문서 로드 및 청킹"""
    docs = []
    for fname in RAG_FILES:
        path = os.path.join(DATA_DIR, fname)
        loader = TextLoader(path, encoding="utf-8")
        loaded = loader.load()
        for doc in loaded:
            doc.metadata["source"] = fname
        docs.extend(loaded)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    return splitter.split_documents(docs)


def benchmark_model(model_info, chunks):
    """단일 모델 벤치마크"""
    name = model_info["name"]
    print(f"\n[{name}] 벤치마크 시작...")
    results = {"name": name, "model_id": model_info["model_id"], "dim": model_info["dim"]}

    # 임베딩 모델 로드
    load_start = time.time()
    embeddings = HuggingFaceEmbeddings(
        model_name=model_info["model_id"],
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    results["model_load_time"] = round(time.time() - load_start, 2)
    print(f"  모델 로드: {results['model_load_time']}s")

    # 인덱싱 시간
    start = time.time()
    vs = FAISS.from_documents(chunks, embeddings)
    results["index_time"] = round(time.time() - start, 2)
    print(f"  인덱싱: {results['index_time']}s")

    # 검색 품질 + 속도
    search_times = []
    hit_at_1 = 0  # top-1 정확도
    hit_at_3 = 0  # top-3 정확도
    hit_at_5 = 0  # top-5 정확도
    avg_scores = []
    details = []

    for eq in EVAL_QUERIES:
        start = time.time()
        docs = vs.similarity_search_with_score(eq["query"], k=5)
        elapsed = time.time() - start
        search_times.append(elapsed)

        sources = [d[0].metadata.get("source", "") for d in docs]
        scores = [float(d[1]) for d in docs]
        avg_scores.append(scores[0] if scores else 999)

        expected = eq["expected_source"]
        if sources and sources[0] == expected:
            hit_at_1 += 1
        if expected in sources[:3]:
            hit_at_3 += 1
        if expected in sources[:5]:
            hit_at_5 += 1

        details.append({
            "query": eq["query"][:40],
            "expected": expected,
            "top1_source": sources[0] if sources else "",
            "top1_score": round(scores[0], 4) if scores else None,
            "hit_top1": sources[0] == expected if sources else False,
            "hit_top5": expected in sources[:5],
            "time_ms": round(elapsed * 1000, 1),
        })

    n = len(EVAL_QUERIES)
    results["hit_at_1"] = round(hit_at_1 / n * 100, 1)
    results["hit_at_3"] = round(hit_at_3 / n * 100, 1)
    results["hit_at_5"] = round(hit_at_5 / n * 100, 1)
    results["avg_search_time_ms"] = round(np.mean(search_times) * 1000, 2)
    results["avg_top1_score"] = round(np.mean(avg_scores), 4)
    results["details"] = details

    print(f"  검색 평균: {results['avg_search_time_ms']}ms")
    print(f"  Hit@1: {results['hit_at_1']}% / Hit@3: {results['hit_at_3']}% / Hit@5: {results['hit_at_5']}%")

    return results


def create_visualizations(all_results):
    """비교 시각화 생성"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("임베딩 모델 비교 분석", fontsize=16, fontweight="bold", y=0.98)

    names = [r["name"] for r in all_results]
    colors = ["#0077b6", "#2d6a4f", "#e85d04"]

    # 1. 검색 정확도 (Hit@1, 3, 5)
    ax = axes[0, 0]
    x = np.arange(len(names))
    width = 0.25
    h1 = [r["hit_at_1"] for r in all_results]
    h3 = [r["hit_at_3"] for r in all_results]
    h5 = [r["hit_at_5"] for r in all_results]
    ax.bar(x - width, h1, width, label="Hit@1", color="#1a1a2e")
    ax.bar(x, h3, width, label="Hit@3", color="#0077b6")
    ax.bar(x + width, h5, width, label="Hit@5", color="#90caf9")
    ax.set_title("검색 정확도 (%)", fontsize=13, fontweight="bold")
    ax.set_ylabel("정확도 (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=10)
    ax.legend()
    ax.set_ylim(0, 110)
    ax.grid(axis="y", alpha=0.3)

    # 2. 평균 검색 시간
    ax = axes[0, 1]
    times = [r["avg_search_time_ms"] for r in all_results]
    bars = ax.bar(names, times, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    ax.set_title("평균 검색 시간 (ms)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (ms)")
    for bar, val in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"{val}ms", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_ylim(0, max(times) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 3. 인덱싱 시간
    ax = axes[1, 0]
    idx_times = [r["index_time"] for r in all_results]
    bars = ax.bar(names, idx_times, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    ax.set_title("인덱싱 시간 (초)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (s)")
    for bar, val in zip(bars, idx_times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f"{val}s", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_ylim(0, max(idx_times) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 4. 종합 점수 레이더 대신 비교표 스타일
    ax = axes[1, 1]
    categories = ["Hit@1", "Hit@5", "속도(역수)", "경량성(역수)"]
    for i, r in enumerate(all_results):
        speed_score = 100 / (r["avg_search_time_ms"] / min(rr["avg_search_time_ms"] for rr in all_results))
        size_score = 100 / (r["dim"] / min(rr["dim"] for rr in all_results))
        scores = [r["hit_at_1"], r["hit_at_5"], round(speed_score, 1), round(size_score, 1)]
        ax.plot(categories, scores, marker='o', linewidth=2, label=r["name"], color=colors[i])
        for j, s in enumerate(scores):
            ax.annotate(f"{s}", (j, s), textcoords="offset points", xytext=(0, 8),
                       ha="center", fontsize=9, color=colors[i])
    ax.set_title("종합 성능 비교", fontsize=13, fontweight="bold")
    ax.set_ylim(0, 110)
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    chart_path = os.path.join(BENCHMARK_DIR, "embedding_comparison.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n[시각화] 저장 완료: {chart_path}")

    # ── 종합 비교표 마크다운 ──
    summary_path = os.path.join(BENCHMARK_DIR, "embedding_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# 임베딩 모델 비교 분석 결과\n\n")
        f.write("## 비교 대상\n\n")
        f.write("| 모델 | 차원 | 특징 |\n")
        f.write("|------|------|------|\n")
        for m in MODELS:
            f.write(f"| {m['name']} | {m['dim']} | {m['desc']} |\n")

        f.write("\n## 종합 비교표\n\n")
        f.write("| 항목 | " + " | ".join(r["name"] for r in all_results) + " |\n")
        f.write("|------|" + "|".join(["------"] * len(all_results)) + "|\n")
        f.write(f"| 벡터 차원 | " + " | ".join(str(r["dim"]) for r in all_results) + " |\n")
        f.write(f"| 모델 로드 시간 | " + " | ".join(f"{r['model_load_time']}s" for r in all_results) + " |\n")
        f.write(f"| 인덱싱 시간 | " + " | ".join(f"{r['index_time']}s" for r in all_results) + " |\n")
        f.write(f"| 평균 검색 시간 | " + " | ".join(f"{r['avg_search_time_ms']}ms" for r in all_results) + " |\n")
        f.write(f"| **Hit@1 (정확도)** | " + " | ".join(f"**{r['hit_at_1']}%**" for r in all_results) + " |\n")
        f.write(f"| Hit@3 | " + " | ".join(f"{r['hit_at_3']}%" for r in all_results) + " |\n")
        f.write(f"| Hit@5 | " + " | ".join(f"{r['hit_at_5']}%" for r in all_results) + " |\n")

        # 선정 결론
        best = max(all_results, key=lambda r: r["hit_at_1"])
        f.write(f"\n## 선정 결론\n\n")
        f.write(f"본 프로젝트에서는 **{best['name']}** (`{best['model_id']}`)을 선정하였다.\n\n")
        f.write("**선정 근거:**\n")
        f.write(f"- Hit@1 정확도 {best['hit_at_1']}%로 검색 품질 최우수\n")
        f.write("- 한국어+영어 혼합 문서(배터리 산업 보고서)에 적합\n")
        f.write("- 오픈소스 모델 (경제성 충족)\n")
        f.write("- MTEB 벤치마크 상위권 성능\n")

    print(f"[요약] 저장 완료: {summary_path}")


if __name__ == "__main__":
    print("=" * 50)
    print("  임베딩 모델 비교 벤치마크")
    print("  e5-large vs bge-m3 vs ko-sroberta")
    print("=" * 50)

    chunks = load_and_chunk()
    all_results = []

    for model in MODELS:
        result = benchmark_model(model, chunks)
        all_results.append(result)

    create_visualizations(all_results)

    # JSON 저장
    raw_path = os.path.join(BENCHMARK_DIR, "embedding_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    print("\n완료!")
