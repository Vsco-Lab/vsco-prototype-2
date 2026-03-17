"""환경 변수 및 프로젝트 설정"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# LLM
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.2

# Embedding
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
EMBEDDING_DIMENSION = 1024

# RAG
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5

# Vectorstore
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "vectorstore")

# Data
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RAG_FILES = [
    "01_글로벌_배터리_시장_환경.md",
    "02_LG에너지솔루션_전략_분석.md",
    "03_CATL_전략_분석.md",
    "04_양사_비교_데이터.md",
    "05_리스크_외부_환경.md",
]

# Output
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# Quality Review
MAX_REVISION_COUNT = 2
BIAS_BALANCE_MIN = 0.3
BIAS_BALANCE_MAX = 0.7
