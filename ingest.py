"""RAG 문서 임베딩 및 FAISS 벡터DB 구축"""
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import (
    DATA_DIR, RAG_FILES, EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, VECTORSTORE_PATH,
)


def load_documents():
    """RAG 대상 문서 5개 로드"""
    docs = []
    for fname in RAG_FILES:
        path = os.path.join(DATA_DIR, fname)
        loader = TextLoader(path, encoding="utf-8")
        loaded = loader.load()
        for doc in loaded:
            doc.metadata["source"] = fname
        docs.extend(loaded)
    print(f"[ingest] {len(docs)}개 문서 로드 완료")
    return docs


def split_documents(docs):
    """문서 청킹 (1,000자 / 오버랩 200자)"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"[ingest] {len(chunks)}개 청크 생성 완료")
    return chunks


def create_vectorstore(chunks):
    """FAISS 벡터DB 생성 및 저장"""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"[ingest] 벡터DB 저장 완료: {VECTORSTORE_PATH}")
    return vectorstore


def load_vectorstore():
    """저장된 FAISS 벡터DB 로드"""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True
    )
    print(f"[ingest] 벡터DB 로드 완료")
    return vectorstore


if __name__ == "__main__":
    docs = load_documents()
    chunks = split_documents(docs)
    create_vectorstore(chunks)
