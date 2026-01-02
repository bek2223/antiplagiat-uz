import streamlit as st
from docx import Document
import pdfplumber
import requests
import json
import time

# Sahifa sozlamalari
st.set_page_config(page_title="Antiplagiat Pro AI", page_icon="🔍", layout="wide")

# CSS dizayni (unsafe_allow_html ishlatildi)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Shaffof Antiplagiat Platformasi")

# --- SOZLAMALAR ---
# Serper API kalitingiz
SERPER_API_KEY = "38c45e021308ac05f6c824fdab463fd816949f79" 

def read_docx(file):
    doc = Document(file)
    return " ".join([p.text for p in doc.paragraphs if p.text])

def read_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            content = page.extract_text()
            if content: text += content + "\n"
    return text

def get_chunks(text, words_per_chunk=40):
    words = text.split()
    for i in range(0, len(words), words_per_chunk):
        yield " ".join(words[i:i + words_per_chunk])

def search_internet(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except: return []

# --- INTERFEYS ---
uploaded_file = st.file_uploader("Hujjatni yuklang (PDF yoki DOCX)", type=['docx', 'pdf'])

if uploaded_file:
    # Faylni o'qish
    raw_text = read_docx(uploaded_file) if uploaded_file.name.endswith('.docx') else read_pdf(uploaded_file)
    
    st.info(f"Fayl o'qildi: {len(raw_text.split())} ta so'z mavjud.")

    if st.button("🚀 Tahlilni internetda boshlash"):
        chunks = list(get_chunks(raw_text, 40))
        total_chunks = min(len(chunks), 10) # Dastlabki 10 bo'lakni tekshirish
        
        progress_bar = st.progress(0)
        plagiarized_count = 0
        found_sources = []

        for i in range(total_chunks):
            results = search_internet(chunks[i])
            if results:
                plagiarized_count += 1
                found_sources.extend(results)
            progress_bar.progress((i + 1) / total_chunks)
            time.sleep(0.1)

        # Foizni hisoblash
        plagiarism_percent = int((plagiarized_count / total_chunks) * 100)
        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.header(f"Natija: {plagiarism_percent}%")
            if plagiarism_percent > 30:
                st.error("Diqqat! O'xshashlik yuqori.")
            else:
                st.success("Matn original deb topildi.")
        
        with c2:
            st.subheader("Topilgan manbalar")
            unique_sources = {s['link']: s for s in found_sources}.values()
            for source in list(unique_sources)[:5]:
                st.markdown(f"🔗 [{source['title']}]({source['link']})")

st.sidebar.title("🛠 Tizim holati")
st.sidebar.success("Internetga ulangan")
st.sidebar.write("GitHub Repository: **antiplagiat-pro**")
