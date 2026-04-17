import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import random

# 1. 페이지 브랜딩 및 디자인 설정
st.set_page_config(page_title="박사원의 만능 워크벤치", layout="wide", page_icon="🚀")

# CSS: 흐르는 공지사항 및 UI 스타일 정의
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* 흐르는 공지사항 스타일 */
    .marquee {
        width: 100%;
        line-height: 50px;
        background-color: #f1c40f;
        color: #000;
        white-space: nowrap;
        overflow: hidden;
        box-sizing: border-box;
        border-radius: 10px;
        margin-bottom: 20px;
        font-weight: bold;
    }
    .marquee p {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 20s linear infinite;
        margin: 0;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. 최상단 공지사항 출력 (흐르는 자막)
st.markdown("""
    <div class="marquee">
        <p>🚨 [공지] 에러 발생 시 엔진 종류를 변경해 주세요! 엔진 변경 후에도 에러가 지속되면 1분 뒤 재실행 바랍니다. 
        버튼 연타는 에러의 원인이 되니 '한 번만' 누르고 대기해 주세요! 🚨</p>
    </div>
    """, unsafe_allow_html=True)

# 3. 고정형 핵심 가이드 (정적 안내)
st.info("💡 **안내:** 생성 버튼을 여러 번 누르면 서버 과부하로 에러가 뜰 수 있습니다. 클릭 후 로딩이 끝날 때까지 기다려 주세요.")

# 4. 시스템 엔진 설정 (Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

# 5. 사이드바 메인 메뉴
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
# 7. 기능 2: 비즈니스 격식 변환기
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
# 8. 기능 3: 콘텐츠 기획 콘티 (v6.3)
# ==========================================
elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 자유 입력형)")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1: client_name = st.text_input("업체명", value="유로진 부산점")
    with col_c2: q_count = st.slider("주제별 질문 개수", 3, 10, 6)

    st.markdown("### 🎯 주제별 상세 가이드 입력")
    st.info("각 주제에서 어떤 내용을 중점적으로 다룰지 PD님의 의도를 적어주세요.")
    
    c_t1, c_t2 = st.columns(2)
    with c_t1:
        focus1 = st.text_input("주제 1 내용 (도입)", placeholder="예: 바세린 주입의 위험성과 전조 증상")
        focus2 = st.text_input("주제 2 내용 (전개)", placeholder="예: 잘못된 민간요법에 대한 팩트체크")
    with c_t2:
        focus3 = st.text_input("주제 3 내용 (심화)", placeholder="예: 제거 수술 과정과 확대 수술 동시 진행 여부")
        focus4 = st.text_input("주제 4 내용 (마무리)", placeholder="예: 사후 관리 및 원장님의 진심어린 당부")

    uploaded_ref = st.file_uploader("레퍼런스 파일 업로드", type=["txt", "docx", "pdf"], key="conti_v6_3")
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
    else: final_ref = st.text_area("레퍼런스 직접 입력", height=150, key="conti_text_v6_3")

    if st.button("💡 맞춤형 콘티 생성"):
        if not final_ref or not client_name: st.warning("필요한 정보를 모두 입력해주세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner(random.choice(msgs_conti)):
                    prompt = f"""당신은 유튜브 콘텐츠 전략가입니다. 업체 '{client_name}'를 위한 시즌 7 스타일의 콘티를 작성하세요.
                    
                    [주제별 가이드라인]
                    - 주제 1: {focus1 if focus1 else '자유 분석'}
                    - 주제 2: {focus2 if focus2 else '자유 분석'}
                    - 주제 3: {focus3 if focus3 else '자유 분석'}
                    - 주제 4: {focus4 if focus4 else '자유 분석'}

                    [형식 규칙]
                    - 각 주제는 '주제 X. [호기심 자극 제목]'으로 시작.
                    - 제목 아래 '핵심 포인트 : [한 줄 요약]' 명시.
                    - 질문은 '#' 번호와 구어체(인터뷰 톤) 사용. 주제당 {q_count}개.
                    레퍼런스: {final_ref}"""
                    
                    response = model.generate_content(prompt)
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.write(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.balloons()
            except Exception as e: st.error(f"오류: {e}")
