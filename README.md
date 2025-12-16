# 🌹 White Rose AI: Intelligent Semantic Search Engine (PoC)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-1.22%2B-FF4B4B)
![OpenSearch](https://img.shields.io/badge/OpenSearch-2.11-005EB8)
![Status](https://img.shields.io/badge/Status-Proof%20of%20Concept-orange)

**White Rose AI** is a high-fidelity Proof of Concept (PoC) designed to demonstrate the capabilities of **Hybrid Search Architecture** (Keyword + Vector Search) in a large-scale retail environment.

This project addresses common e-commerce pain points—such as "zero search results" for natural language queries—by integrating **Retrieval-Augmented Generation (RAG)** using Local LLMs.

---

## 🎯 Business Objectives

1.  **Solve the "Zero Result" Problem:** Enable the search engine to understand user intent (e.g., *"ฉันอยากกินปาร์ตี้หมูกระทะ"*) rather than just matching keywords.
2.  **Enhance Cross-Selling:** Automatically suggest relevant complementary products (Bundling Strategy).
3.  **Technical Feasibility Study:** Assess the performance and scalability of vector databases with **20,000+ SKUs**.

---

## 🏗️ System Architecture

The system follows a microservices-like architecture containerized via Docker:

* **Frontend:** Built with **Streamlit** for rapid UI prototyping and real-time analytics.
* **Backend API:** Developed using **FastAPI** to handle search requests and LLM orchestration.
* **Intelligence Layer:**
    * **Query Expansion:** Uses **Llama 3.2** (via Ollama) to translate natural language into product keywords.
    * **Embedding Model:** Uses `sentence-transformers` to convert text into high-dimensional vectors.
* **Database:** **OpenSearch** configured for k-NN (k-Nearest Neighbors) vector search.

---

## 🛠️ Tech Stack

* **Language:** Python 3.11
* **Web Framework:** FastAPI
* **User Interface:** Streamlit
* **Vector Database:** OpenSearch (Dockerized)
* **AI & LLM:** Ollama (Llama 3.2), SentenceTransformers
* **Data Processing:** Pandas, NumPy, TQDM

---

## 🚀 Installation & Setup

Follow these steps to deploy the PoC on your local machine.

### 1. Prerequisites
* Docker Desktop (Running)
* [Ollama](https://ollama.com/) installed
* Python 3.8+

### 2. Clone the Repository
```bash
git clone https://github.com/kamolchaisiri/white-rose-ai-search
cd white-rose-ai-search
```

### 3. Start Database (OpenSearch)
```bash
docker-compose up -d
```
*Wait for about 60 seconds for the node to initialize.*

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Setup AI Model & Data Pipeline
Run the following commands to pull the model, generate mock data, and ingest it into the database:

```bash
# 1. Pull the Llama 3.2 model
ollama run llama3.2

# 2. Generate 20,000 mock SKUs (White Rose Dataset)
python gen_white_rose_data.py

# 3. Import data & create vector embeddings (This may take a few minutes)
python import_white_rose_data.py
```

### 6. Run the Application
You need to run two terminal sessions:

**Terminal 1: Backend API**
```bash
uvicorn api:app --reload
```

**Terminal 2: Frontend UI**
```bash
streamlit run ui.py
```

---

## 📱 Usage Examples

Once the application is running at `http://localhost:8501`:

1.  **Natural Language Search:** Try searching for *"Ingredients for spicy soup"* or *"Cleaning the bathroom"*.
2.  **AI Reasoning:** Observe how the AI expands your query in the "AI Thought Process" section.
3.  **Analytics:** View the price distribution chart for the search results.

---

## 📂 Project Structure

```text
white-rose-ai-search/
├── api.py                   # FastAPI Backend & AI Logic
├── ui.py                    # Streamlit Frontend Dashboard
├── gen_white_rose_data.py   # Synthetic Data Generator (20k Items)
├── import_white_rose_data.py     # ETL Pipeline (CSV -> Vector DB)
├── products_white_rose.csv  # Generated Dataset
├── docker-compose.yml       # OpenSearch Container Config
├── requirements.txt         # Python Dependencies
└── README.md                # Project Documentation
```

---

## 👨‍💼 About the Author

**Technical Project Manager & Agile Practitioner**

This project was built to bridge the gap between business requirements and technical execution in AI-driven products. It serves as a practical demonstration of managing technical risks, understanding architectural trade-offs, and leading digital transformation initiatives.


