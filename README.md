# 배터리 시장 전략 분석 보고서 — Multi-Agent System

전기차 캐즘 여파 속에서 글로벌 TOP-Tier 배터리 업체인 **LG에너지솔루션**과 **CATL**의 포트폴리오 다각화 전략을 조사하고, 두 기업의 전략적 차이점과 강약점을 객관적 데이터 기반으로 비교 분석하는 **배터리 시장 전략 분석 보고서**를 Supervisor 패턴 기반 Multi-Agent 시스템으로 자동 생성합니다.

## Overview

- **Objective** : LG에너지솔루션 vs CATL 포트폴리오 다각화 전략 비교 분석 보고서 자동 생성
- **Method** : Supervisor Pattern 기반 Multi-Agent + Agentic RAG
- **Tools** : LangGraph, FAISS, Serper.dev, GPT-4o-mini

## Features

- Agentic RAG 기반 정보 검색 : 5개 자체 제작 문서(~95p)를 벡터DB에 적재하고, Query Rewriting → 유사도 검색 → 관련성 판단 → 부족 시 웹 검색 보완의 파이프라인을 적용
- 확증 편향 방지 전략 : 양방향 검색(긍정/부정 쌍 동시 실행) + 교차 검증(상대 기업 관점 재확인) + 균형 감사(긍/부정 비율 30~70% 범위 검증)
- Context Bleed 방지 : LG에너지솔루션과 CATL 분석 Agent를 독립 노드로 분리하고, State 필드(`lg_strategy`, `catl_strategy`)를 격리하여 문맥 오염 차단
- 품질 검증 루프 : 6개 Criteria(목차·수치·SWOT 구조·편향·형식·출처)를 자동 검증하고, 미달 시 최대 2회 재작성 지시

## Tech Stack

| Category   | Details                                |
|------------|----------------------------------------|
| Framework  | LangGraph, LangChain, Python           |
| LLM        | GPT-4o-mini via OpenAI API             |
| Retrieval  | FAISS                                  |
| Embedding  | BAAI/bge-m3 (오픈소스)                  |
| Web Search | Serper.dev (Google Search API)         |

## Embedding 모델 선정

설계 단계에서는 `intfloat/multilingual-e5-large`를 기본 임베딩 모델로 선정하였으나, 개발 과정에서 3개 오픈소스 모델에 대한 벤치마크를 실시한 결과, **`BAAI/bge-m3`가 Hit@1 정확도 80%로 가장 우수**하여 최종 모델을 변경하였다.

| 항목 | multilingual-e5-large | bge-m3 | ko-sroberta |
|------|----------------------|--------|-------------|
| 벡터 차원 | 1024 | 1024 | 768 |
| 인덱싱 시간 | 24.0s | 25.0s | 2.0s |
| 평균 검색 시간 | 113.2ms | 107.2ms | 41.4ms |
| **Hit@1 (정확도)** | 70.0% | **80.0%** | **80.0%** |
| Hit@5 | 100.0% | 100.0% | 100.0% |

> `ko-sroberta`도 Hit@1 80%로 동일했으나, 모델 로드 시간(53.5s vs 5.2s)과 벡터 차원(768 vs 1024)에서 `bge-m3`가 더 균형 잡힌 성능을 보여 최종 선정하였다.

![임베딩 모델 비교 분석](docs/embedding_comparison.png)

## Agents

- **Supervisor Agent** : 전체 파이프라인 제어, 상태 기반 라우팅, 재작업 판단
- **Market Research Agent** : 글로벌 배터리 시장 환경 분석 (캐즘, ESS, 정책 변화)
- **LG Analysis Agent** : LG에너지솔루션 전략·실적·기술 분석
- **CATL Analysis Agent** : CATL 전략·실적·기술 분석
- **Comparison & SWOT Agent** : 양사 4축 비교(사업/기술/지역/리스크) + SWOT 도출
- **Report Writer Agent** : SUMMARY + 본문 통합 + REFERENCE 생성
- **Quality Review Agent** : Criteria 검증 + 편향 감사 (PASS/REVISE)

## Architecture

![시스템 아키텍처](docs/architecture.png)

## Directory Structure

```
├── data/                          # RAG 문서 (5개, ~95p)
│   ├── 01_글로벌_배터리_시장_환경.md
│   ├── 02_LG에너지솔루션_전략_분석.md
│   ├── 03_CATL_전략_분석.md
│   ├── 04_양사_비교_데이터.md
│   └── 05_리스크_외부_환경.md
├── agents/                        # Agent 모듈
│   ├── supervisor.py
│   ├── market_research.py
│   ├── lg_analysis.py
│   ├── catl_analysis.py
│   ├── comparison.py
│   ├── report_writer.py
│   └── quality_review.py
├── tools/                         # 공유 도구
│   ├── rag_tool.py               # Agentic RAG
│   └── web_search_tool.py        # Serper.dev + 편향 방지
├── prompts/                       # 프롬프트 템플릿
├── vectorstore/                   # FAISS 인덱스
├── outputs/                       # 생성 보고서
├── docs/                          # 설계 문서 & 다이어그램
├── app.py                         # 메인 실행
├── graph.py                       # LangGraph 그래프 정의
├── state.py                       # State 정의
├── config.py                      # 설정
└── ingest.py                      # 문서 임베딩 & 벡터DB
```

## How to Run

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY, SERPER_API_KEY 입력

# 3. 실행
python app.py
```

## Contributors

- 양정우 : Agent 설계, RAG 파이프라인, 프롬프트 엔지니어링
