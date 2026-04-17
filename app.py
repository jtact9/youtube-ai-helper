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
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00; font-family: monospace; font-size: 1.1rem; line-height: 1.8; }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. 시스템 설정 (Secrets)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 확인하세요.")
    st.stop()

# 3. 사이드바 - 메인 메뉴 (기능 선택)
with st.sidebar:
    st.title("🛠️ 박사원의 워크벤치")
    menu = st.radio("업무 선택", ["🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.5-flash", "gemini-2.0-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# --- 랜덤 로딩 메시지 리스트 ---
msgs_yt = ["🎬 박사원이 촬영 슬레이트 치고 달려오는 중...", "✂️ 박사원이 컷편집 정밀하게 들어가는 중...", "🎨 박사원이 컬러 그레이딩 입히는 중..."]
msgs_biz = ["💼 박사원이 정장 갈아입고 명함 챙기는 중...", "☕ 박사원이 업체 미팅 전 커피 한 잔 마시는 중...", "✍️ 박사원이 맞춤법 검사기 세 번 돌리는 중..."]

# ==========================================
# 4. 기능 1: 유튜브 업로드 세팅 (기존 기능)
# ==========================================
if menu == "🎬 유튜브 업로드 세팅":
    st.title("🎬 유튜브 업로드 세팅 자동화")
    
    with st.expander("🛠️ 설명란 양식 편집", expanded=False):
        default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫\n\n{summary}\n\n📍 위치 : 부산 부산진구 부전동 257-3\n✔️ 홈페이지 : http://busan.urogyn.co.kr/"""
        desc_template = st.text_area("템플릿", value=default_template, height=200)
        fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

    uploaded_file = st.file_uploader("스크립트 파일 업로드", type=["txt", "docx", "pdf"])
    final_script = st.text_area("또는 직접 입력", height=150) if not uploaded_file else ""

    if st.button("🚀 세팅 데이터 추출하기"):
        try:
            model = genai.GenerativeModel(selected_model)
            with st.spinner(random.choice(msgs_yt)):
                prompt = f"유튜브 PD로서 다음 스크립트를 분석해. 요약은 4~5줄, 이모지 포함, 호기심 유발. 태그는 쉼표 구분 50개. 결과는 JSON으로. 스크립트: {final_script}"
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                data = json.loads(response.text)
                
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown(f'<span class="big-font">🏷️ 검색용 고밀도 태그</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="tag-box">{data.get("tags", "")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown(f'<span class="big-font">📋 최종 설명란</span>', unsafe_allow_html=True)
                final_desc = desc_template.replace("{summary}", data.get("summary_content", ""))
                st.code(f"{final_desc}\n\n{fixed_hashtags}", language="text")
                st.markdown('</div>', unsafe_allow_html=True)
                st.balloons()
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 5. 기능 2: 비즈니스 격식 변환기 (신규 기능)
# ==========================================
elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    st.write("메모장이나 카톡에 쓴 투박한 글을 정중한 업체 대응 문장으로 바꿔드립니다.")

    biz_tone = st.selectbox("변환 톤 선택", ["아주 정중하게 (이메일용)", "부드럽고 친절하게 (카톡/문자용)", "단호하고 명확하게 (공문/요청용)"])
    raw_text = st.text_area("내용을 입력하세요 (예: 낼 촬영 취소임 미안)", height=200)

    if st.button("✨ 격식 있게 변환하기"):
        if not raw_text:
            st.warning("변환할 내용을 입력해주세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner(random.choice(msgs_biz)):
                    prompt = f"""당신은 비즈니스 커뮤니케이션 전문가입니다. 
                    다음 내용을 '{biz_tone}' 톤으로 변환하세요.
                    대상은 영상 제작 협력 업체, 프리랜서 감독, 또는 인터뷰 대상자입니다.
                    작성자: 영상팀 박진성 사원
                    내용: {raw_text}
                    결과는 '제목:'과 '본문:'을 구분하여 정중하게 출력하세요."""
                    
                    response = model.generate_content(prompt)
                    
                    st.markdown('<div class="result-section">', unsafe_allow_html=True)
                    st.markdown(f'<span class="big-font">📝 변환 결과 ({biz_tone})</span>', unsafe_allow_html=True)
                    st.code(response.text, language="text")
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.audio("https://www.soundjay.com/buttons/sounds/button-10.mp3", autoplay=True)
            except Exception as e: st.error(f"오류: {e}")
