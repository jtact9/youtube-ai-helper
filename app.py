import streamlit as st
import google.generativeai as genai

# 1. 페이지 레이아웃 설정
st.set_page_config(page_title="유튜브 PD 전용 SEO 툴 v2.1", layout="wide")

# UI 스타일 개선 (팝업 위치 및 디자인)
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    </style>
    """, unsafe_allow_name=True)

st.title("🎬 유튜브 업로드 세팅 자동화")

# 2. 사이드바: 설정 및 정보
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    
    # 모델 선택 칸 복구 (리스트 기반)
    model_list = [
        "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", 
        "gemini-1.5-pro", "gemini-pro"
    ]
    selected_model_name = st.selectbox("사용할 모델 버전 선택", model_list)
    
    st.divider()
    
    # 프리셋 버튼 및 팝업(Toast)
    if st.button("📋 프리셋 불러오기"):
        # Streamlit의 toast는 기본적으로 우측 하단에 뜨지만, 
        # 가장 깔끔한 UX를 제공하는 표준 방식이다.
        st.toast("기본 프리셋이 적용되었습니다!", icon="✅")
    
    st.divider()
    
    # 토큰 정보 표시 (세션 상태 활용)
    if 'last_tokens' not in st.session_state:
        st.session_state.last_tokens = 0
    
    st.metric(label="마지막 작업 사용 토큰", value=f"{st.session_state.last_tokens} tokens")
    st.caption("※ Gemini 무료 티어는 분당 토큰 제한(TPM)이 있으니 주의하세요.")

# 3. 메인 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400, placeholder="여기에 스크립트를 붙여넣으세요.")

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
            
            # 토큰 계산 (사전 확인)
            input_tokens = model.count_tokens(script_text).total_tokens
            
            with st.spinner(f"{selected_model_name} 분석 중..."):
                prompt = f"""
                당신은 유튜브 SEO 전문가입니다. 
                다음 [스크립트]를 바탕으로 시청자를 사로잡을 데이터를 작성하세요.

                1. **추천 제목 리스트**: 클릭률 높은 제목 5개
                2. **설명란 (Description)**: 핵심 요약 및 시청 유도 (3~4줄)
                3. **쉼표 구분 태그**: 검색 키워드 20개 (쉼표 구분)
                4. **해시태그 10개**: # 포함
                5. **썸네일 카피**: 이미지용 강렬한 문구 3개

                [스크립트]
                {script_text}
                """
                
                response = model.generate_content(prompt)
                
                # 사용량 데이터 추출 및 세션 저장
                # response.usage_metadata를 통해 실제 소비된 토큰 확인 가능
                total_tokens = response.usage_metadata.total_token_count
                st.session_state.last_tokens = total_tokens
                
                st.success("✅ 생성 완료!")
                st.markdown("---")
                st.markdown(response.text)
                
                # 작업 완료 팝업
                st.toast(f"분석 완료! 총 {total_tokens} 토큰이 사용되었습니다.", icon="🚀")
                
        except Exception as e:
            st.error(f"오류 발생: {e}")
