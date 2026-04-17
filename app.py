import streamlit as st
import google.generativeai as genai

# 1. 페이지 레이아웃 및 스타일 설정
st.set_page_config(page_title="유튜브 PD 전용 SEO 툴 v2.2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stButton>button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 유튜브 업로드 세팅 자동화")

# 2. 사이드바: 설정 및 정보
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key", type="password")
    
    model_list = [
        "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", 
        "gemini-1.5-pro", "gemini-pro"
    ]
    selected_model_name = st.selectbox("사용할 모델 버전 선택", model_list)
    
    st.divider()
    
    # 토큰 사용량 정보
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0
    st.metric(label="마지막 작업 사용 토큰", value=f"{st.session_state.total_tokens} tokens")
    
    st.divider()
    if st.button("📋 프리셋 데이터 적용 확인"):
        st.toast("현재 설정된 프리셋이 반영되었습니다!", icon="✅")

# 3. 프리셋 설정 섹션 (새로 추가됨)
with st.expander("🛠️ 채널별 프리셋 설정 (여기를 열어 고정 문구 등을 수정하세요)"):
    col1, col2 = st.columns(2)
    with col1:
        fixed_hashtags = st.text_input("고정 해시태그", value="#PD박진성 #영상편집 #유튜브성장")
        channel_tone = st.selectbox("말투(톤앤매너)", ["친절하고 전문적인", "유머러스하고 재치있는", "간결하고 명확한", "자극적이고 호기심 많은"])
    with col2:
        custom_instruction = st.text_area("추가 지시사항 (예: 특정 단어 금지 등)", value="전문 용어는 쉬운 단어로 풀어서 설명해줘.")

# 4. 메인 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=300, placeholder="여기에 스크립트 전체 내용을 붙여넣으세요.")

# 5. 실행 로직
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
                # 프리셋 정보가 포함된 강화된 프롬프트
                prompt = f"""
                당신은 유튜브 SEO 전문가입니다. 다음 [스크립트]를 바탕으로 시청자를 사로잡을 데이터를 작성하세요.
                
                [채널 설정 프리셋]
                - 말투: {channel_tone}
                - 고정 해시태그 포함: {fixed_hashtags}
                - 추가 가이드: {custom_instruction}

                [요청 사항]
                1. 추천 제목 리스트: 클릭률(CTR)이 높은 제목 5개
                2. 설명란 (Description): 핵심 요약 및 시청 유도 (3~4줄)
                3. 쉼표 구분 태그: 검색 키워드 20개 (쉼표 구분)
                4. 해시태그 10개: 고정 해시태그를 포함하여 총 10개 생성
                5. 썸네일 카피: 강렬한 문구 3개

                [스크립트]
                {script_text}
                """
                
                response = model.generate_content(prompt)
                
                if response.usage_metadata:
                    st.session_state.total_tokens = response.usage_metadata.total_token_count
                
                st.success("✅ 생성이 완료되었습니다!")
                st.markdown("---")
                st.markdown(response.text)
                
                # 좌하단 팝업 효과
                st.toast(f"분석 완료! {st.session_state.total_tokens} 토큰 사용.", icon="🚀")
                
        except Exception as e:
            st.error(f"구동 중 오류 발생: {e}")
