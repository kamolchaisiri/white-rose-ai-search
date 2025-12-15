# 🌹 White Rose AI: Semantic Search Engine (PoC)

**White Rose AI** is a proof-of-concept (PoC) for an intelligent e-commerce search engine utilizing **Hybrid Search Architecture** (Keyword + Vector Search) and **RAG (Retrieval-Augmented Generation)**.

This project demonstrates how integrating Large Language Models (LLMs) can enhance search relevance, solve the "zero results" problem, and improve cross-selling opportunities in a retail environment.

---

## 🚀 Key Features

* **Hybrid Search:** Combines Traditional Keyword Search (BM25) with Semantic Vector Search (k-NN) using **OpenSearch**.
* **AI-Powered Query Expansion:** Uses **Llama 3.2** (via Ollama) to understand user intent and expand search terms (e.g., "Dinner Party" -> "Steak, Wine, Candles").
* **High Scalability:** Tested with a dataset of **20,000+ SKUs** to ensure performance stability.
* **Interactive UI:** Built with **Streamlit** for real-time visualization and analytics.

## 🛠 Tech Stack

* **Core:** Python 3.10+
* **Backend:** FastAPI
* **Frontend:** Streamlit
* **Database:** OpenSearch (Vector DB)
* **AI/LLM:** Ollama (Llama 3.2), SentenceTransformers (Paraphrase-Multilingual)
* **Containerization:** Docker & Docker Compose

## 📦 How to Run

### 1. Prerequisites
* Docker Desktop installed
* [Ollama](https://ollama.com/) installed
* Python 3.x

### 2. Setup Database (Docker)
```bash
docker-compose up -d


### 3. Start Database (OpenSearch)
```bash
docker-compose up -d

Wait for about 60 seconds for the node to initialize.

### 4. Install Dependencies
```bash
pip install -r requirements.txt