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
GENERATION_MODEL = 'gemini-2.5-flash-lite' # Fast and cheap for chat

# --- SYSTEM PERSONA (The "Soul" of Mehman) ---
SYSTEM_PROMPT = """
You are 'Mehman', a sophisticated and culturally wise travel companion for Pakistan. 
You are speaking to a foreign tourist who needs clear, practical, and safe advice.

### YOUR JOB
Your task is to read the "Local Insights" provided to you (which are messy snippets from real travelers) and weave them into a **single, smooth, and coherent answer.**

### RULES FOR "SMOOTH" WRITING
1. **No Robot Talk:** NEVER say "The provided text says," "According to the database," "Context mentions," or "In the snippets."
2. **Synthesize, Don't List:** Do not give a bulleted list of "User A said this, User B said that." Blend the advice together.
   - *Bad:* "One person said wear shalwar kameez. Another said jeans are fine."
   - *Good:* "While jeans are generally acceptable in upscale areas, wearing a shalwar kameez will help you blend in and gain more respect from locals."
3. **The "Why" Matters:** Always explain the cultural reasoning. Don't just give rules; give the *feeling* of the place.
4. **Be Warm but Realistic:** Use a hospitable tone ("Welcome," "Don't worry"), but be firm on safety warnings if the data suggests caution.
5. **Unknowns:** If the Local Insights don't answer the specific question, admit it gracefully: "I don't have a specific local report on that exact location, but generally in Pakistan..."

### OUTPUT FORMAT
- Start with a direct, reassuring opening.
- Provide the synthesized advice in 1-2 smooth paragraphs.
- End with a short, warm closing (e.g., "Safe travels!" or "Enjoy the chai!").
"""
# Initialize Gemini Client
try:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error initializing Client: {e}")
    client = None

# Global variables to hold the loaded "brain"
index = None
chunks = []
metadata = []

def load_brain():
    """Loads the FAISS index and metadata from disk only once."""
    global index, chunks, metadata
    
    if index is not None:
        return # Already loaded

    print("🧠 Loading Mehman's brain...")
    
    try:
        # Load FAISS Index
        index = faiss.read_index(VECTOR_STORE_FILE)
        
        # Load Metadata (Text chunks)
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks = data['chunks']
            metadata = data['metadata']
            
        print(f"✅ Brain loaded! ({index.ntotal} memories available)")
        
    except Exception as e:
        print(f"❌ Error loading brain: {e}")
        print("Did you run rag_backend.py successfully?")

def search_brain(query, k=3):
    """Embeds the query and searches for the top k most relevant chunks."""
    if not client or index is None:
        return []

    try:
        # 1. Embed the user's question
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=query,
            config=genai.types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY" 
            )
        )
        
        # Extract vector (handling the object wrapper if necessary)
        if hasattr(response, 'embeddings'):
            # The new SDK might return a list of objects
            query_vector = np.array([e.values for e in response.embeddings])
        else:
            # Fallback
            query_vector = np.array(response.embedding)

        # 2. Search FAISS
        # D = distances, I = indices of the nearest neighbors
        D, I = index.search(query_vector, k)
        
        # 3. Retrieve the actual text for the top results
        results = []
        for idx in I[0]:
            if idx < len(chunks):
                results.append(chunks[idx])
                
        return results

    except Exception as e:
        print(f"⚠️ Search error: {e}")
        return []

def get_mehman_response(user_question):
    """The main function called by the UI."""
    # Ensure brain is loaded
    if index is None:
        load_brain()

    # 1. Retrieve relevant advice
    retrieved_chunks = search_brain(user_question)
    
    # 2. Format context for the LLM
    context_text = "\n\n".join([f"- {chunk}" for chunk in retrieved_chunks])
    
    if not context_text:
        context_text = "No specific local advice found in database."

    # 3. Construct the full prompt (New "Smooth" Structure)
    full_prompt = f"""
    USER QUESTION:
    {user_question}
    
    RAW LOCAL INSIGHTS (Background Data - Synthesize this, do not quote it directly):
    {context_text}
    """

    # 4. Generate Answer
    try:
        # Check if client is valid before calling
        if not client:
             return "⚠️ Error: Gemini Client not initialized. Please check your API Key in Streamlit Secrets."

        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7 
            )
        )
        
        # SAFETY CHECK: If the model returns None or empty text
        if not response.text:
            return "⚠️ The AI could not generate a response (Possible Safety Block or Rate Limit). Please try rephrasing."
            
        return response.text

    except Exception as e:
        return f"⚠️ I'm having trouble thinking right now. Error: {e}"

# --- TEST AREA (Run this script directly to test) ---
if __name__ == "__main__":
    # This block only runs if you type 'python whisperer.py'
    load_brain()
    
    while True:
        q = input("\nAsk Mehman (or 'q' to quit): ")
        if q.lower() == 'q':
            break
        
        print("\nThinking...")
        answer = get_mehman_response(q)
        print("\n🤖 Mehman says:\n" + "-"*40)
        print(answer)
        print("-" * 40)