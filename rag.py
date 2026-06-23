import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_core.embeddings import Embeddings
from pinecone import Pinecone

load_dotenv()

EMBED_MODEL_NAME = "multilingual-e5-large"
EMBED_DIMENSION = 1024

REQUIRED_ENV_VARS = ["ANTHROPIC_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME", "APP_PASSWORD"]


def check_env():
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")


def get_pinecone_client():
    return Pinecone(api_key=os.environ["PINECONE_API_KEY"])


class PineconeInferenceEmbeddings(Embeddings):
    """Embeddings backed by Pinecone's hosted inference API, no local model needed."""

    def __init__(self, client):
        self.client = client

    def _embed(self, texts, input_type):
        result = self.client.inference.embed(
            model=EMBED_MODEL_NAME,
            inputs=texts,
            parameters={"input_type": input_type, "truncate": "END"},
        )
        return [r["values"] for r in result]

    def embed_documents(self, texts):
        embeddings = []
        batch_size = 96
        for i in range(0, len(texts), batch_size):
            embeddings.extend(self._embed(texts[i : i + batch_size], "passage"))
        return embeddings

    def embed_query(self, text):
        return self._embed([text], "query")[0]


def get_embeddings():
    return PineconeInferenceEmbeddings(get_pinecone_client())


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
