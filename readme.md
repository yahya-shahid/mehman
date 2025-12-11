# 🕌 Mehman: The Cultural Whisperer (AI Travel Guide)

> *Your AI companion for navigating the streets, culture, and hospitality of Pakistan.*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![RAG](https://img.shields.io/badge/Architecture-RAG-green)

##  Overview

**Mehman** (Urdu for *Guest*) is a specialized RAG (Retrieval-Augmented Generation) chatbot designed to help tourists in Pakistan. unlike generic AI, Mehman doesn't just guess—it retrieves **real "street advice"** from thousands of local conversations (Reddit threads) to provide authentic, safety-conscious, and culturally nuanced answers.

It features a unique **Persona**, treating users with the warmth of a Local host while keeping them safe like a caring local friend.

---

##  Key Features

* **🧠 Local RAG Brain:** Powered by a vector database (`FAISS`) containing 19,000+ chunks of real advice from r/pakistan and travel forums.
* **🗣️ Context-Aware Conversation:** Remembers chat history (e.g., "Is **it** safe?" understands "it" refers to the previous city).
* **🎭 Persona:** Speaks with local flair, hospitality, and protective instincts—not like a robot.
* **⚡ Zero-Cost Architecture:** Uses an optimized "Sliding Window" context system to maintain memory without doubling API costs.
* **🚜 Automated Data Pipeline:** Includes a `Harvester` and `Smart Scraper` to automatically discover and fetch thousands of relevant discussions.

---

##  Technical Architecture

Mehman uses a custom-built data pipeline that bypasses expensive APIs in favor of clever engineering.

1.  **Discovery:** `harvester.py` scans Reddit for keywords (Safety, Food, Transport) and saves links.
2.  **Extraction:** `smart_scraper.py` uses a "JSON Endpoint" technique to scrape data incrementally (only fetching new links).
3.  **Vectorization:** `rag_backend.py` chunks the text and creates embeddings using **Google Gemini (`text-embedding-004`)**.
4.  **Retrieval:** **FAISS** (Facebook AI Similarity Search) performs semantic search to find relevant advice.
5.  **Synthesis:** The **Gemini Flash** model synthesizes the retrieved context into a warm, structured answer.

---

##  Installation & Setup

### Prerequisites
* Python 3.8+
* A [Google Gemini API Key](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/mehman.git](https://github.com/yourusername/mehman.git)
cd mehman

2. Install Dependencies
pip install -r requirements.txt

3. Set up API Keys
Mehman uses Streamlit's secret management.
-Create a folder .streamlit in the root directory.
-Create a file .streamlit/secrets.toml.
-Add your key:
GEMINI_API_KEY = "AIzaSy..."

Usage Guide: The Data Pipeline
Mehman is not static. You can make it smarter by running the pipeline.

Step 1: Harvest New Links
Finds new discussions on Reddit based on your keywords.
python harvester.py

Step 2: Scrape Data (Incremental)
Downloads only the new threads found by the harvester.
python smart_scraper.py

Step 3: Rebuild the Brain
Updates the vector database with the new knowledge.
python rag_backend.py

Step 4: Run the App
Launch the chat interface.
streamlit run app.py

📂 Project Structure

📦 mehman
 ┣ 📜 app.py                # The Streamlit Frontend (UI)
 ┣ 📜 whisperer.py          # The Core Logic (RAG, Context, Persona)
 ┣ 📜 rag_backend.py        # Vector Database builder (Embeddings)
 ┣ 📜 smart_scraper.py      # Incremental Data Scraper
 ┣ 📜 harvester.py          # Link Discovery Tool
 ┣ 📜 links.txt             # Source URLs
 ┣ 📜 mehman_data.json      # Raw Text Dataset
 ┣ 📜 mehman_faiss.bin      # The "Brain" (Vector Index)
 ┗ 📜 requirements.txt      # Python Dependencies



 Future Roadmap
[ ] Translator Tab: Add English-to-Urdu script translation for tourists to show locals.
[ ] Citations: Make the bot provide clickable links to the Reddit threads used.
[ ] Voice Mode: Allow users to speak to Mehman directly.

