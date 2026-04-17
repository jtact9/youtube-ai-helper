import streamlit as st
import google.generativeai as genai
import json

# 1. 페이지 설정
st.set_page_config(page_title="유로진 부산점 SEO 마스터 v2.5", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white; font-weight: bold; font-size: 1.1em; }
    .stTextArea textarea { font-size: 1.1em !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎥 유튜브 업로드 세팅 자동화")

# 2. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"])
    
    st.divider()
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰 수", f"{st.session_state.tokens} pts")
    
    if st.button("🔄 세션 초기화"):
        st.rerun()

# 3. 프리셋 & 템플릿 섹션
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

with st.expander("🛠️ 설명란 고정 양식 설정 (수정 시 현재 세션에 저장됨)", expanded=False):
    desc_template = st.text_area("템플릿 편집 ({summary} 위치에 AI 요약이 들어갑니다)", value=default_temp, height=350)
    fixed_tags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성성건강")

# 4. 입력 섹션
script_input = st.text_area("영상 스크립트를 입력하세요", height=300)

# 5. 실행 로직
if st.button("🚀 업로드 세팅 데이터 추출하기"):
    if not api_key or not script_input:
        st.warning("API 키와 스크립트를 모두 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner("AI가 유로진 맞춤형 데이터를 생성 중입니다..."):
                # JSON 형식을 유도하여 파싱이 가능하게 함
                prompt = f"""
                당신은 유로진남성의원 전용 유튜브 PD입니다. 스크립트를 분석해 아래 JSON 형식으로만 답변하세요.
                {{
                    "titles": ["제목1", "제목2", "제목3", "제목4", "제목5"],
                    "summary_content": "여기에 3~4줄의 핵심 요약문을 작성",
                    "tags": "키워드1, 키워드2, ...",
                    "hashtags": "#태그1 #태그2 ...",
                    "thumbnail": ["카피1", "카피2", "카피3"]
                }}
                [스크립트]: {script_input}
                """
                
                response = model.generate_content(prompt)
                
                # 결과 파싱
                raw_res = response.text.replace('```json', '').replace('```', '').strip()
                data = json.loads(raw_res)
                
                # 템플릿 치환
                final_desc = desc_template.format(summary=data['summary_content'])
                st.session_state.tokens = response.usage_metadata.total_token_count
                
                # 화면 출력
                st.success("✅ 생성이 완료되었습니다!")
                st.toast("메타데이터 추출 성공!", icon="💫")
                
                col_res1, col_res2 = st.columns([1, 1])
                
                with col_res1:
                    st.subheader("📋 복사용 설명란")
                    st.code(f"{final_desc}\n\n{fixed_tags} {data['hashtags']}", language="text")
                
                with col_res2:
                    st.subheader("💡 추천 제목 & 썸네일")
                    st.write("**추천 제목:**")
                    for t in data['titles']: st.write(f"- {t}")
                    st.write("**썸네일 카피:**")
                    for c in data['thumbnail']: st.info(c)
                    st.write("**태그:**")
                    st.caption(data['tags'])
                    
        except Exception as e:
            st.error(f"오류가 발생했습니다. AI 응답 형식이 맞지 않을 수 있으니 다시 시도해 주세요. ({e})")
