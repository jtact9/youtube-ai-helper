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

# --- 랜덤 로딩 메시지 ---
msgs_conti = ["📝 주제별 맞춤 가이드 반영 중...", "💡 시즌 7 스타일로 질문 뽑는 중...", "🔍 PD님의 기획 의도를 분석 중..."]

# ==========================================
# 4. 기능 1: 유튜브 업로드 세팅
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
                with st.spinner("🎬 최적화된 업로드 데이터를 생성 중..."):
                    prompt = f"유튜브 PD로서 분석해. 요약 4~5줄, 줄바꿈 필수, 이모지 포함, 호기심 유발. 태그 쉼표 구분 50개. 결과 JSON. {final_script}"
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    data = json.loads(response.text)
                    st.session_state.tokens = response.usage_metadata.total_token_count
                    
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown('<span class="big-font">🏷️ 검색용 고밀도 태그</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown('<span class="big-font">📋 최종 설명란 (복사용)</span>', unsafe_allow_html=True)
                    summary = data.get("summary_content", "")
                    final_desc = desc_template.replace("{summary}", summary)
                    st.code(f"{final_desc}\n\n{fixed_hashtags}", language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 5. 기능 2: 비즈니스 격식 변환기
# ==========================================
elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    biz_tone = st.selectbox("변환 톤", ["아주 정중하게 (이메일용)", "부드럽고 친절하게 (카톡용)", "단호하고 명확하게 (공문용)"])
    raw_text = st.text_area("내용 입력", height=200, placeholder="예: 낼 촬영 2시 가능?")

    if st.button("✨ 변환하기"):
        if not raw_text: st.warning("내용을 입력해주세요.")
        else:
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
# 6. 기능 3: 콘텐츠 기획 콘티 (v6.2)
# ==========================================
elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 자유 입력형)")
