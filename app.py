import os
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from langchain_anthropic import ChatAnthropic

from rag import check_env, get_vectorstore

load_dotenv()
check_env()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

SYSTEM_PROMPT = (
    "You are an assistant that answers questions using ONLY the provided context "
    "from the user's documents. If the context does not contain the answer, say "
    "you don't have that information in the documents. Do not use outside or "
    "general knowledge, and do not make anything up."
)

llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0, api_key=os.environ["ANTHROPIC_API_KEY"])
vectorstore = get_vectorstore()


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == os.environ["APP_PASSWORD"]:
            session["authenticated"] = True
            return redirect(url_for("index"))
        error = "Incorrect password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("authenticated", None)
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    if not question:
        return {"error": "Question is required."}, 400

    results = vectorstore.similarity_search(question, k=4)
    context = "\n\n---\n\n".join(doc.page_content for doc in results)

    if not context.strip():
        return {"answer": "I don't have that information in the documents."}

    user_message = f"Context from documents:\n\n{context}\n\nQuestion: {question}"
    response = llm.invoke([
        ("system", SYSTEM_PROMPT),
        ("human", user_message),
    ])

    return {"answer": response.content}


if __name__ == "__main__":
    app.run(debug=True, port=5050)
