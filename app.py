import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import random

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="박사원의 만능 워크벤치", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #C0392B; }
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 등록하세요.")
    st.stop()

# 3. 사이드바 메인 메뉴
with st.sidebar:
    st.title("🛠️ 박사원의 워크벤치")
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# --- 랜덤 메시지 세트 ---
msgs_yt = ["🎬 박사원이 컷편집 정밀하게 들어가는 중...", "✂️ 박사원이 썸네일 카피 고뇌하는 중..."]
msgs_biz = ["💼 박사원이 정장 갈아입고 명함 챙기는 중...", "✍️ 박사원이 정중한 문장으로 다듬는 중..."]
msgs_conti = ["📝 박사원이 레퍼런스 뜯어보며 콘티 짜는 중...", "💡 박사원이 기발한 질문 리스트 뽑는 중...", "🔍 박사원이 업체 맞춤형 전략 수립 중..."]

# ==========================================
# 4. 기능 1: 유튜브 업로드 세팅
# ==========================================
if menu == "🎬 유튜브 업로드 세팅":
    st.title("🎬 유튜브 업로드 세팅")
    with st.expander("🛠️ 설명란 양식 편집", expanded=False):
        default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫\n\n{summary}\n\n📍 위치 : 부산 부산진구 부전동 257-3\n✔️ 홈페이지 : http://busan.urogyn.co.kr/"""
        desc_template = st.text_area("템플릿", value=default_template, height=200)
        fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

    uploaded_file = st.file_uploader("스크립트 파일 업로드", type=["txt", "docx", "pdf"], key="yt_file")
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
                pdf = PyPDF2.PdfReader(uploaded_file)
                for p in pdf.pages: final_script += p.extract_text() + "\n"
        except Exception as e: st.error(f"파일 로드 실패: {e}")
    else:
        final_script = st.text_area("직접 입력", height=150, key="yt_text")

    if st.button("🚀 데이터 추출하기"):
        if not final_script: st.warning("내용을 입력해주세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner(random.choice(msgs_yt)):
                    prompt = f"유튜브 PD로서 다음 스크립트 분석해. 요약은 4~5줄, 문장마다 줄바꿈 필수, 이모지 포함, 호기심 유발. 태그는 쉼표 구분 50개. 결과 JSON으로. 스크립트: {final_script}"
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    data = json.loads(response.text)
                    st.session_state.tokens = response.usage_metadata.total_token_count
                    
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<span class="big-font">🏷️ 검색용 고밀도 태그</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<span class="big-font">📋 최종 설명란</span>', unsafe_allow_html=True)
                    final_desc = desc_template.replace("{summary}", data.get("summary_content", ""))
                    st.code(f"{final_desc}\n\n{fixed_hashtags}", language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 5. 기능 2: 비즈니스 격식 변환기
# ==========================================
elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    biz_tone = st.selectbox("변환 톤 선택", ["아주 정중하게 (이메일용)", "부드럽고 친절하게 (카톡/문자용)", "단호하고 명확하게 (공문/요청용)"])
    raw_text = st.text_area("내용 입력", height=200, placeholder="예: 낼 촬영 2시 가능?")

    if st.button("✨ 변환하기"):
        if not raw_text: st.warning("내용을 입력하세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner(random
