import csv
import time
import numpy as np
from tqdm import tqdm # หลอดโหลด

# Fix Numpy
if not hasattr(np, 'float_'): np.float_ = np.float64

from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer

# Config
INDEX_NAME = "ecommerce_products"
BATCH_SIZE = 500  # ยิงเข้า DB ทีละ 500 รายการ (กำลังดี)
CSV_FILE = "products_big.csv"

# Connect
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True, use_ssl=False, verify_certs=False, timeout=60
)

# Model (โหลดครั้งเดียว)
print("⏳ Loading AI Model (may take a moment)...")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2') 

def setup_index():
    print(f"🗑️  Resetting Index: {INDEX_NAME}")
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)

    index_body = {
        "settings": {"index": {"knn": True}},
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "description": {"type": "text"},
                "vector_embedding": {
                    "type": "knn_vector",
                    "dimension": 768,
                    "method": {"name": "hnsw", "space_type": "cosinesimil", "engine": "nmslib"}
                }
            }
        }
    }
    client.indices.create(index=INDEX_NAME, body=index_body)
    print("✅ Index Re-created!")

def import_big_data():
    if not client.ping():
        print("❌ Cannot connect to OpenSearch!")
        return

    setup_index()

    # นับจำนวนบรรทัดทั้งหมดก่อน เพื่อทำหลอดโหลด
    print("📊 Counting rows...")
    with open(CSV_FILE, encoding='utf-8') as f:
        total_rows = sum(1 for line in f) - 1
    
    print(f"🚀 Starting Import: {total_rows:,} items")
    print("☕ Go grab a coffee, this will take a while...")

    actions = []
    
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # ใช้ tqdm ครอบ reader เพื่อโชว์ Progress Bar
        for row in tqdm(reader, total=total_rows, unit="item"):
            text = f"{row['title']} {row['description']} {row['category']}"
            vector = model.encode(text).tolist()
            
            doc = {
                "_index": INDEX_NAME,
                "_id": row['id'],
                "_source": {
                    "title": row['title'],
                    "description": row['description'],
                    "category": row['category'],
                    "price": float(row['price']),
                    "vector_embedding": vector
                }
            }
            actions.append(doc)
            
            # ถ้ารวบรวมครบ Batch Size (500) ให้ยิงเข้า DB เลย
            if len(actions) >= BATCH_SIZE:
                helpers.bulk(client, actions)
                actions = [] # เคลียร์แรม

        # เก็บตกเศษที่เหลือ
        if actions:
            helpers.bulk(client, actions)

    print("\n🎉 MISSION COMPLETE! 20,000 items imported.")

if __name__ == "__main__":
    import_big_data()