import csv
import time
import numpy as np

# Fix Numpy 2.0
if not hasattr(np, 'float_'):
    np.float_ = np.float64

from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer

# --- Config การเชื่อมต่อ (ใช้ HTTP ธรรมดา) ---
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    http_compress=True,
    use_ssl=False,         # <--- ปิด SSL (เพราะ Docker เราปิด Security ไว้)
    verify_certs=False,
    timeout=30             # <--- เพิ่มเวลาการรอเป็น 30 วินาที
)

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2') 
INDEX_NAME = "ecommerce_products"

def wait_for_server():
    """ฟังก์ชันวนรอจนกว่า Server จะพร้อม"""
    print("⏳ Connecting to OpenSearch...", end="", flush=True)
    for _ in range(10): # ลอง 10 ครั้ง (ประมาณ 20 วิ)
        try:
            if client.ping():
                print(" ✅ Connected!")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(2)
    print("\n❌ Error: ต่อ Server ไม่ได้เลย (เช็ค Docker หรือยัง?)")
    return False

def load_data_from_csv(filename):
    # 1. รอให้ Server พร้อมก่อน
    if not wait_for_server():
        return

    print(f"📂 Reading {filename}...")
    actions = [] 
    
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
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
                
                if len(actions) >= 100:
                    helpers.bulk(client, actions)
                    print(f"🚀 Indexed batch of {len(actions)}...")
                    actions = [] 

        if actions:
            helpers.bulk(client, actions)
            print(f"🚀 Indexed remaining {len(actions)}.")
            
        print("✅ All data imported successfully!")

    except FileNotFoundError:
        print(f"❌ Error: หาไฟล์ {filename} ไม่เจอ! (วางไว้โฟลเดอร์เดียวกับไฟล์ py หรือยัง?)")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    load_data_from_csv('products.csv')