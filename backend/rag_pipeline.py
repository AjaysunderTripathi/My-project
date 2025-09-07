import os
import pickle
import faiss
import numpy as np
import PyPDF2
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import time

EMBED_MODEL = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
INDEX_PATH = '/tmp/faiss.index'
CHUNKS_PATH = '/tmp/pdf_chunks.pkl'

embedder = SentenceTransformer(EMBED_MODEL)
chatbot = pipeline("text2text-generation", model="facebook/blenderbot-400M-distill")

# Advanced LLM integration: Optionally use OpenAI GPT or a custom Hugging Face model
USE_ADVANCED_LLM = os.environ.get("USE_ADVANCED_LLM", "false").lower() == "true"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)

if USE_ADVANCED_LLM and OPENAI_API_KEY:
    import openai
    openai.api_key = OPENAI_API_KEY

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def chunk_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

def build_faiss_index(chunks):
    embeddings = embedder.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings).astype('float32'))
    return index, embeddings

def save_faiss_index(index):
    faiss.write_index(index, INDEX_PATH)

def load_faiss_index():
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    return None

def save_chunks(chunks):
    with open(CHUNKS_PATH, 'wb') as f:
        pickle.dump(chunks, f)

def load_chunks():
    if os.path.exists(CHUNKS_PATH):
        with open(CHUNKS_PATH, 'rb') as f:
            return pickle.load(f)
    return []

def process_pdf_and_index(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    index, _ = build_faiss_index(chunks)
    save_faiss_index(index)
    save_chunks(chunks)
    return len(chunks)

def advanced_llm_response(prompt):
    # Example for OpenAI GPT-3/4
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.7,
    )
    return response.choices[0].message['content']

def answer_with_rag(query, context):
    index = load_faiss_index()
    chunks = load_chunks()
    if index and chunks:
        query_emb = embedder.encode([query])
        D, I = index.search(np.array(query_emb).astype('float32'), k=1)
        retrieved = chunks[I[0][0]]
        prompt = f"Context: {retrieved}\nUser: {query}\nHistory: {' | '.join(context)}"
    else:
        prompt = query
        retrieved = ""
    if USE_ADVANCED_LLM and OPENAI_API_KEY:
        answer = advanced_llm_response(prompt)
        confidence = 1.0  # OpenAI does not return a confidence score
    else:
        bot_output = chatbot(prompt)[0]
        answer = bot_output['generated_text']
        confidence = bot_output.get('score', 1.0)
    return answer, confidence, retrieved

# Privacy & Compliance: Data retention controls
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))

def cleanup_old_files(directory, days=RETENTION_DAYS):
    if not os.path.exists(directory):
        os.makedirs(directory)
        return
    
    now = time.time()
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_age = now - os.path.getmtime(filepath)
            if file_age > days * 86400:
                os.remove(filepath)

# Call this function periodically (e.g., via a cron job or at app startup)
def enforce_data_retention():
    cleanup_old_files('/tmp/conversation_logs', RETENTION_DAYS)
    cleanup_old_files('/tmp/uploads', RETENTION_DAYS)
    # Add more directories as needed

# Optionally call enforce_data_retention() at module import or app startup
enforce_data_retention()
