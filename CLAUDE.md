# MyRAG

## Product

A password-protected AI about Fiyin. Users sign in, ask questions, and get answers grounded strictly in uploaded documents. No hallucination from general knowledge.

User-facing positioning: "A password-protected AI about me. Ask questions and get to know me." Do not emphasize that answers come from documents in user-facing copy.

### Requirements

- Password-protected login screen
- Chat interface with multi-turn conversation history (last 10 messages)
- Answers sourced only from ingested documents. If the context doesn't contain the answer, say so.
- Do not use outside or general knowledge. Do not make anything up.
- Ingest PDFs, text/markdown files (from `docs/` directory), and URLs (from `urls.txt`)
- Chunk documents and embed into Pinecone vector store
- Retrieve top 4 most similar chunks per question

### What this is not

- Not a general chatbot. Answers only from documents.
- Not a public app. Password required.

## Architecture

| File | Responsibility |
|---|---|
| `app.py` | Flask routes, auth, chat endpoint. Retrieves context from vector store, sends to Claude with system prompt and conversation history. |
| `rag.py` | Pinecone setup, embeddings (Pinecone hosted inference, e5-large), vector store initialization. |
| `ingest.py` | Document loading (PDF, text, markdown, URLs), chunking (1000 chars, 150 overlap), embedding and storage in Pinecone. |

### Key technical decisions

- Claude model: Sonnet 4.5 (via LangChain ChatAnthropic). Candidate for downgrade to Haiku 4.5.
- Embeddings: Pinecone hosted inference (multilingual-e5-large, 1024 dimensions). No local model needed.
- Vector store: Pinecone (serverless, AWS us-east-1, cosine similarity).
- Top 4 chunks retrieved per query via similarity search.
- Conversation history capped at last 10 messages.
- System prompt strictly prohibits using outside knowledge.
- Auth via Flask sessions with APP_PASSWORD env var.

## Design system

- Satoshi font (via Fontshare)
- Custom CSS in `static/style.css`
- Chat interface with topbar, message area, input form
- Login card on auth page

## Deployment

- Render (https://myrag-o7eu.onrender.com)
- Listed on fiyin.org as "MyRAG" with Live badge

## Coding conventions

- No God modules. Each file has one responsibility.
- No unused code.
- Always pick the cheapest Claude model that handles the task.

## Secrets (never commit)

- `.env` contains ANTHROPIC_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, APP_PASSWORD, FLASK_SECRET_KEY
- Document contents in `docs/` may be private
