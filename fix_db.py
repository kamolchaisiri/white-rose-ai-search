import csv
import numpy as np

# Fix Numpy 2.0
if not hasattr(np, 'float_'):
    np.float_ = np.float64

from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer

# --- 1. ตั้งค่าการเชื่อมต่อ (เหมือน api.py) ---
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,
    verify_certs=False,
    timeout=30
)

# --- 2. เลือกโมเดล (ต้องตรงกับ api.py) ---
# คุณใช้ตัวนี้อยู่ใช่ไหมครับ? ถ้าใช้ all-MiniLM ให้เปลี่ยนเป็น 384
model_name = 'paraphrase-multilingual-mpnet-base-v2' 
vector_dim = 768 

print(f"⏳ Loading Model: {model_name}...")
model = SentenceTransformer(model_name)

INDEX_NAME = "ecommerce_products"

def reset_index():
    print(f"🗑️  Deleting old index: {INDEX_NAME}...")
    # ลบของเก่าทิ้งแน่นอน 100%
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)

    print("🏗️  Creating new index with Vector Schema...")
    # สร้างใหม่แบบระบุสเปคชัดเจน
    index_body = {
        "settings": {
            "index": {
                "knn": True # <--- บรรทัดนี้สำคัญที่สุด! บอกให้เปิดระบบ Vector
            }
        },
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "category": {"type": "keyword"},
                "price": {"type": "float"},
                "description": {"type": "text"},
                "vector_embedding": {
                    "type": "knn_vector",  # <--- ระบุประเภทเป็น Vector
                    "dimension": vector_dim, # <--- ขนาดต้องตรงกับโมเดล
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib"
                    }
                }
            }
        }
    }
    client.indices.create(index=INDEX_NAME, body=index_body)
    print("✅ Index created successfully!")

def import_csv():
    print("📂 Reading products.csv...")
    actions = []
    try:
        with open('products.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # รวมคำ
                text = f"{row['title']} {row['description']} {row['category']}"
                # แปลง Vector
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
        
        if actions:
            helpers.bulk(client, actions)
            print(f"🚀 Imported {len(actions)} products to database.")
            
    except FileNotFoundError:
        print("❌ Error: หาไฟล์ products.csv ไม่เจอ")

if __name__ == "__main__":
    if client.ping():
        reset_index()  # ล้างและสร้างใหม่
        import_csv()   # ลงข้อมูล
        print("\n🎉 Repair Complete! คุณกลับไปรัน api.py ได้เลย")
    else:
        print("❌ Error: เชื่อมต่อ OpenSearch ไม่ได้ (Docker เปิดอยู่ไหม?)")