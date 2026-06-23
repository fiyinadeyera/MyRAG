import os
import sys

from langchain_community.document_loaders import PyPDFLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag import check_env, get_vectorstore

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
URLS_FILE = os.path.join(os.path.dirname(__file__), "urls.txt")


def load_documents():
    documents = []
    for filename in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, filename)
        if filename.lower().endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif filename.lower().endswith(".txt") or filename.lower().endswith(".md"):
            loader = TextLoader(path, encoding="utf-8")
        else:
            continue
        documents.extend(loader.load())
    return documents


def load_urls():
    if not os.path.exists(URLS_FILE):
        return []

    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        return []

    documents = []
    for url in urls:
        try:
            documents.extend(WebBaseLoader(url).load())
        except Exception as e:
            print(f"Skipping {url}: {e}")
    return documents


def main():
    check_env()

    documents = load_documents() + load_urls()
    if not documents:
        print(f"No files found in {DOCS_DIR} and no URLs in {URLS_FILE}. Add content and rerun.")
        sys.exit(1)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    print(f"Loaded {len(documents)} document(s), split into {len(chunks)} chunks.")

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    print("Ingestion complete. Chunks embedded and stored in Pinecone.")


if __name__ == "__main__":
    main()
