import streamlit as st
import google.generativeai as genai
import json

# 1. 페이지 레이아웃 및 디자인 강화
st.set_page_config(page_title="유로진 부산점 SEO 마스터 v3.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    /* 버튼 스타일 */
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; border: none; }
    /* 태그/결과물 가독성 강화 */
    .big-font { font-size: 1.2rem !important; font-weight: 600; color: #FFFFFF; }
    .tag-box { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #464b5d; color: #00FF00; font-family: monospace; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 유튜브 업로드 세팅 자동화")

# 2. 시스템 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키 설정 필요 (Secrets에 GEMINI_API_KEY를 넣어주세요)")
    st.stop()

with st.sidebar:
    st.header("⚙️ 시스템 설정")
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-1.5-flash"])
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

# 3. 고정 양식 설정
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

# 4. 입력 섹션
script_text = st.text_area("영상 스크립트를 입력하세요", height=300)

if st.button("🚀 업로드 세팅 추출하기"):
    if not script_text:
        st.warning("스크립트를 입력해 주세요.")
    else:
        try:
            # AI가 줄바꿈을 포함하도록 스키마 설계
            generation_config = {
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "titles": {"type": "array", "items": {"type": "string"}},
                        "summary_content": {"type": "string"}, # 여기에 줄바꿈 포함 지시
                        "tags": {"type": "string"},
                        "hashtags": {"type": "string"},
                        "thumbnail": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["titles", "summary_content", "tags", "hashtags", "thumbnail"]
                }
            }
            
            model = genai.GenerativeModel(model_name=selected_model, generation_config=generation_config)
            
            with st.spinner("가독성 높은 결과물을 생성 중입니다..."):
                # 프롬프트에 줄바꿈 명령 강화
                prompt = f"""당신은 유튜브 SEO 전문가입니다. 
                다음 스크립트를 분석하여 정보를 추출하되, 'summary_content'는 읽기 편하게 반드시 문장 단위로 줄바꿈(\\n)을 넣어서 작성하세요.
                [스크립트]: {script_text}"""
                
                response = model.generate_content(prompt)
                data = json.loads(response.text)
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                # 결과 출력
                st.success("✅ 분석 완료!")
                st.divider()
                
                col_left, col_right = st.columns([1.2, 0.8])
                
                with col_left:
                    st.markdown('<p class="big-font">📋 복사용 설명란 (줄바꿈 적용됨)</p>', unsafe_allow_html=True)
                    # 실제 줄바꿈을 반영하여 조립
                    final_desc = desc_template.replace("{summary}", data['summary_content'])
                    st.code(f"{final_desc}\n\n{fixed_hashtags} {data['hashtags']}", language="text")
                
                with col_right:
                    st.markdown('<p class="big-font">💡 추천 제목</p>', unsafe_allow_html=True)
                    for t in data['titles']: st.write(f"📍 **{t}**")
                    
                    st.divider()
                    st.markdown('<p class="big-font">🏷️ 태그 (복사용)</p>', unsafe_allow_html=True)
                    # 가독성 좋게 박스 형태로 출력
                    st.markdown(f'<div class="tag-box">{data["tags"]}</div>', unsafe_allow_html=True)
                    
                    st.divider()
                    st.write("**썸네일 카피:**")
                    for c in data['thumbnail']: st.info(c)
                    
                st.toast("가독성 개선 버전 추출 성공!", icon="✨")
                
        except Exception as e:
            st.error(f"구동 중 오류 발생: {e}")
