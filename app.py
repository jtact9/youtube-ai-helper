import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import io

# 1. 페이지 브랜딩 및 디자인 설정
st.set_page_config(page_title="박사원의 유튜브 업로드세팅 툴", layout="wide", page_icon="🎬")

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
        font-size: 1.3rem; 
        margin-bottom: 20px;
    }
    .big-font { font-size: 1.4rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 15px; display: block; }
    .result-section { background-color: #161b22; padding: 25px; border-radius: 15px; margin-top: 20px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 박사원의 유튜브 업로드세팅 툴")

# 2. 엔진 설정 (Secrets 활용)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 박사원의 워크벤치")
    model_options = ["gemini-2.5-flash", "gemini-2.0-flash"]
    selected_model = st.selectbox("엔진 선택", model_options)
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# 3. 유로진 부산점 고정 템플릿
default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫

{summary}

유로진남성의원 부산점은 단순한 진료를 넘어,
남성의 자신감과 삶의 질을 회복하도록 돕는 전문 클리닉입니다.
비뇨기 질환부터 남성 성 건강까지, 믿을 수 있는 의료진이 함께합니다.

📩 궁금한 점이나 상담이 필요하다면 댓글로 남겨주세요.
➡️ 유로진남성의 부산점에서 직접 답변드립니다.

📍 위치 : 부산 부산진구 부전동 257-3
✔️ 홈페이지 : http://busan.urogyn.co.kr/
✔️ 블로그 : https://blog.naver.com/kumhot_22
✔️ 카카오톡 상담하기 : https://pf.kakao.com/_BjZTxd"""

with st.expander("🛠️ 설명란 고정 양식 및 프리셋", expanded=False):
    desc_template = st.text_area("템플릿 편집", value=default_template, height=350)
    fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

# 4. 입력 섹션
st.subheader("📁 스크립트 불러오기")
uploaded_file = st.file_uploader("메모장(TXT), 워드, PDF 지원", type=["txt", "docx", "pdf"])

final_script = ""

if uploaded_file is not None:
    try:
        ftype = uploaded_file.name.split('.')[-1].lower()
        if ftype == 'txt':
            raw = uploaded_file.read()
            try:
                final_script = raw.decode("utf-8")
            except:
                final_script = raw.decode("cp949")
        elif ftype == 'docx':
            doc = Document(uploaded_file)
            final_script = "\n".join([p.text for p in doc.paragraphs])
        elif ftype == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for p in pdf_reader.pages:
                txt = p.extract_text()
                if txt: final_script += txt + "\n"
        st.success(f"✅ {uploaded_file.name} 로드 완료")
    except Exception as e:
        st.error(f"파일 읽기 실패: {e}")
else:
    final_script = st.text_area("직접 입력", height=200, placeholder="여기에 내용을 입력하거나 파일을 드래그하세요.")

# 5. 실행 및 결과 출력
if st.button("✨ 세팅 데이터 추출하기"):
    if not final_script:
        st.warning("분석할 스크립트 내용이 없습니다.")
    else:
        try:
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "titles": {"type": "array", "items": {"type": "string"}},
                        "summary_content": {"type": "string"},
                        "tags": {"type": "string"},
                        "hashtags": {"type": "string"},
                        "thumbnail": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["titles", "summary_content", "tags", "hashtags", "thumbnail"]
                }
            }
            model = genai.GenerativeModel(selected_model, generation_config=generation_config)
            
            with st.spinner("박사원의 AI 비서가 분석 중..."):
                prompt = f"당신은 전문 유튜브 PD입니다. 스크립트를 분석하여 줄바꿈이 포함된 요약과 SEO 데이터를 생성하세요: {final_script}"
                response = model.generate_content(prompt)
                data = json.loads(response.text)
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                st.success("✅ 분석 완료! 아래에서 결과를 확인하세요.")
                
                # 결과 출력 섹션 (세로형 배치)
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown('<span class="big-font">💡 추천 제목 리스트</span>', unsafe_allow_html=True)
                    for t in data['titles']: st.write(f"📍 **{t}**")
                with c2:
                    st.markdown('<span class="big-font">🖼️ 썸네일 카피</span>', unsafe_allow_html=True)
                    for c in data['thumbnail']: st.info(c)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown('<span class="big-font">🏷️ 검색용 태그 (쉼표 구분)</span>', unsafe_allow_html=True)
                tag_content = data["tags"]
                st.markdown(f'<div class="tag-box">{tag_content}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                st.markdown('<span class="big-font">📋 최종 설명란 (복사용)</span>', unsafe_allow_html=True)
                final_sum = data['summary_content']
                final_desc = desc_template.replace("{summary}", final_sum)
                st.code(f"{final_desc}\n\n{fixed_hashtags} {data['hashtags']}", language="text")
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.toast("박사원님, 분석이 완벽하게 끝났습니다!", icon="🎬")

        except Exception as e:
            st.error(f"시스템 오류 발생: {e}")
