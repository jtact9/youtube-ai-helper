import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import io

# 1. 페이지 인터페이스 설정
st.set_page_config(page_title="박사원의 유튜브 업로드세팅 툴", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    /* 버튼 및 UI 요소 */
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    /* 태그 박스 가독성 및 스크롤 방지 */
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
    /* 결과 섹션 배경 */
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 박사원의 유튜브 업로드세팅 툴 (v3.6)")

# 2. 시스템 엔진 설정 (Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 박사원의 워크벤치")
    selected_model = st.selectbox("엔진 선택", ["gemini-2.5-flash", "gemini-2.0-flash"])
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# 3. 고정 양식 설정
default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫

{summary}

유로진남성의원 부산점은 단순한 진료를 넘어,
남성의 자신감과 삶의 질을 회복하도록 돕는 전문 클리닉입니다.
비뇨기 질환부터 남성 성 건강까지, 믿을 수 있는 의료진이 함께합니다.

📩 궁금한 점이나 상담이 필요하다면 댓글로 남겨주세요.
➡️ 유로진남성의 부산점에서 직접 답변드립니다.

📍 위치 : 부산 부산진구 부전동 257-3
✔️ 홈페이지 : http://busan.urogyn.co.kr/
✔️ 블로그 : https://blog.naver.com/kumhot_22
✔️ 카카오톡 상담하기 : https://pf.kakao.com/_BjZTxd"""

with st.expander("🛠️ 설명란 고정 양식 및 프리셋", expanded=False):
    desc_template = st.text_area("템플릿 편집", value=default_template, height=350)
    fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

# 4. 입력 섹션
st.subheader("📁 스크립트 불러오기")
uploaded_file = st.file_uploader("메모장(TXT), 워드, PDF 지원", type=["txt", "docx", "pdf"])

final_script = ""
if uploaded_file:
    try:
        ftype = uploaded_file.name.split('.')[-1].lower()
        if ftype == 'txt':
            raw = uploaded_file.read()
            try: final_script = raw.decode("utf-8")
            except: final_script = raw.decode("cp949")
        elif ftype == 'docx':
