import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import io

# 1. 페이지 인터페이스 및 브랜드 설정
st.set_page_config(page_title="박사원의 유튜브 업로드세팅 툴", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #C0392B; }
    .tag-box { 
        background-color: #1e1e1e; 
        padding: 20px; 
        border-radius: 10px; 
        border: 2px solid #00FF00; 
        color: #00FF00; 
        font-family: monospace; 
        font-size: 1.3rem; 
        margin-bottom: 20px;
    }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 박사원의 유튜브 업로드세팅 툴 (v4.0)")

# 2. 시스템 엔진 설정 (Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 박사원의 워크벤치")
    model_options = ["gemini-2.0-flash", "gemini-2.5-flash"]
    selected_model = st.selectbox("엔진 선택", model_options)
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# 3. 유로진 전용 고정 템플릿
default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫

{summary}

유로진남성의원 부산점은 단순한 진료를 넘어,
남성의 자신감과 삶의 질을 회복하도록 돕는 전문 클리닉입니다.
비뇨기 질환부터 남성
