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
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
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

# --- 랜덤 로딩 메시지 (박사원 일상 시리즈) ---
msgs_yt = ["🎬 박사원이 컷편집 정밀하게 들어가는 중...", "✂️ 박사원이 썸네일 카피 고뇌하는 중..."]
msgs_biz = ["💼 박사원이 정장 갈아입고 명함 챙기는 중...", "✍️ 정중한 문장으로 다듬는 중..."]
msgs_conti = ["📝 시즌 7 메커니즘으로 콘티 설계 중...", "💡 시청자가 못 박히게 만들 질문 뽑는 중...", "🔍 업체 맞춤형 핵심 포인트 분석 중..."]

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
    else: final_script = st.text_area("직접 입력", height=200)

    if st.button("🚀 데이터 추출하기"):
        if not final_script: st.warning("내용을 입력해주세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner(random.choice(msgs_yt)):
                    prompt = f"유튜브 PD로서 분석해. 요약 4~5줄, 줄바꿈 필수, 이모지 포함, 호기심 유발. 태그 쉼표 구분 50개. 결과 JSON. {final_script}"
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    data = json.loads(response.text)
                    st.session_state.tokens = response.usage_metadata.total_token_count
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                    st.code(f"{desc_template.replace('{summary}', data.get('summary_content', ''))}\n\n{fixed_hashtags}", language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 5. 기능 2: 비즈니스 격식 변환기
# ==========================================
elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    biz_tone = st.selectbox("변환 톤", ["아주 정중하게 (이메일용)", "부드럽고 친절하게 (카톡용)", "단호하고 명확하게 (공문용)"])
    raw_text = st.text_area("내용 입력", height=200)
    if st.button("✨ 변환하기"):
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner(random.choice(msgs_biz)):
                prompt = f"비즈니스 전문가로서 '영상팀 박진성 사원' 명의로 다음을 '{biz_tone}'으로 변환. {raw_text}"
                response = model.generate_content(prompt)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.code(response.text, language="text")
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 6. 기능 3: 콘텐츠 기획 콘티 (시즌 7 메커니즘 업데이트)
# ==========================================
elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 Style)")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1: client_name = st.text_input("업체명", value="유로진 부산점")
    with col_c2: q_count = st.slider("주제별 질문 개수", 3, 10, 6)

    st.markdown("### 🎯 주제별 중점 사항 설정")
    t_opts = ["정의 및 원인 분석", "오해와 진실/팩트체크", "부작용 및 방치 시 위험성", "수술/시술 과정과 원리", "수술 후 관리 및 주의사항", "전문의의 당부와 결론"]
    c_t1, c_t2, c_t3, c_t4 = st.columns(4)
    with c_t1: focus1 = st.selectbox("주제 1 중점", t_opts, index=0)
    with c_t2: focus2 = st.selectbox("주제 2 중점", t_opts, index=2)
    with c_t3: focus3 = st.selectbox("주제 3 중점", t_opts, index=3)
    with c_t4: focus4 = st.selectbox("주제 4 중점", t_opts, index=5)

    uploaded_ref = st.file_uploader("레퍼런스 파일 업로드", type=["txt", "docx", "pdf"], key="conti_up")
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

    if st.button("💡 시즌 7 스타일 콘티 생성"):
        if not final_ref: st.warning("레퍼런스 내용을 입력해주세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner(random.choice(msgs_conti)):
                    # 시즌 7 메커니즘을 이식한 고도화 프롬프트
                    prompt = f"""당신은 유튜브 콘텐츠 작가입니다. 업체 '{client_name}'의 영상을 위해 다음 [레퍼런스]를 분석하여 4개의 주제별 콘티를 작성하세요.
                    
                    [형식 규칙 - 중요!]
                    - 각 주제는 반드시 '주제 X. [호기심 자극 제목]'으로 시작할 것.
                    - 제목 아래에 '핵심 포인트 : [한 줄 요약]'을 명시할 것.
                    - 질문은 반드시 '#'으로 시작하는 번호 매기기 형식을 사용하고, 구어체(예: "원장님, ~한가요?")를 사용할 것.
                    - 질문의 개수는 주제당 {q_count}개로 고정할 것.

                    [주제별 흐름 가이드]
                    - 주제 1 (중점: {focus1}): 현상의 정의와 시청자가 겪는 초기 고민 위주.
                    - 주제 2 (중점: {focus2}): 방치했을 때의 공포나 잘못된 상식 바로잡기.
                    - 주제 3 (중점: {focus3}): 실제 해결 방법(수술/시술)의 상세 과정과 차별점.
                    - 주제 4 (중점: {focus4}): 사후 관리 및 전문의의 진정성 있는 조언.

                    [질문 작성 철학]
                    - 절대로 답변이나 결론을 미리 노출하지 말 것. 오직 '궁금함'만 유발할 것.
                    - 핵심만 짧고 굵게 짚을 것.

                    [레퍼런스]: {final_ref}"""
                    
                    response = model.generate_content(prompt)
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<span class="big-font">📝 {client_name} 시즌 7 스타일 콘티</span>', unsafe_allow_html=True)
                    st.write(response.text)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.balloons()
            except Exception as e: st.error(f"오류: {e}")
