import os
import json
import numpy as np
import faiss
import requests

# --- CONFIGURATION ---
VECTOR_STORE_FILE = 'mehman_faiss.bin'
METADATA_FILE = 'mehman_faiss.bin_metadata.json'

OLLAMA_GEN_URL = "http://localhost:11434/api/generate"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "llama3.2"
EMBED_MODEL_NAME = "nomic-embed-text"

SYSTEM_PROMPT = """
You are 'Mehman', a warm, lively, and incredibly hospitable Pakistani travel companion. 
You are a "Zindadil" (lively hearted) local friend guiding a guest.

### YOUR VIBE:
- Warmth: Start with "Assalam-o-Alaikum!"
- Hospitality: Treat the user like an honored guest.
- Protective: Sound like a caring older sibling regarding safety.
- Foodie: Get excited about food!

### 🎨 FORMATTING RULES (CRITICAL FOR UI):
Structure your answers clearly into short sections using Markdown:
1. Headings: Use bold text (e.g., "**🍛 The Food**" or "**⚠️ Safety Tips**") to separate topics.
2. Bullet Points: Use bullet points for any lists of locations, instructions, or recommendations.
3. Short Paragraphs: Keep responses punchy. Break text blocks often.
"""

index = None
chunks = []
metadata = []

def load_brain():
    global index, chunks, metadata
    if index is not None: return
    try:
        index = faiss.read_index(VECTOR_STORE_FILE)
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks = data['chunks']
            metadata = data['metadata']
    except Exception as e:
        print(f"❌ Error loading local vector index: {e}")

def needs_context(query):
    triggers = ["it", "that", "there", "this", "he", "she", "they", "them", "those", "do", "does"]
    query_words = query.lower().split()
    return len(query_words) < 5 or any(word in triggers for word in query_words)

def query_local_llm(prompt, system_instruction="", json_mode=False):
    """Helper method to run a standard POST generation to Ollama."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_instruction,
        "stream": False
    }
    if json_mode:
        payload["format"] = "json"
        
    try:
        response = requests.post(OLLAMA_GEN_URL, json=payload)
        if response.status_code == 200:
            return response.json()["response"]
    except Exception as e:
        print(f"⚠️ Local inference query error: {e}")
    return ""

def rewrite_query(user_question, chat_history):
    if not chat_history: return user_question
    recent_history = chat_history[-3:]
    history_str = "\n".join(recent_history)
    
    prompt = f"Context history:\n{history_str}\n\nFollow-up: {user_question}\n\nRewrite this follow-up question as a single standalone search query containing the necessary context (like names or cities). Output ONLY the final standalone query string."
    rewritten = query_local_llm(prompt)
    return rewritten.strip() if rewritten else user_question

def search_brain(query, k=4):
    if index is None: load_brain()
    try:
        res = requests.post(OLLAMA_EMBED_URL, json={"model": EMBED_MODEL_NAME, "prompt": query})
        if res.status_code != 200: return []
        
        query_vector = np.array([res.json()["embedding"]]).astype('float32')
        D, I = index.search(query_vector, k)
        
        results = []
        for idx in I[0]:
            if idx < len(chunks):
                results.append(chunks[idx])
        return results
    except Exception:
        return []

def get_mehman_response(user_question, chat_history_context=[]):
    if index is None: load_brain()
    
    search_query = user_question
    if chat_history_context and needs_context(user_question):
        search_query = rewrite_query(user_question, chat_history_context)
        
    retrieved_chunks = search_brain(search_query)
    context_text = "\n\n".join([f"- {chunk}" for chunk in retrieved_chunks])
    
    history_text = "\n".join(chat_history_context[-3:])
    
    full_prompt = f"CHAT HISTORY:\n{history_text}\n\nUSER QUESTION:\n{user_question}\n\nRAW LOCAL COMMUNITY INSIGHTS:\n{context_text}"
    
    return query_local_llm(full_prompt, system_instruction=SYSTEM_PROMPT)

def get_mehman_translation(english_text):
    prompt = f"Translate this text into highly polite and respectful Urdu using 'Aap'. Output strictly as a JSON object with two keys: 'urdu_script' and 'roman_urdu'.\n\nText: \"{english_text}\""
    response_text = query_local_llm(prompt, json_mode=True)
    try:
        return json.loads(response_text)
    except Exception:
        return {"urdu_script": "ترجمہ دستیاب نہیں ہے", "roman_urdu": "Tarjuma dastyab nahi hai."}