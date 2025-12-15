import time
import numpy as np  # <--- เพิ่มบรรทัดนี้

# --- เพิ่มท่อนนี้เพื่อแก้บั๊ก Numpy 2.0 ---
if not hasattr(np, 'float_'):
    np.float_ = np.float64
# ---------------------------------------

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

# 1. เชื่อมต่อ Elasticsearch (Localhost)
es = Elasticsearch("http://localhost:9200")

# 2. โหลด AI Model (ใช้รุ่นเล็ก โหลดไว แม่นใช้ได้)
print("⏳ Loading AI Model... (ครั้งแรกอาจนานหน่อย)")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model Loaded!")

INDEX_NAME = "ecommerce_products"

def create_index():
    print(f"🗑️  Cleaning up index {INDEX_NAME}...")
    
    # แก้: ลบคำสั่ง if exists ทิ้ง แล้วใช้บรรทัดนี้แทน
    # แปลว่า: "ช่วยลบ Index นี้ให้หน่อย ถ้าหาไม่เจอก็ช่างมัน (ignore_unavailable=True)"
    es.indices.delete(index=INDEX_NAME, ignore_unavailable=True)

    # กำหนด Schema
    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "description": {"type": "text"},
                "vector_embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine"
                }
            }
        }
    }
    
    # สร้าง Index ใหม่
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✅ Created index: {INDEX_NAME}")

def add_products():
    # ข้อมูลตัวอย่าง (สังเกตว่าผมใส่ภาษาไทยและอังกฤษปนกัน)
    products = [
        {"id": "1", "title": "Nike Air Max 97", "desc": "รองเท้าวิ่งผู้ชาย สีขาว ดีไซน์ทันสมัย ใส่สบาย", "cat": "Shoes", "price": 5400},
        {"id": "2", "title": "iPhone 15 Pro", "desc": "สมาร์ทโฟน Apple ชิป A17 Pro กล้องชัด ไทเทเนียม", "cat": "Electronics", "price": 42000},
        {"id": "3", "title": "Logitech MX Master 3S", "desc": "เมาส์ไร้สาย เพื่อสุขภาพ Ergonomic mouse for work", "cat": "Accessories", "price": 3900},
        {"id": "4", "title": "เสื้อยืด Uniqlo Cotton", "desc": "เสื้อยืดคอกลม ผ้าฝ้าย 100% ใส่สบาย ระบายอากาศดี", "cat": "Clothing", "price": 390},
        {"id": "5", "title": "Dyson V12 Detect Slim", "desc": "เครื่องดูดฝุ่นไร้สาย พลังแรงสูง ดูดไรฝุ่นได้", "cat": "Home", "price": 25900},
    ]

    print("🚀 Indexing products...")
    for p in products:
        # รวม text เพื่อทำ Embedding (Title + Description + Category)
        text_to_embed = f"{p['title']} {p['desc']} {p['cat']}"
        vector = model.encode(text_to_embed)

        doc = {
            "title": p['title'],
            "description": p['desc'],
            "category": p['cat'],
            "price": p['price'],
            "vector_embedding": vector
        }
        es.index(index=INDEX_NAME, id=p['id'], document=doc)
    
    # Refresh ให้ข้อมูลพร้อมค้นหาทันที
    es.indices.refresh(index=INDEX_NAME)
    print(f"✅ Indexed {len(products)} products.")

def search(query_text):
    print(f"\n🔍 Searching for: '{query_text}'")
    
    # 1. แปลงคำค้นหาเป็น Vector
    query_vector = model.encode(query_text)

    # 2. ค้นหาแบบ Hybrid (Vector + Keyword)
    # แต่ใน Demo นี้เน้น Vector (kNN) ให้เห็นภาพชัดๆ
    response = es.search(
        index=INDEX_NAME,
        knn={
            "field": "vector_embedding",
            "query_vector": query_vector,
            "k": 3, # เอามาแค่ 3 อันดับแรก
            "num_candidates": 100
        }
    )

    # 3. แสดงผล
    print("--- Results ---")
    for hit in response['hits']['hits']:
        score = hit['_score']
        source = hit['_source']
        print(f"[{score:.4f}] {source['title']} ({source['price']} THB)")
        print(f"   -> {source['description']}")

# --- Main Execution ---
if __name__ == "__main__":
    create_index()
    add_products()

    # ลองทดสอบค้นหา
    # Case 1: ค้นหาด้วยความหมาย (ไม่ตรง keyword เป๊ะๆ)
    search("มือถือถ่ายรูปสวย") 
    # (ควรเจอ iPhone 15 แม้ไม่มีคำว่า 'มือถือ' หรือ 'ถ่ายรูป' ในชื่อตรงๆ แต่ใน desc มีบริบทใกล้เคียง)

    # Case 2: ค้นหาแบบระบุปัญหา
    search("อุปกรณ์ทำความสะอาดบ้าน")
    # (ควรเจอ Dyson)
    
    # Case 3: ค้นหาภาษาอังกฤษ
    search("mouse for coding")
    # (ควรเจอ Logitech)