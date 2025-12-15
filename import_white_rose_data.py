import csv
import sys
import numpy as np
from tqdm import tqdm

# Fix Numpy
if not hasattr(np, 'float_'): np.float_ = np.float64

from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer

# --- Config ---
INDEX_NAME = "ecommerce_products"
CSV_FILE = "products_white_rose.csv"
BATCH_SIZE = 500

# เชื่อมต่อ OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True, use_ssl=False, verify_certs=False, timeout=60
)

def get_model():
    print("⏳ Loading AI Model...")
    try:
        # ลองตัวเก่งก่อน (MPNet)
        return SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    except Exception as e:
        print(f"⚠️ Warning: Model ตัวหลักโหลดไม่ได้ ({e})")
        print("🔄 Switching to smaller model (MiniLM)...")
        # ถ้าพัง ให้ใช้ตัวเล็กแทน (กินแรมน้อยกว่า)
        return SentenceTransformer('all-MiniLM-L6-v2')

def import_data():
    # 1. เช็คไฟล์ก่อนเลย
    try:
        with open(CSV_FILE, encoding='utf-8') as f:
            total_rows = sum(1 for line in f) - 1
    except FileNotFoundError:
        print(f"❌ Error: หาไฟล์ '{CSV_FILE}' ไม่เจอ!")
        print("👉 ต้องรัน 'python gen_white_rose_data.py' ก่อนนะครับ")
        return

    # 2. โหลดโมเดล (ย้ายมาทำตรงนี้จะได้เห็น error)
    try:
        model = get_model()
        vector_dim = model.get_sentence_embedding_dimension()
        print(f"✅ Model Loaded! Dimension: {vector_dim}")
    except Exception as e:
        print(f"❌ Critical Error: โหลดโมเดลไม่ผ่านเลย ({e})")
        return

    # 3. เตรียม Database
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
                    "dimension": vector_dim, # ใช้ค่าจริงจากโมเดล
                    "method": {"name": "hnsw", "space_type": "cosinesimil", "engine": "nmslib"}
                }
            }
        }
    }
    client.indices.create(index=INDEX_NAME, body=index_body)

    # 4. เริ่มอัดข้อมูล
    print(f"🚀 Importing {total_rows:,} items...")
    actions = []
    
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in tqdm(reader, total=total_rows, unit="item"):
            try:
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
                
                if len(actions) >= BATCH_SIZE:
                    helpers.bulk(client, actions)
                    actions = []
            except Exception as e:
                print(f"⚠️ Skip row: {e}")
                continue

        if actions:
            helpers.bulk(client, actions)

    print("\n🎉 MISSION COMPLETE! ข้อมูลเข้าตู้เรียบร้อยครับ")

if __name__ == "__main__":
    if client.ping():
        import_data()
    else:
        print("❌ Connect OpenSearch ไม่ได้ (เช็ค Docker ด่วน!)")