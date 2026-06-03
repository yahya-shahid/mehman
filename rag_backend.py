import os
import json
import numpy as np
import faiss
import requests

# --- CONFIGURATION ---
DATA_FILE = 'mehman_data.json'
VECTOR_STORE_FILE = 'mehman_faiss.bin'
METADATA_FILE = 'mehman_faiss.bin_metadata.json'

# Local Ollama Configurations
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text"  # Generates 768 dimensions locally

def load_and_chunk_data(data_path):
    if not os.path.exists(data_path):
        print(f"❌ Error: {data_path} not found.")
        return [], []
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_chunks = []
    metadata_list = []

    for entry in data:
        source_info = {
            "title": entry.get('title', 'No Title'),
            "url": entry.get('url', 'N/A')
        }
        for answer in entry.get('answers', []):
            if len(answer.strip()) > 50:
                all_chunks.append(answer)
                metadata_list.append(source_info)
                
    print(f"✅ Prepared {len(all_chunks)} chunks from local source database.")
    return all_chunks, metadata_list

def get_local_embedding(text):
    """Fetches text vector directly from local Ollama instance."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": EMBEDDING_MODEL, "prompt": text}
        )
        if response.status_code == 200:
            return response.json()["embedding"]
        else:
            print(f"⚠️ Ollama error code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection to Ollama failed: {e}")
        return None

def create_and_save_vector_store(chunks, metadata_list):
    if not chunks:
        return

    print(f"🚀 Embedding {len(chunks)} chunks locally using {EMBEDDING_MODEL}...")
    all_embeddings = []

    for i, chunk in enumerate(chunks):
        vector = get_local_embedding(chunk)
        if vector:
            all_embeddings.append(vector)
        if i % 50 == 0 and i > 0:
            print(f"   Processed {i}/{len(chunks)} vectors...")

    if not all_embeddings:
        print("❌ Ingestion aborted. No embeddings compiled.")
        return

    embeddings = np.array(all_embeddings).astype('float32')
    dimension = embeddings.shape[1]
    
    # Initialize FAISS Flat Index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Serialize files to working path
    faiss.write_index(index, VECTOR_STORE_FILE)
    
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"chunks": chunks, "metadata": metadata_list}, f, indent=4, ensure_ascii=False)

    print(f"✅ SUCCESS! Generated native database. Index contains {index.ntotal} vectors.")

if __name__ == "__main__":
    text_chunks, metadata = load_and_chunk_data(DATA_FILE)
    if text_chunks:
        create_and_save_vector_store(text_chunks, metadata)