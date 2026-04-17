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

# CSS: UI 스타일 및 애니메이션
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
    .notice-card { background-color: #21262d; padding: 20px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 15px; }
    .delete-btn>button { background-color: #555 !important; height: 2em !important; font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 저장 및 이미지 처리 로직
NOTICES_FILE = 'notices.json'

def load_notices():
    if os.path.exists(NOTICES_FILE):
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return [{"date": datetime.now().strftime("%Y-%m-%d"), "tag": "필독", "content": "🚨 [가이드] 생성 도중 메뉴 전환 시 작업이 초기화됩니다. 에러 발생 시 엔진 변경 후 1분 뒤 재시도 바랍니다. 🚨", "image": None}]

def save_notices(notices):
    with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notices, f, ensure_ascii=False, indent=4)

if 'notices' not in st.session_state:
    st.session_state.notices = load_notices()

# 3. 최상단 동적 공지사항 (최신 텍스트 공지 연동)
latest_notice = st.session_state.notices[0]['content'] if st.session_state.notices else "현재 등록된 공지사항이 없습니다."
st.markdown(f'<div class="marquee"><p>{latest_notice}</p></div>', unsafe_allow_html=True)

st.warning("⚠️ **주의:** 생성 중 메뉴 이동 시 데이터가 초기화됩니다. 결과 도출까지 현재 화면을 유지해 주세요.")

# 4. 시스템 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정 오류")
    st.stop()

# 5. 사이드바 메뉴
with st.sidebar:
    st.title("🛠️ 워크벤치")
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티", "📋 공지게시판"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])

# --- 공통 유틸리티: 이미지 인코딩 ---
def img_to_base64(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.read()).decode()
    return None

# ==========================================
# 기능 1, 2, 3 (기존 로직 유지)
# ==========================================
# [중략: 유튜브 세팅, 비즈니스 변환, 콘티 기획 로직은 v7.3과 동일하게 작동합니다]

# ==========================================
# 9. 기능 4: 공지게시판 (삭제 및 이미지 추가)
# ==========================================
elif menu == "📋 공지게시판":
    st.title("📋 팀 공지게시판")
    
    with st.expander("➕ 새 공지사항 작성 (관리자 인증)", expanded=False):
        new_tag = st.selectbox("태그", ["필독", "안내", "업데이트", "긴급"])
        new_content = st.text_area("내용 입력")
        
        # 이미지 첨부 기능
        uploaded_img = st.file_uploader("사진 첨부 (선택 사항)", type=["png", "jpg", "jpeg"])
        
        admin_password = st.text_input("보안 비밀번호", type="password", key="reg_pass")
        
        if st.button("📢 공지 등록"):
            if admin_password == "0914":
                if new_content:
                    img_base64 = img_to_base64(uploaded_img)
                    new_notice = {
                        "id": random.randint(1000, 9999), # 삭제를 위한 임시 ID
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "tag": new_tag,
                        "content": new_content,
                        "image": img_base64
                    }
                    st.session_state.notices.insert(0, new_notice)
                    save_notices(st.session_state.notices)
                    st.success("✅ 공지가 이미지와 함께 등록되었습니다.")
                    st.rerun()
            else: st.error("❌ 비밀번호가 틀렸습니다.")

    st.markdown("---")
    
    if not st.session_state.notices:
        st.write("등록된 공지사항이 없습니다.")
    
    for idx, notice in enumerate(st.session_state.notices):
        with st.container():
            st.markdown(f"""
                <div class="notice-card">
                    <small>[{notice['date']}] <b>{notice['tag']}</b></small><br>
                    <p style="font-size: 1.1rem; margin-top: 10px;">{notice['content']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 이미지 출력
            if notice.get("image"):
                st.image(base64.b64decode(notice["image"]), width=400)
            
            # 삭제 기능 (비밀번호 확인 후 삭제)
            with st.popover("🗑️ 삭제"):
                del_pass = st.text_input(f"삭제 비밀번호 ({notice['date']})", type="password", key=f"del_{idx}")
                if st.button("영구 삭제 확인", key=f"btn_{idx}"):
                    if del_pass == "0914":
                        st.session_state.notices.pop(idx)
                        save_notices(st.session_state.notices)
                        st.success("공지가 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("비밀번호 불일치")
            st.markdown("<br>", unsafe_allow_html=True)
