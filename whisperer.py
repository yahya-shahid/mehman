import os
import json
import numpy as np
import faiss
from google import genai
from google.genai.errors import APIError

# --- CONFIGURATION ---
VECTOR_STORE_FILE = 'mehman_faiss.bin'
METADATA_FILE = 'mehman_faiss.bin_metadata.json'
EMBEDDING_MODEL = 'text-embedding-004'
GENERATION_MODEL = 'gemini-2.5-flash' # Using the stable flash model

# --- SYSTEM PERSONA ---

# --- SYSTEM PERSONA (The "Zindadil" Update) ---
# --- SYSTEM PERSONA (The "Structured Zindadil" Update) ---
SYSTEM_PROMPT = """
You are 'Mehman', a warm, lively, and incredibly hospitable Pakistani travel companion. 
You are not a robot; you are a "Zindadil" (lively hearted) local friend guiding a guest.

### YOUR VIBE:
- **Warmth:** Start with "Assalam-o-Alaikum!", "Jee Ayan Nu!", or "Welcome!"
- **Hospitality:** Treat the user like an honored guest.
- **Protective:** Sound like a caring older sibling regarding safety.
- **Foodie:** Get excited about food!

### 🎨 FORMATTING RULES (CRITICAL FOR UI):
You must structure your answer into clear, scannable "Info Chunks" using Markdown:
1.  **The Greeting:** Keep it separate and short.
2.  **Headings:** Use **Bold** or `### Headers` to separate topics (e.g., "**🍛 The Food**" or "**⚠️ Safety Tips**").
3.  **Bullet Points:** ALWAYS use bullet points for lists of places, foods, or tips. It makes reading easier.
4.  **Short Paragraphs:** Never write a paragraph longer than 3 lines. Break it up!
5.  **Emojis:** Use emojis to visually separate sections.

### EXAMPLE OUTPUT FORMAT:
Assalam-o-Alaikum! You have asked about the best city!

**🏙️ Why it's famous**
Lahore is the cultural heart of Pakistan. It is known for its history and vibe.

**🍛 Must-Try Food**
* **Nihari:** You must try Waris Nihari.
* **Lassi:** The perfect drink for summer.

**⚠️ A Little Caution**
Just be mindful of your phone in busy bazaars.

Enjoy your trip, my friend!
"""
# Initialize Client (Handles both Streamlit Secrets and Local Env)
try:
    import streamlit as st
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
except Exception:
    client = None

# Global Brain Variables
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
        print(f"❌ Error loading brain: {e}")

def needs_context(query):
    """
    Heuristic: Returns True if the query likely refers to previous context.
    """
    triggers = ["it", "that", "there", "this", "he", "she", "they", "them", "those","do","does"]
    query_words = query.lower().split()
    
    # Condition 1: Very short queries ("And food?", "Is it safe?")
    if len(query_words) < 5:
        return True
        
    # Condition 2: Contains pronouns ("Is *it* famous?")
    if any(word in triggers for word in query_words):
        return True
        
    return False

def rewrite_query(user_question, chat_history):
    """
    Uses the LLM to rewrite the query. This is the 'Costly' but 'Smart' step.
    """
    if not chat_history: return user_question
    
    # We only need the last few turns
    recent_history = chat_history[-3:]
    history_str = "\n".join(recent_history)
    
    prompt = f"""
    The user is asking a follow-up question. Rewrite it to be a standalone search query that includes the necessary context (like the city name).
    
    Chat History:
    {history_str}
    
    Follow-up Question: {user_question}
    
    Standalone Search Query (Output ONLY the query):
    """
    
    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt
        )
        rewritten = response.text.strip()
        print(f"🔄 Rewrote: '{user_question}' -> '{rewritten}'")
        return rewritten
    except Exception:
        return user_question

def search_brain(query, k=4):
    """Embeds the query and searches for the top k most relevant chunks."""
    if not client or index is None: return []

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query,
            config=genai.types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        )
        
        if hasattr(response, 'embeddings'):
             query_vector = np.array([e.values for e in response.embeddings])
        else:
             query_vector = np.array(response.embedding)

        D, I = index.search(query_vector, k)
        
        results = []
        for idx in I[0]:
            if idx < len(chunks):
                results.append(chunks[idx])
        return results

    except Exception as e:
        return [f"Search Error: {e}"]

def get_mehman_response(user_question, chat_history_context=[]):
    """
    The Main Brain Function
    """
    if index is None: load_brain()
    if not client: return "⚠️ API Key Error."

    # --- STEP 1: SMART QUERY REWRITING ---
    search_query = user_question
    
    # Check if we need to pay for a rewrite
    if chat_history_context and needs_context(user_question):
        # "Is it famous?" -> triggers Rewrite
        search_query = rewrite_query(user_question, chat_history_context)
    else:
        # "Is Lahore famous?" -> Zero Cost (Pass through)
        pass
    
    # --- STEP 2: RETRIEVE ---
    # Now we search for "Is Lahore a famous city?" (Much better results)
    retrieved_chunks = search_brain(search_query)
    
    # --- STEP 3: GENERATE ---
    context_text = "\n\n".join([f"- {chunk}" for chunk in retrieved_chunks])
    if not context_text: context_text = "No specific local advice found."

    # We still give the LLM the history so the TONE is conversational
    limited_history = chat_history_context[-3:]
    history_text = "\n".join(limited_history)

    full_prompt = f"""
    CHAT HISTORY:
    {history_text}
    
    USER QUESTION:
    {user_question}
    
    RAW LOCAL INSIGHTS (Background Data found for "{search_query}"):
    {context_text}
    """

    try:
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7 
            )
        )
        return response.text if response.text else "⚠️ Empty response from AI."

    except Exception as e:
        return f"⚠️ Error: {e}"