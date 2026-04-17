import streamlit as st
import google.generativeai as genai
import json
import os
import base64
from docx import Document
import PyPDF2
import random
from datetime import datetime
from io import BytesIO

# 1. 페이지 브랜딩 및 디자인 설정
st.set_page_config(page_title="박사원의 만능 워크벤치", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .marquee {
        width: 100%; line-height: 50px; background-color: #f1c40f; color: #000;
        white-space: nowrap; overflow: hidden; box-sizing: border-box;
        border-radius: 10px; margin-bottom: 20px; font-weight: bold;
    }
    .marquee p {
        display: inline-block; padding-left: 100%;
        animation: marquee 25s linear infinite; margin: 0;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    /* 고정 게시물용 스타일 */
    .notice-card-pinned { background-color: #2d333b; padding: 20px; border-radius: 10px; border-left: 8px solid #f1c40f; margin-bottom: 15px; border-top: 1px solid #f1c40f; }
    /* 일반 게시물용 스타일 */
    .notice-card { background-color: #21262d; padding: 20px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 15px; }
    .pinned-badge { background-color: #f1c40f; color: #000; padding: 2px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 저장 로직
NOTICES_FILE = 'notices.json'

def load_notices():
    if os.path.exists(NOTICES_FILE):
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if data else []
        except: return []
    return [{"id": 1, "date": datetime.now().strftime("%Y-%m-%d"), "tag": "필독", "content": "🚨 [가이드] 생성 중 메뉴 전환 시 초기화됩니다. 에러 시 엔진 변경 후 1분 뒤 재시도 바랍니다. 🚨", "image": None, "pinned": True}]

def save_notices(notices):
    with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notices, f, ensure_ascii=False, indent=4)

if 'notices' not in st.session_state:
    st.session_state.notices = load_notices()

# 3. 상단 동적 공지 (고정 기능 반영)
pinned_list = [n for n in st.session_state.notices if n.get('pinned', False)]
marquee_content = f"📌 [고정] {pinned_list[0]['content']}" if pinned_list else (st.session_state.notices[0]['content'] if st.session_state.notices else "현재 등록된 공지가 없습니다.")

st.markdown(f'<div class="marquee"><p>{marquee_content}</p></div>', unsafe_allow_html=True)
st.warning("⚠️ **주의:** 생성 중 메뉴 이동 시 데이터가 초기화됩니다.")

# 4. 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정 오류")
    st.stop()

# 5. 사이드바
with st.sidebar:
    st.title("🛠️ 워크벤치")
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티", "📋 공지게시판"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

def img_to_base64(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.read()).decode()
    return None

# ==========================================
# 기능 1, 2, 3 (기존 기능 유지)
# ==========================================
if menu == "🎬 유튜브 업로드 세팅":
    st.title("🎬 유튜브 업로드 세팅")
    with st.expander("🛠️ 설명란 양식 편집", expanded=False):
        default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫\n\n{summary}\n\n📍 위치 : 부산 부산진구 부전동 257-3\n✔️ 홈페이지 : http://busan.urogyn.co.kr/"""
        desc_template = st.text_area("템플릿", value=default_template, height=200)
        fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

    uploaded_file = st.file_uploader("스크립트 업로드", type=["txt", "docx", "pdf"], key="yt_up")
    final_script = st.text_area("직접 입력", height=200) if not uploaded_file else ""
    # [파일 로드 및 생성 로직 생략 - v7.6과 동일]
    if st.button("🚀 데이터 추출하기"):
        # 생략된 로직은 v7.6 코드를 그대로 따릅니다.
        pass

elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    # [변환기 로직 생략 - v7.6과 동일]
    pass

elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 Style)")
    # [콘티 로직 생략 - v7.6과 동일]
    pass

# ==========================================
# 9. 기능 4: 공지게시판 (게시판 내 상단 고정 강화)
# ==========================================
elif menu == "📋 공지게시판":
    st.title("📋 팀 공지게시판")
    
    with st.expander("➕
