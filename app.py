import streamlit as st
import google.generativeai as genai
import json

# 1. 페이지 인터페이스 설정 (박사원의 툴로 브랜딩)
st.set_page_config(page_title="박사원의 유튜브 업로드세팅 툴", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    /* 브랜드 버튼 스타일 */
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    /* 결과물 가독성 (녹색 코딩 폰트 적용) */
    .tag-box { 
        background-color: #1e1e1e; 
        padding: 20px; 
        border-radius: 10px; 
        border: 2px solid #00FF00; 
        color: #00FF00; 
        font-family: 'Courier New', Courier, monospace; 
        font-size: 1.3rem; 
        line-height: 1.6;
    }
    .big-font { font-size: 1.3rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 메인 타이틀 변경
st.title("🚀 박사원의 유튜브 업로드세팅 툴")

# 2. 시스템 엔진 설정 (Secrets 연동)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ 설정 오류: Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

with st.sidebar:
    st.header("⚙️ 박사원의 워크벤치")
    model_options = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]
    selected_model = st.selectbox("엔진 선택", model_options)
    
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

with st.expander("🛠️ 설명란 고정 양식 설정", expanded=False):
    desc_template = st.text_area("템플릿 편집", value=default_template, height=350)
    fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

# 4. 입력 섹션
script_text = st.text_area("영상 스크립트를 여기에 넣어주세요", height=300)

# 5. 실행 로직
if st.button("✨ 세팅 데이터 추출하기"):
    if not script_text:
        st.warning("분석할 스크립트가 없습니다.")
    else:
        try:
            # 구조화된 출력 스키마
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
            
            with st.spinner("박사원의 AI 비서가 분석 중..."):
                prompt = f"당신은 전문 유튜브 PD입니다. 스크립트를 분석하여 문장 단위 줄바꿈(\\n)이 포함된 요약과 SEO 데이터를 생성하세요: {script_text}"
                response = model.generate_content(prompt)
                data = json.loads(response.text)
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                # 결과 출력
                st.success("✅ 분석이 완료되었습니다!")
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
                    
                    st.divider()
                    st.write("**썸네일 카피 추천:**")
                    for c in data['thumbnail']: st.info(c)
                
                st.toast("박사원님, 작업이 완료되었습니다!", icon="🎬")
                
        except Exception as e:
            st.error(f"시스템 오류 발생: {e}")
