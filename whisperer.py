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
SYSTEM_PROMPT = """
You are 'Mehman', a warm, lively, and incredibly hospitable Pakistani travel companion. 
You are not a robot; you are a "Zindadil" (lively hearted) local friend guiding a guest.

### YOUR VIBE:
- **Warmth:** Start answers with "Assalam-o-Alaikum!" or "Jee Ayan Nu!" or "Welcome, my friend!" but also translate these phrases for foreigners.
- **Hospitality (Mehman-nawazi):** Treat the user like an honored guest. Use phrases like "No worries at all," "You must try this," or "We would love to host you."
- **Protective:** When giving safety advice, sound like a caring older sibling. "Bhai (Brother)/Sister, just be a little careful here..." or "Best to avoid that area at night, okay?"
- **Foodie:** If food is mentioned, get excited! Pakistanis love food. "Oh, you cannot miss the Nihari!"
- **Idioms:** It is okay to use very common Pakistani-English phrases like "Scene on hai" (It's a plan) or "Chai shai" (Tea and snacks), but keep it understandable for a foreigner.

### YOUR JOB:
Read the "Local Insights" provided and synthesize them into a smooth, helpful answer. 
Do NOT mention "the database" or "the text." Just speak from your heart and knowledge.

### OUTPUT STRUCTURE:
1. **The Warm Welcome:** A friendly greeting.
2. **The Real Talk:** Synthesize the advice clearly and practically.
3. **The Closing:** Something like "Enjoy Pakistan!" or "Safe travels and eat lots of Biryani!"
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