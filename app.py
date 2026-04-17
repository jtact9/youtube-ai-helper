import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import random

# 1. 페이지 브랜딩 및 디자인 설정
st.set_page_config(page_title="박사원의 만능 워크벤치", layout="wide", page_icon="🚀")

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
        font-size: 1.1rem; 
        line-height: 1.8; 
    }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. 시스템 엔진 설정 (Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

# 3. 사이드바 메인 메뉴
with st.sidebar:
    st.title("🛠️ 박사원의 워크벤치")
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# --- 랜덤 로딩 메시지 세트 ---
msgs_yt = [
    "🎬 박사원이 컷편집 정밀하게 들어가는 중...", 
    "✂️ 박사원이 썸네일 카피 고뇌하는 중...",
    "🙏 유튜브 알고리즘 신에게 기도 올리는 중..."
]
msgs_biz = [
    "💼 박사원이 정장 갈아입고 명함 챙기는 중...", 
    "✍️ 박사원이 정중한 문장으로 다듬는 중...",
    "☕ 업체 미팅 전 맞춤법 검사기 돌리는 중..."
]
msgs_conti = [
    "📝 박사원이 레퍼런스 뜯어보며 콘티 짜는 중...", 
    "💡 박사원이 기발한 질문 리스트 뽑는 중...",
    "🔍 결론은 감추고 호기심은 키우는 중..."
]

# ==========================================
# 4. 기능 1: 유튜브 업로드 세팅
# ==========================================
if menu == "🎬 유튜브 업로드 세팅":
    st.title("🎬 유튜브 업로드 세팅")
    
    with st.expander("🛠️ 설명란 양식 편집", expanded=False):
        default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫\n\n{summary}\n\n📍 위치 : 부산 부산진구 부전동 257-3\n✔️ 홈페이지 : http://busan.urogyn.co.kr/"""
        desc_template = st.text_area("템플릿", value=default_template, height=200)
        fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

    uploaded_file = st.file_uploader("스크립트 파일 업로드", type=["txt", "docx", "pdf"])
    
    final_script = ""
    if uploaded_file:
        try:
            ftype = uploaded_file.name.split('.')[-1].lower()
            if ftype == 'txt':
                raw = uploaded_file.read()
                try: final_script = raw.decode("utf-8")
                except: final_script = raw.decode("cp949")
            elif ftype == 'docx':
                doc = Document(uploaded_file)
                final_script = "\n".join([p.text for p in doc.paragraphs])
            elif ftype == 'pdf':
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for p in pdf_reader.pages:
                    txt = p.extract_text()
                    if txt: final_script += txt + "\n"
            st.success(f"✅ {uploaded_file.name} 로드 성공")
        except Exception as e:
            st.error(f"파일 로드 실패: {e}")
    else:
        final_script = st.text_area("직접 입력", height=200, placeholder="여기에 스크립트를 직접 입력하세요.")

    if st.button("🚀 데이터 추출하기"):
        if not final_script:
            st.warning("분석할 내용을 입력해주세요.")
        else:
            try
