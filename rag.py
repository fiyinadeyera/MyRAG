import os

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIMENSION = 384

REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME", "APP_PASSWORD"]


def check_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)


def get_pinecone_client():
    return Pinecone(api_key=os.environ["PINECONE_API_KEY"])


def get_or_create_index():
    pc = get_pinecone_client()
    index_name = os.environ["PINECONE_INDEX_NAME"]
    existing = [idx["name"] for idx in pc.list_indexes()]
    if index_name not in existing:
        from pinecone import ServerlessSpec

        pc.create_index(
            name=index_name,
            dimension=EMBED_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(index_name)


def get_vectorstore():
    index = get_or_create_index()
    embeddings = get_embeddings()
    return PineconeVectorStore(index, embeddings, "text")
