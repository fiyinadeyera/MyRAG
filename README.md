# MyRAG

A password-protected RAG chat app. Answers questions using only the content of files placed in `/docs`, retrieved from Pinecone and answered by Claude.

## Setup

1. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in:
   - `ANTHROPIC_API_KEY`
   - `PINECONE_API_KEY`
   - `PINECONE_INDEX_NAME`
   - `APP_PASSWORD`
   - `FLASK_SECRET_KEY` (any random string)

3. Add PDF, `.txt`, or `.md` files to `/docs`. To include web pages instead, add their URLs (one per line) to `urls.txt`.

4. Run ingestion to embed and store the documents in Pinecone:
   ```
   python ingest.py
   ```
   Re-run this any time `/docs` or `urls.txt` changes.

5. Start the app:
   ```
   python app.py
   ```
   Visit `http://localhost:5000` and sign in with `APP_PASSWORD`.

## Deploying to Render

1. Push this repo to GitHub.
2. Create a new Web Service on Render, pointed at the repo.
3. Render will use `Procfile` and `requirements.txt` automatically.
4. Set the same environment variables (`ANTHROPIC_API_KEY`, `PINECONE_API_KEY`, `PINECONE_INDEX_NAME`, `APP_PASSWORD`, `FLASK_SECRET_KEY`) in the Render dashboard.
5. Run `python ingest.py` once locally (or via a Render shell) after adding documents, since `/docs` is not deployed with the app, it stores embeddings, not the raw files.

## Notes

- Embeddings use a local model (`sentence-transformers/all-MiniLM-L6-v2`), so no OpenAI key is required.
- Answers are restricted to document content via the system prompt and retrieval-only context. If nothing relevant is found, the app says so rather than guessing.
