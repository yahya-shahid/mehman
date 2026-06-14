# 🕌 Mehman: A Culturally-Aware RAG Framework for Hyper-Local Tourism

Mehman (*Urdu for Guest*) is a decoupled full-stack Retrieval-Augmented Generation (RAG) assistant engineered to deliver high-fidelity, culturally calibrated travel, security, and context-specific guidance for international visitors navigating Pakistan.

---

## 🗺️ Architectural Evolution & Engineering Journey

The system underwent a rigorous iterative progression to achieve its current production-grade performance thresholds:

### Epoch 1: Monolithic Streamlit Prototyping (Local CPU CPU Constraints)
The initial architectural exploration was constructed entirely as a single-file Streamlit application (`app.py`), relying on a local open-source Small Language Model (`Llama 3.2 3B`) orchestrating vector transformations row-by-row on an older mobile Intel i7 dual-core processor. 
* **The Bottleneck:** Local token generation latency exceeded 30–60 seconds per response, and sequential collection arrays created severe system memory locks. Sequential data ingestion on raw local strings required over 12 hours of compute allocation.

### Epoch 2: The Full-Stack Transition (Decoupled Decoupled Paradigm)
To achieve acceptable interactive communication metrics, the Streamlit presentation engine was completely deprecated and replaced with a production-grade decoupled model:
1. **Frontend Presentation:** A single-page application built using React 18, TypeScript, Vite, and Tailwind CSS.
2. **Business Domain Service:** A high-performance, asynchronous Python API backend built on FastAPI.

### Epoch 3: Hybrid Cloud Optimization (Sub-Second Latency Metrics)
To resolve mobile hardware compute restrictions while satisfying data ownership constraints, a hybrid pipeline was established:
* **Localized Context Sifting:** Vector lookups are handled natively on system memory in milliseconds using a local flat L2 space FAISS index (`mehman_faiss.bin`) mapped through Ollama’s localized `nomic-embed-text` framework.
* **Cloud-Accelerated Synthesis:** Matching document blocks are securely packaged and passed to Groq’s high-speed inference array utilizing `Llama 3.3 70B parameters`. This optimization reduced user communication latency from 60 seconds down to a sub-second token stream, automatically fortified via an alternative cloud failover routing loop directed to Google Gemini nodes.

---

## 🏗️ Technical Stack Details

### Core Application Backbones
* **UI Client:** React 18.3.1, TypeScript, Vite 6.3.5, React Router 7.13.0
* **Style Engine:** Tailwind CSS, Radix UI Primitives, Material UI Icons, Framer Motion
* **API Inferences Backend:** FastAPI, Uvicorn Server, Python-Dotenv, Native HTTP Requests
* **Vector Index:** FAISS (Facebook AI Similarity Search) CPU FlatL2 Bound

### Third-Party Microservices
* **Localized Vector Embeddings:** Ollama Engine (`nomic-embed-text`)
* **Primary LLM Processor:** Groq Cloud LPU (`llama-3.3-70b-versatile`)
* **Secondary Failover Layer:** Google Gemini Cloud Network (`gemini-2.5-flash-lite`)

---

## 🚀 Execution & Setup Protocol

### Backend Workspace Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
