import streamlit as st
import requests
import pandas as pd

# กำหนด URL ของ API (ที่เราทำไว้ก่อนหน้านี้)
API_URL = "http://localhost:8000"

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="White Rose's AI Search PoC", page_icon="🛒", layout="wide")

# --- ส่วน Header ---
st.title("🛒 White Rose's AI Smart Search")
st.caption("Proof of Concept: Hybrid Search & AI Recommendation")

# --- ส่วน Sidebar (ตัวกรอง) ---
with st.sidebar:
    st.header("🔧 Filters")
    min_score = st.slider("AI Confidence Score", 0.0, 1.0, 0.5, 0.05, help="ค่าความมั่นใจของ AI (ยิ่งสูง ยิ่งตรง)")
    
    st.divider()
    
    # ปุ่ม Reset Database (เผื่อไว้โชว์ตอน Demo)
    if st.button("🔄 Reset / Setup Data"):
        try:
            res = requests.post(f"{API_URL}/setup")
            st.success("Database Reset Successful!")
        except:
            st.error("Connection failed. Is the API running?")

# --- ส่วนเนื้อหาหลัก ---
col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input("🔍 ค้นหาสินค้า (ลองพิมพ์แบบภาษาคนได้เลย)", placeholder="เช่น อยากทำหมูกระทะ, ของใช้ในห้องน้ำ, อาหารลดความอ้วน")

with col2:
    st.write("") # จัดระเบียบ
    st.write("") 
    search_btn = st.button("Search", type="primary", use_container_width=True)

# --- Logic การแสดงผล ---
if search_btn or query:
    if not query:
        st.warning("กรุณาพิมพ์คำค้นหาก่อนครับ")
    else:
        with st.spinner('🤖 AI กำลังวิเคราะห์ความต้องการของคุณ...'):
            try:
                # 1. ยิงไปหา API Search
                response = requests.get(f"{API_URL}/search", params={"q": query})
                data = response.json()
                
                results = data.get("data", [])
                
                # กรองตาม Score ที่เลือกใน Sidebar
                filtered_results = [r for r in results if r['score'] >= min_score]
                
                # --- ส่วนแสดงผล AI Summary (จำลอง) ---
                st.success(f"✅ พบสินค้าที่เกี่ยวข้อง: {len(filtered_results)} รายการ")
                
                if len(filtered_results) > 0:
                    # แปลงเป็น DataFrame เพื่อทำกราฟง่ายๆ
                    df = pd.DataFrame(filtered_results)
                    
                    # Layout แสดงของ
                    for index, row in df.iterrows():
                        with st.container():
                            c1, c2, c3 = st.columns([1, 3, 1])
                            with c1:
                                # รูปจำลอง (Placeholder)
                                st.image("https://via.placeholder.com/150", width=100)
                            with c2:
                                st.subheader(row['title'])
                                st.text(row.get('description', '-'))
                                st.caption(f"Category: {row['category']} | AI Score: {row['score']:.2f}")
                            with c3:
                                st.metric(label="ราคา", value=f"{row['price']} ฿")
                            st.divider()
                    
                    # --- ส่วน Analytics (โชว์ความเป็น PM สาย Data) ---
                    st.subheader("📊 Price Analysis")
                    st.bar_chart(df, x="title", y="price")
                    
                else:
                    st.info("ไม่พบสินค้าที่ตรงกับเงื่อนไข หรือ AI Score ต่ำเกินไป")

            except Exception as e:
                st.error(f"Error connecting to API: {e}")
                st.info("💡 อย่าลืมรัน 'uvicorn api:app --reload' ใน Terminal อีกตัวหนึ่งนะ!")