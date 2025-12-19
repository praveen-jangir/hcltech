import os
import torch
import faiss
import numpy as np
from flask import Flask, request, jsonify
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pyngrok import ngrok

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL = "microsoft/deberta-v3-large"
CHUNK_SIZE = 300
TOP_K = 5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

embedder = SentenceTransformer(EMBEDDING_MODEL)

tokenizer = AutoTokenizer.from_pretrained(RERANK_MODEL)
reranker = AutoModelForSequenceClassification.from_pretrained(
    RERANK_MODEL,
    num_labels=2
).to(DEVICE)


documents = []
faiss_index = None


def chunk_text(text, size=CHUNK_SIZE):
    words = text.split()
    return [
        " ".join(words[i:i + size])
        for i in range(0, len(words), size)
    ]

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + " "
    return text

def build_faiss(chunks):
    embeddings = embedder.encode(chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index, embeddings

def rerank(query, contexts):
    pairs = [(query, c) for c in contexts]
    inputs = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        scores = reranker(**inputs).logits[:, 1]

    best_idx = torch.argmax(scores).item()
    return contexts[best_idx]


app = Flask(__name__)

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    global documents, faiss_index

    file = request.files["file"]
    path = f"./{file.filename}"
    file.save(path)

    text = read_pdf(path)
    chunks = chunk_text(text)
    faiss_index, _ = build_faiss(chunks)
    documents = chunks

    return jsonify({
        "status": "PDF uploaded",
        "chunks_created": len(chunks)
    })

@app.route("/ask", methods=["POST"])
def ask_question():
    if faiss_index is None:
        return jsonify({"error": "Upload PDF first"}), 400

    query = request.json["question"]

    query_emb = embedder.encode([query])
    distances, indices = faiss_index.search(
        np.array(query_emb), TOP_K
    )

    retrieved_chunks = [documents[i] for i in indices[0]]
    best_context = rerank(query, retrieved_chunks)

    return jsonify({
        "question": query,
        "answer_context": best_context
    })

if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print("Public URL:", public_url)
    app.run(port=5000)

