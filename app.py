import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import random
from datetime import datetime

# 1. 페이지 브랜딩 및 디자인 설정
st.set_page_config(page_title="박사원의 만능 워크벤치", layout="wide", page_icon="🚀")

# CSS: UI 스타일 및 애니메이션 정의
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
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    .notice-card { background-color: #21262d; padding: 15px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 최상단 흐르는 공지사항 (긴급 가이드)
st.markdown("""
    <div class="marquee">
        <p>🚨 [필독] 생성 도중 페이지를 벗어나거나 업무를 전환하면 작업이 초기화됩니다! 에러 시 엔진 변경 후 1분 뒤 재실행 바랍니다. 버튼 연타 금지! 🚨</p>
    </div>
    """, unsafe_allow_html=True)

# 3. 고정형 초기화 경고
st.warning("⚠️ **주의:** 메뉴 전환 시 입력 데이터가 사라집니다. 결과가 나올 때까지 현재 페이지를 유지해 주세요.")

# 4. 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 확인하세요.")
    st.stop()

# 5. 사이드바 메인 메뉴
with st.sidebar:
    st.title("🛠️ 박사원의 워크벤치")
    # 공지게시판 메뉴 추가
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티", "📋 공지게시판"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# --- 데이터 보존을 위한 session_state 설정 ---
if 'notices' not in st.session_state:
    st.session_state.notices = [
        {"date": "2026-04-17", "tag": "필독", "content": "워크벤치 v7.0 업데이트: 공지게시판 기능이 추가되었습니다."},
        {"date": "2026-04-16", "tag": "안내", "content": "서버 부하 방지를 위해 API 요청은 분당 5회로 제한됩니다."}
    ]

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
            if ftype == 'txt': final_script = uploaded_file.read().decode("utf-8")
            elif ftype == 'docx': final_script = "\n".join([p.text for p in Document(uploaded_file).paragraphs])
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
                    prompt = f"유튜브 PD로서 분석해. 요약 4~5줄, 줄바꿈 필수, 이모지 포함, 호기심 유발. 태그 쉼표 구분 50개. 결과 JSON. {final_script}"
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    data = json.loads(response.text)
                    st.session_state.tokens = response.usage_metadata.total_token_count
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                    summary = data.get("summary_content", "")
                    st.code(f"{desc_template.replace('{summary}', summary)}\n\n{fixed_hashtags}", language="text")
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
            with st.spinner("📧 문장을 다듬는 중..."):
                prompt = f"비즈니스 전문가로서 '영상팀 박진성 사원' 명의로 다음을 '{biz_tone}'으로 변환. {raw_text}"
                response = model.generate_content(prompt)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.code(response.text, language="text")
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 8. 기능 3: 콘텐츠 기획 콘티
# ==========================================
elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 Style)")
    col_c1, col_c2 = st.columns(2)
    with col_c1: client_name = st.text_input("업체명", value="유로진 부산점")
    with col_c2: q_count = st.slider("질문 개수", 3, 10, 6)
    
    st.markdown("### 🎯 주제별 상세 가이드")
    st.info("각 주제에서 다룰 핵심 의도를 입력해주세요.")
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        f1 = st.text_input("주제 1", placeholder="도입부 위험성 강조")
        f2 = st.text_input("주제 2", placeholder="민간요법 팩트체크")
    with c_t2:
        f3 = st.text_input("주제 3", placeholder="수술 상세 과정")
        f4 = st.text_input("주제 4", placeholder="사후 관리 및 당부")

    uploaded_ref = st.file_uploader("레퍼런스 파일", type=["txt", "docx", "pdf"])
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
            with st.spinner("📝 PD님의 의도를 반영한 콘티 설계 중..."):
                prompt = f"전략가로서 '{client_name}' 콘티 작성. 주제1:{f1}, 주제2:{f2}, 주제3:{f3}, 주제4:{f4}. 시즌 7 형식 준수. 질문 {q_count}개. 레퍼런스:{final_ref}"
                response = model.generate_content(prompt)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.write(response.text)
                st.markdown('</div>', unsafe_allow_html=True)
                st.balloons()
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 9. 기능 4: 공지게시판 (Notice Board)
# ==========================================
elif menu == "📋 공지게시판":
    st.title("📋 팀 공지게시판")
    st.write("팀원들과 공유할 공지사항을 확인하고 관리할 수 있습니다.")

    # 공지사항 작성 (Admin 영역)
    with st.expander("➕ 새 공지사항 작성 (PD 전용)", expanded=False):
        new_tag = st.selectbox("태그 선택", ["필독", "안내", "업데이트", "긴급"])
        new_content = st.text_area("공지 내용 입력")
        if st.button("📢 공지 등록"):
            if new_content:
                new_notice = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "tag": new_tag,
                    "content": new_content
                }
                # 최신 공지가 위로 오게 추가
                st.session_state.notices.insert(0, new_notice)
                st.success("새 공지가 등록되었습니다.")
                st.rerun()

    # 공지사항 리스트 출력
    st.markdown("---")
    for notice in st.session_state.notices:
        st.markdown(f"""
            <div class="notice-card">
                <small>[{notice['date']}] <b>{notice['tag']}</b></small><br>
                {notice['content']}
            </div>
        """, unsafe_allow_html=True)
