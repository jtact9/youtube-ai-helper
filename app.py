import streamlit as st
import google.generativeai as genai
import json

# 1. 페이지 인터페이스 설정
st.set_page_config(page_title="유로진 부산점 SEO 마스터 v3.0", layout="wide")

# 디자인 테마 설정
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; font-size: 1.1em; border: none; }
    .stButton>button:hover { background-color: #C0392B; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 징성씨의 유튜브 업로드세팅 툴")

# 2. 시스템 엔진 설정 (Streamlit Secrets 활용)
try:
    # 시스템 금고에서 키를 자동으로 불러옵니다.
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API 키가 설정되지 않았습니다. Streamlit Cloud의 Settings > Secrets에서 GEMINI_API_KEY를 설정해주세요.")
    st.stop()

# 사이드바: 통계 및 설정
with st.sidebar:
    st.header("⚙️ 시스템 정보")
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"])
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")
    st.caption("※ 모든 데이터는 5인 팀 공용 할당량 내에서 처리됩니다.")

# 3. 유로진 전용 고정 템플릿 (기본값 박제)
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

with st.expander("🛠️ 설명란 고정 양식 및 프리셋 (필요 시 수정)", expanded=False):
    desc_template = st.text_area("설명란 템플릿 ({summary} 자리에 요약이 들어갑니다)", value=default_template, height=350)
    fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

# 4. 메인 워크플로우
script_text = st.text_area("영상 스크립트를 입력하세요", height=300, placeholder="여기에 스크립트 내용을 붙여넣으세요.")

if st.button("🚀 업로드 세팅 추출하기"):
    if not script_text:
        st.warning("스크립트를 입력해 주세요.")
    else:
        try:
            # 구조화된 출력(JSON) 설정
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
            
            with st.spinner("전문 PD AI가 분석 중입니다..."):
                prompt = f"당신은 유튜브 SEO 전문가입니다. 다음 스크립트를 분석하여 정보를 추출하세요: {script_text}"
                response = model.generate_content(prompt)
                
                # 결과 파싱
                data = json.loads(response.text)
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                # 템플릿 조립
                final_description = desc_template.replace("{summary}", data['summary_content'])
                
                st.success("✅ 분석 완료!")
                st.toast("데이터 추출 성공!", icon="🚀")
                
                # 결과 출력 섹션
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("📋 설명란 복사")
                    st.code(f"{final_description}\n\n{fixed_hashtags} {data['hashtags']}", language="text")
                
                with col_right:
                    st.subheader("💡 추천 제목")
                    for t in data['titles']: st.write(f"📍 {t}")
                    st.divider()
                    st.write("**썸네일 카피:**")
                    for c in data['thumbnail']: st.info(c)
                    st.write("**태그(쉼표 구분):**")
                    st.caption(data['tags'])
                    
        except Exception as e:
            st.error(f"구동 중 오류 발생: {e}")
