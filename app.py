import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import random # 랜덤 기능을 위해 추가

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="박사원의 유튜브 업로드세팅 툴", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 박사원의 유튜브 업로드세팅 툴 (v4.6)")

# 2. 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 확인하세요.")
    st.stop()

# 3. 사이드바
with st.sidebar:
    st.header("⚙️ 박사원의 워크벤치")
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# 4. 고정 템플릿
default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫

{summary}

유로진남성의원 부산점은 단순한 진료를 넘어,
남성의 자신감과 삶의 질을 회복하도록 돕는 전문 클리닉입니다.

📍 위치 : 부산 부산진구 부전동 257-3
✔️ 홈페이지 : http://busan.urogyn.co.kr/
✔️ 블로그 : https://blog.naver.com/kumhot_22
✔️ 카카오톡 상담하기 : https://pf.kakao.com/_BjZTxd"""

with st.expander("🛠️ 설명란 양식 편집", expanded=False):
    desc_template = st.text_area("템플릿", value=default_template, height=300)
    fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

# 5. 입력 섹션
uploaded_file = st.file_uploader("스크립트 파일 업로드", type=["txt", "docx", "pdf"])
final_script = ""

if uploaded_file:
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
else:
    final_script = st.text_area("직접 입력", height=200)

# 6. 실행 및 랜덤 로딩 로직
if st.button("✨ 세팅 데이터 추출하기"):
    if not final_script:
        st.warning("내용을 입력해주세요.")
    else:
        # 랜덤 메시지 리스트
        msgs = [
            "🔍 박사원이 카메라 렌즈 먼지 한 땀 한 땀 닦는 중...",
            "✂️ 박사원이 지식포털 컷편집 정밀하게 들어가는 중...",
            "⚙️ 박사원이 프리미어 프로 렌더링 게이지 채우는 중...",
            "💾 박사원이 촬영본 백업하느라 외장하드랑 싸우는 중...",
            "🎭 박사원이 영상 속 원장님 모자이크 꼼꼼하게 입히는 중...",
            "✍️ 박사원이 썸네일 클릭률 높일 문구 고뇌하는 중...",
            "🎬 박사원이 촬영 현장 슬레이트 치고 달려오는 중...",
            "🎧 박사원이 오디오 노이즈 잡으려고 숨죽여 듣는 중...",
            "🎨 박사원이 컬러 그레이딩으로 영상 색깔 입히는 중...",
            "👀 박사원이 자막 오타 없나 눈 크게 뜨고 검수 중...",
            "🏃 박사원이 시즌6 촬영 장소 섭외하러 뛰어다니는 중...",
            "☀️ 박사원이 화이트 밸런스 안 맞아서 쩔쩔매는 중...",
            "🙏 박사원이 유튜브 알고리즘 신에게 기도 올리는 중...",
            "🎵 박사원이 배경음악 고르느라 100번째 곡 감상 중...",
            "🥪 박사원이 촬영 감독님 간식 챙겨드리고 오는 중...",
            "⏳ 박사원이 인코딩 끝날 때까지 모니터 멍하니 보는 중...",
            "❄️ 박사원이 프록시 만드느라 과열된 컴퓨터 식히는 중...",
            "📏 박사원이 원고랑 영상 싱크 자로 재듯 맞추는 중...",
            "✨ 박사원이 화려한 트랜지션 넣을까 말까 고민 중...",
            "🚀 박사원이 업로드 버튼 누르기 직전 심호흡 중..."
        ]
        
        try:
            model = genai.GenerativeModel(selected_model)
            # 랜덤 메시지 선택하여 스피너 실행
            with st.spinner(random.choice(msgs)):
                prompt = f"""유튜브 PD로서 다음 스크립트를 분석해. 
                1. 요약(summary_content)은 4~5줄, 이모지 포함, 호기심 유발.
                2. 태그(tags)는 약 50개, 쉼표 구분, 500자 이내.
                결과는 JSON으로 줘. {final_script}"""
                
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                data = json.loads(response.text)
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                # 결과 레이아웃
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown(f'<span class="big-font">🏷️ 검색용 고밀도 태그</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown(f'<span class="big-font">📋 최종 설명란</span>', unsafe_allow_html=True)
                final_desc = desc_template.replace("{summary}", data.get("summary_content", ""))
                st.code(f"{final_desc}\n\n{fixed_hashtags}", language="text")
                st.markdown('</div>', unsafe_allow_html=True)
                st.toast("박사원님, 작업 완료!")
        except Exception as e:
            st.error(f"오류: {e}")
