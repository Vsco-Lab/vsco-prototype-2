"""벡터DB 비교 벤치마크: FAISS vs Chroma"""
import os
import time
import json
import psutil
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from config import DATA_DIR, RAG_FILES, EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

matplotlib.rcParams['font.family'] = 'AppleGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# ── 벤치마크 설정 ──
BENCHMARK_DIR = os.path.join(os.path.dirname(__file__), "benchmark_results")
os.makedirs(BENCHMARK_DIR, exist_ok=True)

TEST_QUERIES = [
    "LG에너지솔루션 2025년 매출 영업이익",
    "CATL 나트륨이온 배터리 상용화 시점",
    "글로벌 ESS 시장 규모 성장률 전망",
    "전기차 캐즘 원인과 HEV 피벗",
    "LG에너지솔루션 CATL 시장점유율 비교",
    "배터리 원자재 리튬 가격 변동",
    "CATL 해외 공장 유럽 인도네시아",
    "전고체 배터리 기술 로드맵 양산",
    "IRA 정책 변동 K-배터리 영향",
    "배터리스왑 EVOGO 서비스 전략",
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
    chunks = splitter.split_documents(docs)
    print(f"[benchmark] {len(docs)}개 문서 → {len(chunks)}개 청크")
    return chunks


def get_embeddings():
    """임베딩 모델 로드"""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def benchmark_faiss(chunks, embeddings):
    """FAISS 벤치마크"""
    print("\n[FAISS] 벤치마크 시작...")
    results = {"name": "FAISS"}

    # 인덱싱 시간
    mem_before = psutil.Process().memory_info().rss / 1024 / 1024
    start = time.time()
    vs = FAISS.from_documents(chunks, embeddings)
    results["index_time"] = round(time.time() - start, 3)
    mem_after = psutil.Process().memory_info().rss / 1024 / 1024
    results["memory_mb"] = round(mem_after - mem_before, 1)
    print(f"  인덱싱: {results['index_time']}s / 메모리: {results['memory_mb']}MB")

    # 검색 시간 (10개 쿼리 평균)
    search_times = []
    search_results = []
    for q in TEST_QUERIES:
        start = time.time()
        docs = vs.similarity_search_with_score(q, k=5)
        elapsed = time.time() - start
        search_times.append(elapsed)
        search_results.append({
            "query": q,
            "time": round(elapsed, 4),
            "top1_score": round(float(docs[0][1]), 4) if docs else None,
            "top1_source": docs[0][0].metadata.get("source", "") if docs else "",
            "top1_preview": docs[0][0].page_content[:80] if docs else "",
        })

    results["avg_search_time"] = round(np.mean(search_times) * 1000, 2)  # ms
    results["min_search_time"] = round(np.min(search_times) * 1000, 2)
    results["max_search_time"] = round(np.max(search_times) * 1000, 2)
    results["search_details"] = search_results
    print(f"  검색 평균: {results['avg_search_time']}ms")

    # 저장 크기
    tmp_path = os.path.join(BENCHMARK_DIR, "faiss_tmp")
    vs.save_local(tmp_path)
    total_size = sum(
        os.path.getsize(os.path.join(tmp_path, f))
        for f in os.listdir(tmp_path)
    )
    results["disk_mb"] = round(total_size / 1024 / 1024, 2)
    print(f"  디스크: {results['disk_mb']}MB")

    return results


def benchmark_chroma(chunks, embeddings):
    """Chroma 벤치마크"""
    print("\n[Chroma] 벤치마크 시작...")
    results = {"name": "Chroma"}

    chroma_path = os.path.join(BENCHMARK_DIR, "chroma_tmp")
    if os.path.exists(chroma_path):
        import shutil
        shutil.rmtree(chroma_path)

    # 인덱싱 시간
    mem_before = psutil.Process().memory_info().rss / 1024 / 1024
    start = time.time()
    vs = Chroma.from_documents(
        chunks, embeddings, persist_directory=chroma_path
    )
    results["index_time"] = round(time.time() - start, 3)
    mem_after = psutil.Process().memory_info().rss / 1024 / 1024
    results["memory_mb"] = round(mem_after - mem_before, 1)
    print(f"  인덱싱: {results['index_time']}s / 메모리: {results['memory_mb']}MB")

    # 검색 시간
    search_times = []
    search_results = []
    for q in TEST_QUERIES:
        start = time.time()
        docs = vs.similarity_search_with_score(q, k=5)
        elapsed = time.time() - start
        search_times.append(elapsed)
        search_results.append({
            "query": q,
            "time": round(elapsed, 4),
            "top1_score": round(float(docs[0][1]), 4) if docs else None,
            "top1_source": docs[0][0].metadata.get("source", "") if docs else "",
            "top1_preview": docs[0][0].page_content[:80] if docs else "",
        })

    results["avg_search_time"] = round(np.mean(search_times) * 1000, 2)
    results["min_search_time"] = round(np.min(search_times) * 1000, 2)
    results["max_search_time"] = round(np.max(search_times) * 1000, 2)
    results["search_details"] = search_results
    print(f"  검색 평균: {results['avg_search_time']}ms")

    # 저장 크기
    total_size = 0
    for root, dirs, files in os.walk(chroma_path):
        for f in files:
            total_size += os.path.getsize(os.path.join(root, f))
    results["disk_mb"] = round(total_size / 1024 / 1024, 2)
    print(f"  디스크: {results['disk_mb']}MB")

    return results


def create_visualizations(faiss_results, chroma_results):
    """비교 시각화 생성"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("벡터DB 비교 분석: FAISS vs Chroma", fontsize=16, fontweight="bold", y=0.98)

    names = ["FAISS", "Chroma"]
    colors = ["#0077b6", "#e85d04"]

    # 1. 인덱싱 시간
    ax = axes[0, 0]
    times = [faiss_results["index_time"], chroma_results["index_time"]]
    bars = ax.bar(names, times, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    ax.set_title("인덱싱 시간 (초)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (s)")
    for bar, val in zip(bars, times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val}s", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_ylim(0, max(times) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 2. 평균 검색 시간
    ax = axes[0, 1]
    search_times = [faiss_results["avg_search_time"], chroma_results["avg_search_time"]]
    bars = ax.bar(names, search_times, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    ax.set_title("평균 검색 시간 (ms)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (ms)")
    for bar, val in zip(bars, search_times):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f"{val}ms", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_ylim(0, max(search_times) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 3. 디스크 사용량
    ax = axes[1, 0]
    disk = [faiss_results["disk_mb"], chroma_results["disk_mb"]]
    bars = ax.bar(names, disk, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
    ax.set_title("디스크 사용량 (MB)", fontsize=13, fontweight="bold")
    ax.set_ylabel("크기 (MB)")
    for bar, val in zip(bars, disk):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f"{val}MB", ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_ylim(0, max(disk) * 1.3)
    ax.grid(axis="y", alpha=0.3)

    # 4. 쿼리별 검색 시간 비교
    ax = axes[1, 1]
    x = np.arange(len(TEST_QUERIES))
    width = 0.35
    faiss_qtimes = [d["time"] * 1000 for d in faiss_results["search_details"]]
    chroma_qtimes = [d["time"] * 1000 for d in chroma_results["search_details"]]
    ax.bar(x - width/2, faiss_qtimes, width, label="FAISS", color=colors[0], alpha=0.85)
    ax.bar(x + width/2, chroma_qtimes, width, label="Chroma", color=colors[1], alpha=0.85)
    ax.set_title("쿼리별 검색 시간 (ms)", fontsize=13, fontweight="bold")
    ax.set_ylabel("시간 (ms)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"Q{i+1}" for i in range(len(TEST_QUERIES))], fontsize=9)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    chart_path = os.path.join(BENCHMARK_DIR, "vectordb_comparison.png")
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n[시각화] 저장 완료: {chart_path}")

    # ── 종합 비교표 생성 ──
    summary_path = os.path.join(BENCHMARK_DIR, "vectordb_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# 벡터DB 비교 분석 결과\n\n")
        f.write("## 종합 비교표\n\n")
        f.write("| 항목 | FAISS | Chroma | 우위 |\n")
        f.write("|------|-------|--------|------|\n")
        f.write(f"| 인덱싱 시간 | {faiss_results['index_time']}s | {chroma_results['index_time']}s | {'FAISS' if faiss_results['index_time'] < chroma_results['index_time'] else 'Chroma'} |\n")
        f.write(f"| 평균 검색 시간 | {faiss_results['avg_search_time']}ms | {chroma_results['avg_search_time']}ms | {'FAISS' if faiss_results['avg_search_time'] < chroma_results['avg_search_time'] else 'Chroma'} |\n")
        f.write(f"| 디스크 사용량 | {faiss_results['disk_mb']}MB | {chroma_results['disk_mb']}MB | {'FAISS' if faiss_results['disk_mb'] < chroma_results['disk_mb'] else 'Chroma'} |\n")
        f.write(f"| 메모리 증가량 | {faiss_results['memory_mb']}MB | {chroma_results['memory_mb']}MB | {'FAISS' if faiss_results['memory_mb'] < chroma_results['memory_mb'] else 'Chroma'} |\n")
        f.write(f"| 최소 검색 시간 | {faiss_results['min_search_time']}ms | {chroma_results['min_search_time']}ms | {'FAISS' if faiss_results['min_search_time'] < chroma_results['min_search_time'] else 'Chroma'} |\n")
        f.write(f"| 최대 검색 시간 | {faiss_results['max_search_time']}ms | {chroma_results['max_search_time']}ms | {'FAISS' if faiss_results['max_search_time'] < chroma_results['max_search_time'] else 'Chroma'} |\n")

        f.write("\n## 선정 결론\n\n")
        f.write("본 프로젝트에서는 **FAISS**를 선정하였다.\n\n")
        f.write("**선정 근거:**\n")
        f.write("- 소규모 문서(5개, ~95페이지)에 적합한 경량 솔루션\n")
        f.write("- 외부 서버 불필요 (로컬 파일 기반)\n")
        f.write("- LangChain 공식 통합 지원\n")
        f.write("- 설치 및 설정이 간편하여 프로토타입에 적합\n")

        f.write("\n## 쿼리별 상세 결과\n\n")
        f.write("| # | 쿼리 | FAISS (ms) | Chroma (ms) |\n")
        f.write("|---|------|-----------|------------|\n")
        for i, (fq, cq) in enumerate(zip(faiss_results["search_details"], chroma_results["search_details"])):
            f.write(f"| Q{i+1} | {fq['query'][:30]}... | {fq['time']*1000:.1f} | {cq['time']*1000:.1f} |\n")

    print(f"[요약] 저장 완료: {summary_path}")


if __name__ == "__main__":
    print("=" * 50)
    print("  벡터DB 비교 벤치마크")
    print("  FAISS vs Chroma")
    print("=" * 50)

    chunks = load_and_chunk()
    embeddings = get_embeddings()

    faiss_results = benchmark_faiss(chunks, embeddings)
    chroma_results = benchmark_chroma(chunks, embeddings)

    create_visualizations(faiss_results, chroma_results)

    # JSON 저장
    raw_path = os.path.join(BENCHMARK_DIR, "benchmark_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump({"faiss": faiss_results, "chroma": chroma_results}, f, ensure_ascii=False, indent=2, default=str)
    print(f"[원본] 저장 완료: {raw_path}")

    print("\n완료!")
