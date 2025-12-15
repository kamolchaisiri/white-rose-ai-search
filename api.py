import numpy as np
import requests
import json

# Fix Numpy 2.0
if not hasattr(np, 'float_'):
    np.float_ = np.float64

from fastapi import FastAPI
from pydantic import BaseModel
from opensearchpy import OpenSearch
from sentence_transformers import SentenceTransformer

app = FastAPI(title="White Rose's AI Search")

# --- จุดสำคัญ: แก้ Config ให้เหมือนตอน Import CSV ---
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,          # <--- ปิด SSL
    verify_certs=False,
    timeout=30
)

# เลือกโมเดลให้ตรงกับที่ใช้ Import ข้อมูล (แนะนำตัวเก่งภาษาไทย)
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
INDEX_NAME = "ecommerce_products"

# ฟังก์ชันคุยกับ Ollama
def ask_ollama(user_query):
    print(f"🤖 AI Thinking: {user_query}")
    try:
        url = "http://localhost:11434/api/generate"
        prompt = f"""Task: Extract product keywords for supermarket search.
        Query: "{user_query}"
        Output: Just list 3-5 keywords in Thai separated by space. No explanation."""
        
        payload = {"model": "llama3.2", "prompt": prompt, "stream": False}
        res = requests.post(url, json=payload, timeout=5) # timeout 5 วิ กันรอนาน
        return res.json()['response'].strip()
    except:
        return user_query # ถ้า Ollama ช้าหรือไม่เปิด ให้ใช้คำเดิม

@app.get("/search")
def search_products(q: str):
    # 1. ขยายความด้วย AI
    expanded = ask_ollama(q)
    final_query = f"{q} {expanded}"
    print(f"🔎 Final Search: {final_query}")

    # 2. แปลง Vector
    query_vector = model.encode(final_query).tolist()

    # 3. ค้นหาใน OpenSearch
    query_body = {
        "size": 10,
        "query": {
            "knn": {
                "vector_embedding": {
                    "vector": query_vector,
                    "k": 10
                }
            }
        }
    }
    
    try:
        response = client.search(index=INDEX_NAME, body=query_body)
        results = []
        for hit in response['hits']['hits']:
            # กรอง Score ต่ำๆ ทิ้ง
            if hit['_score'] < 0.4: continue 
            
            src = hit['_source']
            results.append({
                "title": src.get('title'),
                "price": src.get('price'),
                "category": src.get('category'),
                "description": src.get('description'),
                "score": hit['_score']
            })
        return {"data": results, "ai_thought": expanded}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"data": [], "error": str(e)}

# (ส่วน Setup/Add Product ละไว้ได้ เพราะเรา Import ผ่าน CSV แล้ว)
@app.post("/setup") # ใส่ไว้เผื่อกด Reset จากหน้าเว็บ
def setup_placeholder():
    return {"msg": "Please use import_csv.py for bulk data"}