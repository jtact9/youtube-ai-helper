import streamlit as st
import google.generativeai as genai
import json
from docx import Document
import PyPDF2
import io

# 1. 페이지 인터페이스 설정 (박사원의 브랜딩 유지)
st.set_page_config(page_title="박사원의 유튜브 업로드세팅 툴", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; }
    .tag-box { 
        background-color: #1e1e1e; 
        padding: 20px; 
        border-radius: 10px; 
        border: 2px solid #00FF00; 
        color: #00FF00; 
        font-family: monospace; 
        font-size: 1.3rem; 
    }
    .big-font { font-size: 1.3rem !important; font-weight: 700; color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 박사원의 유튜브 업로드세팅 툴 (v3.5)")

# 2. 시스템 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 워크벤치 설정")
    selected_model = st.selectbox("엔진 선택", ["gemini-2.5-flash", "gemini-2.0-flash"])
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# 3. 유로진 전용 고정 템플릿
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
    desc_template = st.text_area("설명란 템플릿", value=default_template, height=350)
    fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

# 4. 파일 업로드 및 텍스트 추출 로직 (메모장 파일 강화)
st.subheader("📁 스크립트 파일 업로드")
uploaded_file = st.file_uploader("메모장(TXT), 워드(DOCX), PDF 파일을 업로드하세요", type=["txt", "docx", "pdf"])

final_script = ""

if uploaded_file is not None:
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'txt':
            # 메모장 파일 인코딩 대응 (UTF-8 시도 후 실패 시 CP949 시도)
            raw_data = uploaded_file.read()
            try:
                final_script = raw_data.decode("utf-8")
            except UnicodeDecodeError:
                final_script = raw_data.decode("cp949")
                
        elif file_type == 'docx':
            doc = Document(uploaded_file)
            final_script = "\n".join([para.text for para in doc.paragraphs])
            
        elif file_type == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text: final_script += text + "\n"
        
        st.success(f"✅ {uploaded_file.name} 파일을 성공적으로 읽었습니다.")
        with st.expander("파일 내용 확인"):
            st.write(final_script[:1000] + "..." if len(final_script) > 1000 else final_script)
            
    except Exception as e:
        st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
else:
    final_script = st.text_area("또는 여기에 스크립트를 직접 입력하세요", height=200)

# 5. 실행 로직
if st.button("✨ 세팅 데이터 추출하기"):
    if not final_script or len(final_script.strip()) == 0:
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
            
            model = genai.GenerativeModel(model_name=selected_model, generation_config=generation_config)
            
            with st.spinner("박사원의 AI 비서가 데이터를 생성 중..."):
                prompt = f"당신은 유튜브 SEO 전문가입니다. 다음 스크립트를 분석하여 문장 단위 줄바꿈이 포함된 요약과 SEO 데이터를 생성하세요: {final_script}"
                response = model.generate_content(prompt)
                data = json.loads(response.text)
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                st.divider()
                col_left, col_right = st.columns([1.1, 0.9])
                
                with col_left:
                    st.markdown('<p class="big-font">📋 유튜브 설명란 (복사용)</p>', unsafe_allow_html=True)
                    final_desc = desc_template.replace("{summary}", data['summary_content'])
                    st.code(f"{final_desc}\n\n{fixed_hashtags} {data['hashtags']}", language="text")
                
                with col_right:
                    st.markdown('<p class="big-font">💡 추천 제목</p>', unsafe_allow_html=True)
                    for t in data['titles']: st.write(f"📍 **{t}**")
                    st.divider()
                    st.markdown('<p class="big-font">🏷️ 태그 (쉼표 구분)</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="tag-box">{data["tags"]}</div>', unsafe_allow_html=True)
                    st.write("**썸네일 카피:**")
                    for c in data['thumbnail']: st.info(c)
                
                st.toast("박사원님, 파일 분석 세팅 완료!", icon="🎬")
                
        except Exception as e:
            st.error(f"시스템 오류 발생: {e}")
