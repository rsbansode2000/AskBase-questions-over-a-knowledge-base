"""Flask entry point for the Company Q&A RAG Assistant."""

from __future__ import annotations

import hashlib
import os
from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from rag.chat import ChatService
from rag.vectorstore import VectorStoreService

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DIR = BASE_DIR / "chroma_db"
ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE = 25 * 1024 * 1024
DEMO_EMAIL = "user@123"
DEMO_PASSWORD = "user@123"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "change-this-demo-secret"),
    MAX_CONTENT_LENGTH=MAX_FILE_SIZE,
)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
vector_store = VectorStoreService(CHROMA_DIR, UPLOAD_DIR)
chat_service = ChatService(vector_store)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def remove_file(path: Path) -> None:
    path.unlink(missing_ok=True)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin portal.", "warning")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def index_upload(uploaded_file, force: bool = False) -> dict:
    """Handle the one-file policy and immediately create or reuse embeddings."""
    if uploaded_file is None or not uploaded_file.filename:
        raise ValueError("No PDF selected. Choose a PDF file first.")
    if not allowed_file(uploaded_file.filename):
        raise ValueError("Unsupported file type. Please upload a PDF file.")

    incoming = UPLOAD_DIR / ".incoming.pdf"
    uploaded_file.save(incoming)
    digest = calculate_file_hash(incoming)
    existing = vector_store.load_metadata()
    active_path = UPLOAD_DIR / str(existing.get("stored_name", ""))
    if not force and existing.get("hash") == digest and existing.get("embedded") and active_path.is_file():
        remove_file(incoming)
        return {**vector_store.status(), "already_embedded": True, "skipped": True}

    destination = UPLOAD_DIR / (secure_filename(uploaded_file.filename) or "company-document.pdf")
    for old_file in UPLOAD_DIR.glob("*"):
        if old_file.is_file() and old_file != incoming:
            remove_file(old_file)
    incoming.replace(destination)
    try:
        return vector_store.process_uploaded_file(destination, uploaded_file.filename, digest, force=force)
    except Exception:
        remove_file(destination)
        raise


@app.context_processor
def inject_globals():
    return {"status": vector_store.status(), "current_year": 2026}


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/query")
def query_page():
    return render_template("query.html", history=session.get("chat_history", []))


@app.post("/chat/new")
def new_chat():
    """Start a fresh conversation while keeping the knowledge base available."""
    session["chat_history"] = []
    return jsonify({"message": "New chat started."})


@app.post("/chat/delete")
def delete_chat():
    """Delete the current conversation from the user's session."""
    session.pop("chat_history", None)
    return jsonify({"message": "Chat deleted successfully."})


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("email") == DEMO_EMAIL and request.form.get("password") == DEMO_PASSWORD:
            session["admin_logged_in"] = True
            flash("Signed in successfully.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.get("/admin/dashboard")
@admin_required
def admin_dashboard():
    return render_template("dashboard.html")


@app.route("/admin/upload", methods=["GET", "POST"])
@admin_required
def admin_upload():
    if request.method == "POST":
        try:
            result = index_upload(request.files.get("file"))
            if result.get("already_embedded"):
                flash("This document has already been embedded.", "info")
            else:
                flash("File uploaded successfully.", "success")
                flash("Embeddings generated successfully. Document is ready for chatting.", "success")
        except ConnectionError:
            flash("Ollama is not running. Start Ollama and try again.", "danger")
        except (ValueError, FileNotFoundError, OSError) as exc:
            flash(str(exc), "danger")
        except Exception:
            app.logger.exception("Admin indexing failed")
            flash("Indexing failed. Check Ollama and Chroma, then try again.", "danger")
        return redirect(url_for("admin_upload"))
    return render_template("upload.html")


@app.post("/admin/rebuild")
@admin_required
def admin_rebuild():
    metadata = vector_store.load_metadata()
    path = UPLOAD_DIR / str(metadata.get("stored_name", ""))
    if not path.is_file():
        flash("Upload a PDF before rebuilding embeddings.", "warning")
        return redirect(url_for("admin_upload"))
    try:
        digest = calculate_file_hash(path)
        result = vector_store.process_uploaded_file(path, str(metadata.get("file_name", path.name)), digest, force=True)
        flash("Embeddings rebuilt successfully. Document is ready for chatting.", "success")
    except ConnectionError:
        flash("Ollama is not running. Start Ollama and try again.", "danger")
    except Exception:
        app.logger.exception("Embedding rebuild failed")
        flash("Rebuild failed. Check the PDF and Ollama, then try again.", "danger")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/delete")
@admin_required
def admin_delete():
    vector_store.delete_collection()
    session.pop("chat_history", None)
    flash("Knowledge base deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.get("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.post("/upload")
def upload():
    try:
        result = index_upload(request.files.get("file"))
    except ConnectionError:
        return jsonify({"error": "Ollama is not running. Start Ollama and try again."}), 502
    except (ValueError, FileNotFoundError, OSError) as exc:
        return jsonify({"error": str(exc)}), 422
    except Exception:
        app.logger.exception("Upload indexing failed")
        return jsonify({"error": "Indexing failed. Check Ollama and Chroma, then try again."}), 502
    return jsonify({"message": "File uploaded successfully.", **result})


@app.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Enter a question first."}), 400
    try:
        result = chat_service.answer(question)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 400
    except ConnectionError:
        return jsonify({"error": "Ollama is not running. Start Ollama and try again."}), 502
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify({"error": "Could not generate an answer. Check Ollama and try again."}), 502
    history = session.setdefault("chat_history", [])
    history.append({"question": question, "answer": result["answer"], "sources": result["sources"], "timestamp": result.get("timestamp")})
    session.modified = True
    result["history"] = history
    return jsonify(result)


@app.get("/status")
def status():
    return jsonify(vector_store.status())


@app.post("/delete-vector-store")
def delete_vector_store():
    vector_store.delete_collection()
    session.pop("chat_history", None)
    return jsonify({"message": "Knowledge base deleted successfully."})


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({"error": "That file is too large. The maximum size is 25 MB."}), 413


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST", "127.0.0.1"), port=int(os.getenv("FLASK_PORT", "5000")), debug=True)
