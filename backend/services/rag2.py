!pip install -q pdfplumber pymupdf
!pip install -q google-genai
from google import genai

client = genai.Client(api_key="AIzaSyDLqhoMwfr2VFIPH3UlouR-xF60PhG_CwQ")

import fitz
print(fitz.__doc__)
print(fitz.__file__)

import os
images_dir = "extracted_images"
os.makedirs(images_dir, exist_ok=True)


import pdfplumber

def extract_text_by_page(pdf_path):
    page_texts = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_texts[page_number] = text.strip()

    return page_texts


def needs_ocr(text, min_chars=200):

    return len(text.strip()) < min_chars

import fitz
import os
def extract_page_as_image(pdf_path, page_number, output_dir="temp_images"):
    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    page = doc[page_number]

    pix = page.get_pixmap(dpi=300)
    image_path = os.path.join(output_dir, f"page_{page_number}.png")
    pix.save(image_path)

    return [image_path]


from PIL import Image

def ocr_images(image_paths):
    ocr_text = ""

    for image_path in image_paths:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        ocr_text += text + "\n"

    return ocr_text.strip()


def process_pdf(pdf_path):
    final_text = []

    page_texts = extract_text_by_page(pdf_path)

    for page_number, text in page_texts.items():
        if needs_ocr(text):
            image_paths = extract_page_images(
                pdf_path,
                page_number,
                output_dir="temp_images"
            )
            ocr_text = ocr_images(image_paths)
            final_text.append(ocr_text)
        else:
            final_text.append(text)

    return "\n".join(final_text)


from google.colab import files

uploaded = files.upload()

print(process_pdf("grp6.pdf"))

from google.colab import files

uploaded = files.upload()

print(process_pdf("HCL_Plan.pdf"))

text = process_pdf("grp6.pdf")

print("Total characters:", len(text))
print(text[:1500])

with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(text)

import re

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

cleaned_text = clean_text(text)


def chunk_text(text, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks

chunks = chunk_text(cleaned_text)
print("Total chunks:", len(chunks))


from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

embedder = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = embedder.encode(chunks)
embeddings = np.array(embeddings).astype("float32")

faiss.normalize_L2(embeddings)

dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

print("FAISS vectors:", index.ntotal)


def retrieve_top_k(query, k=3, similarity_threshold=0.3):
    q_emb = embedder.encode([query]).astype("float32")
    faiss.normalize_L2(q_emb)

    scores, indices = index.search(q_emb, k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score >= similarity_threshold:
            results.append(chunks[idx])

    return results


def keyword_fallback(query, chunks):
    query_lower = query.lower()
    hits = []

    for chunk in chunks:
        if any(word in chunk.lower() for word in query_lower.split()):
            hits.append(chunk)

    return hits


retrieve_top_k("human rights", k=2)

def generate_answer(question, context_chunks):
    if len(context_chunks) == 0:
        return "Information not available in the provided document."

    context = "\n".join(context_chunks)

    prompt = f"""
Answer only using the provided context.
If the answer is not found, say:
‘Information not available in the provided document."

Context:
{context}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3-pro-preview",  # or gemini-3.0-flash
        contents=prompt
    )

    return response.text


def rag_pipeline(question, k=3):
    context = retrieve_top_k(question, k)

    if len(context) == 0:
        context = keyword_fallback(question, chunks)

    if len(context) == 0:
        full_text = " ".join(chunks).lower()

        if "phone number" in question.lower() or "mobile number" in question.lower():
            if contains_phone_number(full_text):
                return "Yes, the document contains phone numbers."

    if len(context) == 0:
        return "Information not available in the provided document."

    return generate_answer(question, context)


rag_pipeline("What is the group name?")



