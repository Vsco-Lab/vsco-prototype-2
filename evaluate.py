"""RAG 품질 평가 (RAGAS) + 보고서 품질 평가 (LLM-as-a-Judge)"""
import os
import json
import glob
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.rag_tool import rag_search
from config import LLM_MODEL, OUTPUT_DIR

EVAL_DIR = os.path.join(os.path.dirname(__file__), "evaluation_results")
os.makedirs(EVAL_DIR, exist_ok=True)


# ═══════════════════════════════════════════
# 1. RAG 품질 평가
# ═══════════════════════════════════════════

RAG_EVAL_QUERIES = [
    {
        "query": "LG에너지솔루션 2025년 매출과 영업이익은?",
        "expected_answer": "매출 23조 6,718억원, 영업이익 1조 3,461억원",
        "expected_source": "02_LG에너지솔루션_전략_분석.md",
    },
    {
        "query": "CATL의 2025년 글로벌 EV 배터리 시장점유율은?",
        "expected_answer": "39.2%로 글로벌 1위",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "2026년 글로벌 ESS 설치 용량 전망은?",
        "expected_answer": "359GWh",
        "expected_source": "01_글로벌_배터리_시장_환경.md",
    },
    {
        "query": "LG에너지솔루션의 2026년 ESS 신규 수주 목표는?",
        "expected_answer": "90GWh 이상",
        "expected_source": "02_LG에너지솔루션_전략_분석.md",
    },
    {
        "query": "CATL의 나트륨이온 배터리 승용차 주행거리는?",
        "expected_answer": "500km 이상",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "CATL의 2025년 R&D 투자 규모는?",
        "expected_answer": "221억 위안, 약 4조 7,700억원",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "미국 IRA 전기차 세액공제 조기 종료 시점은?",
        "expected_answer": "2026년 12월 31일로 앞당기는 법안",
        "expected_source": "05_리스크_외부_환경.md",
    },
    {
        "query": "LG에너지솔루션과 CATL의 매출 격차는 몇 배인가?",
        "expected_answer": "약 3.4배",
        "expected_source": "04_양사_비교_데이터.md",
    },
    {
        "query": "CATL의 인도네시아 투자 규모는?",
        "expected_answer": "50억 달러",
        "expected_source": "03_CATL_전략_분석.md",
    },
    {
        "query": "리튬 가격은 2022년 대비 2024년에 얼마나 하락했나?",
        "expected_answer": "톤당 70,000달러에서 15,000달러 미만으로 78% 이상 하락",
        "expected_source": "05_리스크_외부_환경.md",
    },
]


def evaluate_rag():
    """RAG 검색 품질 평가"""
    print("\n[RAG 평가] 시작...")
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    results = []

    for i, eq in enumerate(RAG_EVAL_QUERIES):
        rag_result = rag_search(eq["query"])
        context = rag_result["context"]
        sources = rag_result["sources"]

        # 1. Context Relevancy — 검색된 문맥이 질문과 관련 있는가
        relevancy_prompt = ChatPromptTemplate.from_template(
            "다음 질문에 대해 검색된 문맥이 얼마나 관련성이 있는지 1~10점으로 평가하세요.\n\n"
            "질문: {query}\n\n문맥:\n{context}\n\n"
            "점수(숫자만):"
        )
        relevancy_score = int(
            (relevancy_prompt | llm | StrOutputParser())
            .invoke({"query": eq["query"], "context": context[:2000]})
            .strip().split()[0].replace("점", "")
        )

        # 2. Faithfulness — 문맥에서 정답을 도출할 수 있는가
        faith_prompt = ChatPromptTemplate.from_template(
            "다음 문맥만으로 정답을 도출할 수 있는지 1~10점으로 평가하세요.\n\n"
            "질문: {query}\n기대 정답: {expected}\n\n문맥:\n{context}\n\n"
            "점수(숫자만):"
        )
        faith_score = int(
            (faith_prompt | llm | StrOutputParser())
            .invoke({"query": eq["query"], "expected": eq["expected_answer"], "context": context[:2000]})
            .strip().split()[0].replace("점", "")
        )

        # 3. Source Accuracy — 올바른 문서에서 검색했는가
        source_hit = 1 if eq["expected_source"] in sources else 0

        results.append({
            "query": eq["query"],
            "expected_source": eq["expected_source"],
            "retrieved_sources": sources,
            "source_hit": source_hit,
            "context_relevancy": relevancy_score,
            "faithfulness": faith_score,
        })
        print(f"  Q{i+1}: 관련성={relevancy_score} 충실도={faith_score} 출처={'O' if source_hit else 'X'}")

    # 종합 점수
    n = len(results)
    summary = {
        "avg_context_relevancy": round(sum(r["context_relevancy"] for r in results) / n, 2),
        "avg_faithfulness": round(sum(r["faithfulness"] for r in results) / n, 2),
        "source_accuracy": round(sum(r["source_hit"] for r in results) / n * 100, 1),
        "total_queries": n,
        "details": results,
    }
    print(f"\n[RAG 평가 결과]")
    print(f"  문맥 관련성: {summary['avg_context_relevancy']}/10")
    print(f"  충실도: {summary['avg_faithfulness']}/10")
    print(f"  출처 정확도: {summary['source_accuracy']}%")
    return summary


# ═══════════════════════════════════════════
# 2. 보고서 품질 평가 (LLM-as-a-Judge)
# ═══════════════════════════════════════════

REPORT_EVAL_PROMPT = """당신은 전략 분석 보고서를 평가하는 전문 심사위원입니다.

다음 보고서를 읽고, 6개 항목에 대해 각각 1~10점으로 평가하세요.

## 평가 항목

1. **데이터 정확성** (1~10): 인용된 수치·사실 관계가 정확하고 구체적인가
2. **분석 깊이** (1~10): 단순 나열이 아닌, 전략적 인사이트와 해석이 포함되어 있는가
3. **균형성** (1~10): 두 기업(LG에너지솔루션, CATL)을 편향 없이 균형 있게 서술했는가
4. **최신성** (1~10): 2025~2026년 기준의 최신 정보가 반영되어 있는가
5. **구조 완성도** (1~10): SUMMARY~REFERENCE까지 보고서 구조가 적절하고 논리적 흐름이 있는가
6. **실용성** (1~10): 실제 의사결정에 참고할 수 있는 수준의 분석인가

## 출력 형식 (반드시 이 JSON 형식으로만 출력)

```json
{{
  "데이터_정확성": {{"score": 8, "reason": "이유"}},
  "분석_깊이": {{"score": 7, "reason": "이유"}},
  "균형성": {{"score": 9, "reason": "이유"}},
  "최신성": {{"score": 7, "reason": "이유"}},
  "구조_완성도": {{"score": 8, "reason": "이유"}},
  "실용성": {{"score": 7, "reason": "이유"}}
}}
```

## 보고서 전문
{report}
"""


def evaluate_report(report_path: str = None):
    """보고서 품질 평가 (LLM-as-a-Judge)"""
    # 가장 최근 보고서 찾기
    if not report_path:
        md_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "report_*.md")))
        if not md_files:
            print("[보고서 평가] 보고서 파일이 없습니다.")
            return None
        report_path = md_files[-1]

    print(f"\n[보고서 평가] 대상: {os.path.basename(report_path)}")

    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_template(REPORT_EVAL_PROMPT)
    chain = prompt | llm | StrOutputParser()

    raw_result = chain.invoke({"report": report[:12000]})

    # JSON 파싱
    try:
        json_str = raw_result.split("```json")[-1].split("```")[0].strip() if "```json" in raw_result else raw_result
        scores = json.loads(json_str)
    except json.JSONDecodeError:
        print("[보고서 평가] JSON 파싱 실패, 재시도...")
        retry_prompt = ChatPromptTemplate.from_template(
            "다음 텍스트에서 JSON만 추출하세요:\n{text}\n\nJSON:"
        )
        retry_result = (retry_prompt | llm | StrOutputParser()).invoke({"text": raw_result})
        try:
            scores = json.loads(retry_result.strip())
        except json.JSONDecodeError:
            scores = {"error": "파싱 실패", "raw": raw_result}

    # 종합 점수 계산
    if "error" not in scores:
        total = sum(v["score"] for v in scores.values())
        avg = round(total / len(scores), 2)
        summary = {
            "report_file": os.path.basename(report_path),
            "scores": scores,
            "total_score": total,
            "average_score": avg,
            "max_score": 60,
            "grade": "A" if avg >= 8 else "B" if avg >= 6.5 else "C" if avg >= 5 else "D",
        }
        print(f"\n[보고서 평가 결과]")
        for k, v in scores.items():
            print(f"  {k}: {v['score']}/10 — {v['reason']}")
        print(f"\n  종합: {total}/60 (평균 {avg}/10) — 등급 {summary['grade']}")
    else:
        summary = scores

    return summary


# ═══════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print("  품질 평가 시스템")
    print("  RAG 평가 (RAGAS 기반) + 보고서 평가 (LLM-as-a-Judge)")
    print("=" * 55)

    # RAG 평가
    rag_result = evaluate_rag()

    # 보고서 평가
    report_result = evaluate_report()

    # 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    eval_path = os.path.join(EVAL_DIR, f"evaluation_{timestamp}.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "rag_evaluation": rag_result,
            "report_evaluation": report_result,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n[저장] {eval_path}")
