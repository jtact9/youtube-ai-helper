import streamlit as st
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content

# 1. 페이지 설정
st.set_page_config(page_title="유로진 부산점 SEO 마스터 v2.6", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎥 유튜브 업로드 세팅 자동화")

# 2. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    
    # 당신의 계정에서 확인된 실존 모델로만 구성 (404 방지)
    model_options = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-pro"]
    selected_model = st.selectbox("사용 가능한 엔진 선택", model_options)
    
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰 수", f"{st.session_state.tokens} pts")

# 3. 고정 양식 설정
default_temp = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫

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
    desc_template = st.text_area("템플릿 편집", value=default_temp, height=350)
    fixed_tags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성성건강")

# 4. 입력 섹션
script_input = st.text_area("영상 스크립트를 입력하세요", height=300)

# 5. 실행 로직 (Response Schema 적용으로 JSON 오류 차단)
if st.button("🚀 업로드 세팅 데이터 추출하기"):
    if not api_key or not script_input:
        st.warning("API 키와 스크립트를 입력하세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 응답 구조 강제 정의 (AI가 반드시 이 형식으로만 답하게 함)
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
                },
            }
            
            model = genai.GenerativeModel(
                model_name=selected_model,
                generation_config=generation_config
            )
            
            with st.spinner(f"{selected_model} 엔진 가동 중..."):
                prompt = f"유튜브 PD로서 다음 스크립트를 분석하여 메타데이터를 생성하세요: {script_input}"
                response = model.generate_content(prompt)
                
                # 결과 데이터 파싱
                import json
                data = json.loads(response.text)
                
                # 템플릿 치환
                final_desc = desc_template.replace("{summary}", data['summary_content'])
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                st.success("✅ 생성이 완료되었습니다!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📋 복사용 설명란")
                    st.code(f"{final_desc}\n\n{fixed_tags} {data['hashtags']}", language="text")
                with col2:
                    st.subheader("💡 추천 제목 & 썸네일")
                    for t in data['titles']: st.write(f"📍 {t}")
                    st.divider()
                    st.write("**썸네일 카피:**")
                    for c in data['thumbnail']: st.info(c)
                    st.write("**태그(쉼표 구분):**")
                    st.caption(data['tags'])
                    
                st.toast("추출 성공!", icon="🚀")
                
        except Exception as e:
            st.error(f"시스템 오류 발생: {e}")
            st.info("API 키가 정확한지, 혹은 모델 선택이 올바른지 다시 확인해 보세요.")
