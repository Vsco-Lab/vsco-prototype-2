"""Agentic RAG 검색 도구"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ingest import load_vectorstore
from config import LLM_MODEL, LLM_TEMPERATURE, TOP_K

vectorstore = None


def get_vectorstore():
    """벡터DB 싱글턴 로드"""
    global vectorstore
    if vectorstore is None:
        vectorstore = load_vectorstore()
    return vectorstore


def query_rewrite(query: str) -> str:
    """질의를 검색에 최적화된 형태로 재작성"""
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        "다음 질문을 벡터 검색에 최적화된 키워드 중심 질의로 재작성하세요.\n"
        "원래 질문: {query}\n"
        "재작성된 질의:"
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"query": query})


def check_relevance(query: str, context: str) -> bool:
    """검색 결과가 질의에 충분히 답할 수 있는지 판단"""
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(
        "다음 질문에 대해 주어진 문맥이 충분한 정보를 제공하는지 판단하세요.\n\n"
        "질문: {query}\n\n"
        "문맥:\n{context}\n\n"
        "'충분' 또는 '부족'으로만 답하세요:"
    )
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"query": query, "context": context})
    return "충분" in result


def rag_search(query: str) -> dict:
    """
    Agentic RAG 검색 실행

    Returns:
        {"context": str, "sources": list, "needs_web": bool}
    """
    # 1. Query Rewriting
    rewritten = query_rewrite(query)

    # 2. Vector Search
    vs = get_vectorstore()
    results = vs.similarity_search(rewritten, k=TOP_K)

    context = "\n\n".join([doc.page_content for doc in results])
    sources = list(set([doc.metadata.get("source", "") for doc in results]))

    # 3. Relevance Check
    is_relevant = check_relevance(query, context)

    return {
        "context": context,
        "sources": sources,
        "needs_web": not is_relevant,
        "rewritten_query": rewritten,
    }
