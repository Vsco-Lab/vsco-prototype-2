# 배터리 시장 전략 분석 보고서 — Multi-Agent System

전기차 캐즘 여파 속에서 글로벌 TOP-Tier 배터리 업체인 **LG에너지솔루션**과 **CATL**의 포트폴리오 다각화 전략을 조사하고, 두 기업의 전략적 차이점과 강약점을 객관적 데이터 기반으로 비교 분석하는 **배터리 시장 전략 분석 보고서**를 Multi-Agent 기반으로 자동 생성합니다.

## Overview

- **Objective** : LG에너지솔루션 vs CATL 포트폴리오 다각화 전략 비교 분석 보고서 자동 생성
- **Method** : Supervisor Pattern 기반 Multi-Agent + Agentic RAG
- **Tools** : LangGraph, FAISS, Serper.dev, GPT-4o-mini

## Features

- **Agentic RAG** : 5개 문서(~95p) 기반 벡터 검색 + 관련성 판단 + 웹 보완
- **확증 편향 방지** : 양방향 검색(긍정/부정 쌍) + 교차 검증 + 균형 감사(30~70%)
- **Context Bleed 방지** : LG / CATL 분석 Agent 분리, State 필드 격리
- **품질 검증 루프** : 6개 Criteria 자동 검증, 미달 시 최대 2회 재작성

## Tech Stack

| Category   | Details                                              |
|------------|------------------------------------------------------|
| Framework  | LangGraph, LangChain, Python                         |
| LLM        | GPT-4o-mini via OpenAI API                           |
| Retrieval  | FAISS                                                |
| Embedding  | intfloat/multilingual-e5-large (오픈소스)             |
| Web Search | Serper.dev (Google Search API)                       |

## Agents

- **Supervisor Agent** : 전체 파이프라인 제어, 상태 기반 라우팅, 재작업 판단
- **Market Research Agent** : 글로벌 배터리 시장 환경 분석 (캐즘, ESS, 정책)
- **LG Analysis Agent** : LG에너지솔루션 전략·실적·기술 분석
- **CATL Analysis Agent** : CATL 전략·실적·기술 분석
- **Comparison & SWOT Agent** : 양사 4축 비교 + SWOT 도출 (내부/외부 구분)
- **Report Writer Agent** : SUMMARY + 본문 통합 + REFERENCE 생성
- **Quality Review Agent** : Criteria 검증 + 편향 감사 (PASS/REVISE)

## Architecture

```
                    ┌────────────────┐
                    │ Supervisor     │
                    │ Agent          │◀──── REVISE (최대 2회) ────┐
                    └───────┬────────┘                           │
                            │                                    │
            ┌───────────────┼───────────────┐                    │
            ▼               ▼               ▼                    │
    ┌──────────────┐ ┌─────────────┐ ┌─────────────┐            │
    │ Market       │ │ LG Analysis │ │ CATL        │            │
    │ Research     │ │ Agent       │ │ Analysis    │            │
    └──────┬───────┘ └──────┬──────┘ └──────┬──────┘            │
           └────────────────┼───────────────┘                    │
                            ▼                                    │
                  ┌───────────────────┐                          │
                  │ Comparison &      │                          │
                  │ SWOT Agent        │                          │
                  └─────────┬─────────┘                          │
                            ▼                                    │
                  ┌───────────────────┐                          │
                  │ Report Writer     │                          │
                  │ Agent             │                          │
                  └─────────┬─────────┘                          │
                            ▼                                    │
                  ┌───────────────────┐                          │
                  │ Quality Review    │──── REVISE ──────────────┘
                  │ Agent             │
                  └─────────┬─────────┘
                            │ PASS
                            ▼
                    ┌──────────────┐
                    │ Final Report │
                    │ (MD / HTML)  │
                    └──────────────┘
```

## Directory Structure

```
vsco-prototype-2/
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
│   ├── rag_tool.py               # Agentic RAG (Query Rewriting + 관련성 판단)
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
