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
    .notice-card-pinned { background-color: #2d333b; padding: 20px; border-radius: 10px; border-left: 8px solid #f1c40f; margin-bottom: 15px; border-top: 1px solid #f1c40f; }
    .notice-card { background-color: #21262d; padding: 20px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 15px; }
    .pinned-badge { background-color: #f1c40f; color: #000; padding: 2px 8px; border-radius: 5px; font-size: 0.8rem; font-weight: bold; margin-left: 10px; }
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
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
st.warning("⚠️ **주의:** 생성 중 메뉴 이동 시 데이터가 초기화됩니다. 결과 도출까지 현재 화면을 유지해 주세요.")

# 4. 시스템 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정 오류 (GEMINI_API_KEY)")
    st.stop()

# 5. 사이드바 메뉴
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
# 6. 기능 1: 유튜브 업로드 세팅
# ==========================================
if menu == "🎬 유튜브 업로드 세팅":
    st.title("🎬 유튜브 업로드 세팅")
    with st.expander("🛠️ 설명란 양식 편집", expanded=False):
        default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫\n\n{summary}\n\n📍 위치 : 부산 부산진구 부전동 257-3\n✔️ 홈페이지 : http://busan.urogyn.co.kr/"""
        desc_template = st.text_area("템플릿", value=default_template, height=200)
        fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

    uploaded_file = st.file_uploader("스크립트 파일 업로드", type=["txt", "docx", "pdf"], key="yt_up")
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
                pr = PyPDF2.PdfReader(uploaded_file)
                for p in pr.pages: final_script += (p.extract_text() or "") + "\n"
        except Exception as e: st.error(f"파일 로드 실패: {e}")
    else: final_script = st.text_area("직접 입력", height=200, key="yt_text")

    if st.button("🚀 데이터 추출하기"):
        if not final_script: st.warning("분석할 내용을 입력해주세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner("🎬 최적화된 데이터를 생성 중..."):
                    prompt = f"유튜브 PD로서 분석해. 요약 4~5줄, 줄바꿈 필수, 이모지 포함. 태그 쉼표 구분 50개. 결과 JSON. {final_script}"
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    data = json.loads(response.text)
                    st.session_state.tokens = response.usage_metadata.total_token_count
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                    st.code(f"{desc_template.replace('{summary}', data.get('summary_content', ''))}\n\n{fixed_hashtags}", language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 7. 기능 2: 비즈니스 격식 변환기
# ==========================================
elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    biz_tone = st.selectbox("변환 톤", ["아주 정중하게 (이메일용)", "부드럽고 친절하게 (카톡용)", "단호하고 명확하게 (공문용)"])
    raw_text = st.text_area("내용 입력", height=200)
    if st.button("✨ 변환하기"):
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner("📧 문장을 정중하게 다듬는 중..."):
                prompt = f"비즈니스 전문가로서 '영상팀 박진성 사원' 명의로 다음을 '{biz_tone}'으로 변환. {raw_text}"
                response = model.generate_content(prompt)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.code(response.text, language="text")
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 8. 기능 3: 콘텐츠 기획 콘티 (시즌 7 Style)
# ==========================================
elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 Style)")
    client_name = st.text_input("업체명", value="유로진 부산점")
    q_count = st.slider("질문 개수", 3, 10, 6)
    st.markdown("### 🎯 주제별 상세 가이드")
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        f1 = st.text_input("주제 1", placeholder="도입부 위험성 강조")
        f2 = st.text_input("주제 2", placeholder="민간요법 팩트체크")
    with c_t2:
        f3 = st.text_input("주제 3", placeholder="수술 상세 과정")
        f4 = st.text_input("주제 4", placeholder="사후 관리 및 당부")

    uploaded_ref = st.file_uploader("레퍼런스 파일", type=["txt", "docx", "pdf"], key="ref_up")
    final_ref = ""
    if uploaded_ref:
        try:
            ftype = uploaded_ref.name.split('.')[-1].lower()
            if ftype == 'txt': final_ref = uploaded_ref.read().decode("utf-8")
            elif ftype == 'docx': final_ref = "\n".join([p.text for p in Document(uploaded_ref).paragraphs])
            elif ftype == 'pdf':
                pr = PyPDF2.PdfReader(uploaded_ref)
                for p in pr.pages: final_ref += (p.extract_text() or "") + "\n"
        except: st.error("파일 로드 실패")
    else: final_ref = st.text_area("레퍼런스 직접 입력", height=150)

    if st.button("💡 맞춤형 콘티 생성"):
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner("📝 기획 의도를 반영한 콘티 설계 중..."):
                prompt = f"전략가로서 '{client_name}' 콘티 작성. 주제1:{f1}, 주제2:{f2}, 주제3:{f3}, 주제4:{f4}. 시즌 7 형식 준수. 질문 {q_count}개. 레퍼런스:{final_ref}"
                response = model.generate_content(prompt)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.write(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                st.balloons()
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 9. 기능 4: 공지게시판 (상단 고정 강화)
# ==========================================
elif menu == "📋 공지게시판":
    st.title("📋 팀 공지게시판")
    
    #  SyntaxError 해결: 괄호와 따옴표를 정확히 닫았습니다.
    with st.expander("➕ 새 공지사항 작성 (관리자 인증)", expanded=False):
        new_tag = st.selectbox("태그", ["필독", "안내", "업데이트", "긴급"])
        new_content = st.text_area("내용 입력")
        uploaded_img = st.file_uploader("사진 첨부", type=["png", "jpg", "jpeg"])
        admin_password = st.text_input("비밀번호", type="password", key="reg_pass")
        
        if st.button("📢 공지 등록"):
            if admin_password == "0914":
                if new_content:
                    img_base64 = img_to_base64(uploaded_img)
                    new_notice = {
                        "id": random.randint(100000, 999999),
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "tag": new_tag,
                        "content": new_content,
                        "image": img_base64,
                        "pinned": False
                    }
                    st.session_state.notices.insert(0, new_notice)
                    save_notices(st.session_state.notices)
                    st.success("✅ 공지가 등록되었습니다.")
                    st.rerun()
            else: st.error("❌ 비밀번호 불일치")

    st.markdown("---")
    
    # [게시판 내 상단 고정 로직] 고정된 공지를 리스트 가장 앞으로 정렬
    sorted_notices = sorted(st.session_state.notices, key=lambda x: x.get('pinned', False), reverse=True)
    
    if not sorted_notices:
        st.write("등록된 공지사항이 없습니다.")
    
    for notice in sorted_notices:
        # 실제 데이터 인덱스 확보
        actual_idx = next(i for i, n in enumerate(st.session_state.notices) if n['id'] == notice['id'])
        is_pinned = notice.get("pinned", False)
        card_class = "notice-card-pinned" if is_pinned else "notice-card"
        pin_label = "📌 상단 고정됨" if is_pinned else ""
        
        st.markdown(f"""
            <div class="{card_class}">
                <small>[{notice['date']}] <b>{notice['tag']}</b> <span style="color:#f1c40f; font-weight:bold;">{pin_label}</span></small><br>
                <p style="font-size: 1.1rem; margin-top: 10px;">{notice['content']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if notice.get("image"):
            try: st.image(base64.b64decode(notice["image"]), width=400)
            except: pass
        
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            with st.popover("📌 고정 설정"):
                p_pass = st.text_input("비밀번호", type="password", key=f"pin_p_{notice['id']}")
                if st.button("고정/해제", key=f"pin_b_{notice['id']}"):
                    if p_pass == "0914":
                        if not is_pinned:
                            for n in st.session_state.notices: n["pinned"] = False
                            st.session_state.notices[actual_idx]["pinned"] = True
                        else:
                            st.session_state.notices[actual_idx]["pinned"] = False
                        save_notices(st.session_state.notices)
                        st.rerun()
                    else: st.error("비밀번호 불일치")
        with c2:
            with st.popover("🗑️ 삭제"):
                del_pass = st.text_input("비밀번호", type="password", key=f"del_p_{notice['id']}")
                if st.button("삭제 확인", key=f"del_b_{notice['id']}"):
                    if del_pass == "0914":
                        st.session_state.notices.pop(actual_idx)
                        save_notices(st.session_state.notices)
                        st.rerun()
                    else: st.error("비밀번호 불일치")
        st.markdown("<br>", unsafe_allow_html=True)
