import streamlit as st
import google.generativeai as genai

# 1. 페이지 레이아웃 및 스타일 설정
st.set_page_config(page_title="유튜브 PD 전용 SEO 툴 v2.1", layout="wide")

# CSS를 활용한 디자인 (오타 수정됨: unsafe_allow_html=True)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 유튜브 업로드 세팅 자동화")

# 2. 사이드바: 설정 및 정보
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    
    # 모델 선택 (당신의 계정에서 확인된 리스트 반영)
    model_list = [
        "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", 
        "gemini-1.5-pro", "gemini-pro"
    ]
    selected_model_name = st.selectbox("사용할 모델 버전 선택", model_list)
    
    st.divider()
    
    # 프리셋 버튼 및 팝업(Toast)
    if st.button("📋 프리셋 불러오기"):
        st.toast("기본 프리셋이 하단에 적용되었습니다!", icon="✅")
    
    st.divider()
    
    # 토큰 사용량 정보 표시
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0
    
    st.metric(label="마지막 작업 사용 토큰", value=f"{st.session_state.total_tokens} tokens")
    st.caption("※ Gemini는 요청마다 사용된 토큰을 계산해 보여줍니다.")

# 3. 메인 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400, placeholder="여기에 스크립트 전체 내용을 붙여넣으세요.")

# 4. 실행 로직
if st.button("🚀 메타데이터 생성 시작"):
    if not api_key:
        st.error("API 키를 입력해 주세요.")
    elif not script_text:
        st.warning("스크립트 내용을 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model_name)
            
            with st.spinner(f"{selected_model_name} 모델이 분석 중입니다..."):
                prompt = f"""
                당신은 유튜브 SEO 및 마케팅 전문가입니다. 
                제공된 [스크립트]를 바탕으로 시청자의 클릭을 유도하고 검색 노출에 최적화된 데이터를 작성하세요.

                1. **추천 제목 리스트**: 클릭률(CTR)이 높을 법한 제목 5개
                2. **설명란 (Description)**: 영상 핵심 내용 요약 및 시청 유도 문구 (3~4줄)
                3. **쉼표 구분 태그**: 검색용 키워드 20개 (쉼표로 구분, # 없음)
                4. **해시태그 10개**: 영상 설명란 하단용 (# 포함)
                5. **썸네일 카피**: 이미지에 들어갈 강렬한 문구 3개

                [스크립트]
                {script_text}
                """
                
                response = model.generate_content(prompt)
                
                # 사용된 토큰 계산 및 저장
                if response.usage_metadata:
                    st.session_state.total_tokens = response.usage_metadata.total_token_count
                
                st.success("✅ 생성이 완료되었습니다!")
                st.markdown("---")
                st.markdown(response.text)
                
                # 작업 완료 토스트 팝업 (하단에 노출됨)
                st.toast(f"분석 완료! {st.session_state.total_tokens} 토큰 사용.", icon="🚀")
                
        except Exception as e:
            st.error(f"구동 중 오류가 발생했습니다: {e}")
