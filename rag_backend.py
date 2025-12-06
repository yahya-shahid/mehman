import json
import numpy as np
import faiss
from google import genai
from google.genai.errors import APIError

# --- CONFIGURATION ---
DATA_FILE = 'mehman_data.json'
VECTOR_STORE_FILE = 'mehman_faiss.bin'
EMBEDDING_MODEL = 'text-embedding-004' # The optimal embedding model for RAG

# Initialize the Gemini Client
# Ensure you have your GEMINI_API_KEY set as an environment variable, 
# or replace 'os.environ.get("GEMINI_API_KEY")' with your key string.

try:
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini Client. Make sure your API key is configured. Details: {e}")
    client = None

def load_and_chunk_data(data_path):
    """
    Loads data from the JSON file and prepares chunks of text for embedding.
    
    Placeholder: When your JSON is ready, this function will iterate over the 'answers'
    list in each entry and yield individual text chunks.
    """
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Waiting for {data_path} (from Part 2) to be created. Returning empty data.")
        return [], []
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON. Check {data_path} for formatting errors.")
        return [], []

    # In Part 2, we scraped a list of Q&A dictionaries.
    # Here, we only need the text from the 'answers' list to build the RAG.
    
    all_chunks = []
    # We will also save the original source (title and URL) for citation later
    metadata_list = []

    for entry in data:
        source_info = {
            "title": entry.get('title', 'N/A'),
            "url": entry.get('url', 'N/A')
        }
        
        for answer in entry.get('answers', []):
            # Simple chunking: each top comment is a chunk.
            # For a real project, we might split longer comments.
            if len(answer.strip()) > 50: # Only embed meaningful comments
                all_chunks.append(answer)
                metadata_list.append(source_info)
                
    print(f"✅ Loaded {len(data)} threads and prepared {len(all_chunks)} text chunks for embedding.")
    return all_chunks, metadata_list


def create_and_save_vector_store(chunks, metadata_list):
    """
    Embeds the text chunks IN BATCHES and saves them to a FAISS index on disk.
    """
    if not chunks or not client:
        print("⚠️ No data chunks found or Gemini client is not initialized. Exiting.")
        return

    print(f"🚀 Embedding {len(chunks)} chunks using {EMBEDDING_MODEL}...")

    # --- BATCHING CONFIGURATION ---
    BATCH_SIZE = 50  # Safe size (well under the 100 limit)
    all_embeddings = []

    try:
        # Loop through the chunks in batches
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            print(f"   Processing batch {i} to {i + len(batch)}...")

            response = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
                config=genai.types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT"
                )
            )

            # Extract vectors from this batch
            if hasattr(response, 'embeddings'):
                batch_embeddings = [e.values for e in response.embeddings]
                all_embeddings.extend(batch_embeddings)
            else:
                # Fallback for single embedding edge cases (rare in batches)
                print("⚠️ Unexpected batch response format. Skipping batch.")

        # Convert list of lists to numpy array
        if not all_embeddings:
            print("❌ No embeddings were generated. Exiting.")
            return

        embeddings = np.array(all_embeddings)

        # 2. Create the FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        
        # Add the vectors to the index
        index.add(embeddings)

        # 3. Save the index to disk
        faiss.write_index(index, VECTOR_STORE_FILE)
        
        # 4. Save the metadata
        with open(VECTOR_STORE_FILE + "_metadata.json", 'w', encoding='utf-8') as f:
            json.dump({
                "chunks": chunks, 
                "metadata": metadata_list
            }, f, indent=4, ensure_ascii=False)

        print(f"✅ Success! Vector store saved to {VECTOR_STORE_FILE} and metadata saved.")
        print(f"Index size: {index.ntotal} vectors.")

    except APIError as e:
        print(f"❌ Gemini API Error during embedding: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    text_chunks, metadata = load_and_chunk_data(DATA_FILE)
    if text_chunks:
        create_and_save_vector_store(text_chunks, metadata)
    else:
        print("\n⏳ Vector store creation deferred until mehman_data.json is available.")