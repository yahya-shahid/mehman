#This lightweight server processes context lookups natively on your machine,
# queries Groq for instantaneous answers, and streams
# tokens directly over to your React layout.
import os
import json
import numpy as np
import faiss
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Base environment setups
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="Mehman AI Backend Framework")

# Enable Cross-Origin Resource Sharing (CORS) so your React frontend can talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific port (e.g., ["http://localhost:5173"]) in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration mappings
VECTOR_STORE_FILE = 'mehman_faiss.bin'
METADATA_FILE = 'mehman_faiss.bin_metadata.json'
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:streamGenerateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """You are 'Mehman', a warm, lively, and incredibly hospitable Pakistani travel companion. 
You are a "Zindadil" (lively hearted) local friend guiding a guest.

### YOUR VIBE:
- Warmth: Start with Salam or something warm to set a friendly tone.
- Hospitality: Treat the user like an honored guest.
- Protective: Sound like a caring older sibling regarding safety.
- Foodie: Get excited about food!

### 🎨 FORMATTING RULES (CRITICAL FOR UI):
Structure your answers clearly into short sections using Markdown:
1. Headings: Use bold text (e.g., "**🍛 The Food**" or "**⚠️ Safety Tips**") to separate topics.
2. Bullet Points: Use bullet points for any lists of locations, instructions, or recommendations.
3. Short Paragraphs: Keep responses punchy. Break text blocks often."""

# Global variables for vector database structures
index = None
chunks = []

def init_vector_db():
    global index, chunks
    if os.path.exists(VECTOR_STORE_FILE) and os.path.exists(METADATA_FILE):
        index = faiss.read_index(VECTOR_STORE_FILE)
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            chunks = json.load(f)['chunks']
    else:
        print("⚠️ Warning: Vector index files not compiled yet.")

@app.on_event("startup")
def startup_event():
    init_vector_db()

class ChatRequest(BaseModel):
    message: str
    history: list = []

def query_local_embedding(text: str):
    """Generates localized query coordinates in 0.03 seconds via Ollama."""
    try:
        res = requests.post(OLLAMA_EMBED_URL, json={"model": "nomic-embed-text", "prompt": text}, timeout=3)
        if res.status_code == 200:
            return res.json()["embedding"]
    except Exception:
        return None

def fetch_rag_context(query: str, k: int = 3) -> str:
    """Performs a local semantic search inside the vector base."""
    if index is None:
        return ""
    vector = query_local_embedding(query)
    if not vector:
        return ""
    
    query_vector = np.array([vector]).astype('float32')
    _, I = index.search(query_vector, k)
    
    matched_chunks = [chunks[idx] for idx in I[0] if idx < len(chunks)]
    return "\n\n".join([f"- {c}" for c in matched_chunks])

def stream_groq_response(payload: dict):
    """Streams data from Groq with a transparent failover to Gemini."""
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    try:
        # Step 1: Attempt Cloud Execution through Groq
        response = requests.post(GROQ_URL, json=payload, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith("data: ") and "[DONE]" not in decoded:
                        data = json.loads(decoded[6:])
                        token = data["choices"][0]["delta"].get("content", "")
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
            return
    except Exception as e:
        print(f"⚠️ Primary Groq gateway failed: {e}. Initiating Gemini fall-back routine...")

    # Step 2: Fallback Logic targeting Gemini API if Groq encounters exceptions
    try:
        gemini_payload = {"contents": [{"parts": [{"text": payload["messages"][-1]["content"]}]}]}
        res = requests.post(GEMINI_URL, json=gemini_payload, stream=True, timeout=10)
        if res.status_code == 200:
            for line in res.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    token = chunk["candidates"][0]["content"]["parts"][0]["text"]
                    yield f"data: {json.dumps({'token': token})}\n\n"
    except Exception as final_err:
        yield f"data: {json.dumps({'error': 'Both API networks are currently unreachable.'})}\n\n"

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    context = fetch_rag_context(request.message)
    
    # Structure system prompt rules and raw vector advice into conversational history
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context data:\n{context}\n\nQuestion: {request.message}"}
    ]
    
    groq_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "stream": True
    }
    
    return StreamingResponse(stream_groq_response(groq_payload), media_type="text/event-stream")

class TranslateRequest(BaseModel):
    text: str

@app.post("/api/translate")
async def translate_endpoint(request: TranslateRequest):
    """Translates travel text into polite Urdu and automatically appends a street tip."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty.")
        
    prompt = (
        f"Translate this English travel sentence into highly polite and respectful Urdu using 'Aap'. "
        f"In addition, formulate a short, practical cultural tip ('tip') for a tourist saying this in Pakistan. "
        f"Output strictly as a JSON object with exactly three keys: 'urdu', 'roman', and 'tip'.\n\n"
        f"Sentence: \"{request.text}\""
    )
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "response_format": {"type": "json_object"}
    }
    
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result_json = response.json()["choices"][0]["message"]["content"]
            return json.loads(result_json)
    except Exception as e:
        print(f"⚠️ Translation service failure: {e}")
        
    return {
        "urdu": "معاف کیجیے، سرور مصروف ہے",
        "roman": "Maaf kijiye, server masroof hai.",
        "tip": "Connection interrupted. Try typing your sentence once again."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)