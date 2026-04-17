import streamlit as st
import google.generativeai as genai
import json
import os  # 파일 존재 확인을 위해 추가
from docx import Document
import PyPDF2
import random
from datetime import datetime

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
    .notice-card { background-color: #21262d; padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 파일 저장 로직 (영구 저장용)
NOTICES_FILE = 'notices.json'

def load_notices():
    """파일에서 공지사항 로드"""
    if os.path.exists(NOTICES_FILE):
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_notices(notices):
    """파일에 공지사항 저장"""
    with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notices, f, ensure_ascii=False, indent=4)

# 3. 최상단 공지 및 경고
st.markdown("""
    <div class="marquee">
        <p>🚨 [필독] 생성 도중 메뉴를 전환하면 작업이 초기화됩니다! 에러 시 엔진 변경 후 1분 뒤 재실행 바랍니다. 연타 금지! 🚨</p>
    </div>
    """, unsafe_allow_html=True)

# 4. 시스템 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정 오류")
    st.stop()

# 5. 사이드바 메뉴
with st.sidebar:
    st.title("🛠️ 박사원의 워크벤치")
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티", "📋 공지게시판"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])

# --- 초기 데이터 로드 ---
if 'notices' not in st.session_state:
    st.session_state.notices = load_notices()

# ==========================================
# 기능 1, 2, 3 (기존 로직 유지)
# ==========================================
# [중략: 유튜브 세팅, 비즈니스 변환, 콘티 기획 로직은 v7.1과 동일하게 작동합니다]

# ==========================================
# 6. 기능 4: 공지게시판 (저장 기능 강화)
# ==========================================
elif menu == "📋 공지게시판":
    st.title("📋 팀 공지게시판")
    
    with st.expander("➕ 새 공지사항 작성 (관리자 인증)", expanded=False):
        new_tag = st.selectbox("태그", ["필독", "안내", "업데이트", "긴급"])
        new_content = st.text_area("내용 입력")
        admin_password = st.text_input("보안 비밀번호", type="password")
        
        if st.button("📢 공지 등록"):
            if admin_password == "0914":
                if new_content:
                    new_notice = {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "tag": new_tag,
                        "content": new_content
                    }
                    # 리스트 추가 및 파일 저장
                    st.session_state.notices.insert(0, new_notice)
                    save_notices(st.session_state.notices)
                    st.success("✅ 공지가 파일에 안전하게 저장되었습니다.")
                    st.rerun()
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")

    st.markdown("---")
    # 저장된 공지가 없을 경우 안내
    if not st.session_state.notices:
        st.write("등록된 공지사항이 없습니다.")
    
    for notice in st.session_state.notices:
        st.markdown(f"""
            <div class="notice-card">
                <small>[{notice['date']}] <b>{notice['tag']}</b></small><br>
                {notice['content']}
            </div>
        """, unsafe_allow_html=True)
