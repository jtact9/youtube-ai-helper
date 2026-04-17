import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 SEO 툴 v2.5", layout="wide")
st.title("🎬 유튜브 업로드 세팅 자동화 (프리셋 모드)")

# 2. 채널별 프리셋 데이터 정의 (여기에 채널을 추가/수정하세요)
CHANNEL_PRESETS = {
    "기본 설정": "일반적인 유튜브 시청자에게 매력적인 톤으로 작성하세요.",
    "의학/전문가 채널": "신뢰감 있고 전문적인 용어를 사용하되, 시청자가 이해하기 쉽게 설명하세요. 권위 있는 톤을 유지하세요.",
    "예능/브이로그": "유머러스하고 트렌디한 신조어를 적절히 섞어 활기찬 톤으로 작성하세요.",
    "교육/정보 전달": "체계적이고 명확한 구조로 정보를 요약하고 학습 의욕을 고취시키는 톤으로 작성하세요."
}

# 3. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    
    st.divider()
    
    # 채널 프리셋 선택
    selected_channel = st.selectbox("📺 대상 채널 선택", list(CHANNEL_PRESETS.keys()))
    channel_context = CHANNEL_PRESETS[selected_channel]
    
    # 모델 선택 (이전 리스트 기반)
    available_models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
    selected_model = st.selectbox("🤖 AI 모델 선택", available_models)
    
    st.info(f"선택된 프리셋: {selected_channel}")

# 4. 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400)

# 5. 생성 로직
if st.button("🚀 프리셋 기반 메타데이터 생성"):
    if not api_key:
        st.error("API 키를 입력해 주세요.")
    elif not script_text:
        st.warning("스크립트 내용을 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner(f"[{selected_channel}] 스타일로 분석 중..."):
                # 강화된 프롬프트
                prompt = f"""
                당신은 유튜브 SEO 및 마케팅 전문가입니다. 
                다음 지침에 따라 제공된 [스크립트]를 분석하여 데이터를 작성하세요.

                [채널 성격 및 톤앤매너]
                {channel_context}

                [요구사항]
                1. **추천 제목 리스트**: 클릭률(CTR)을 극대화할 수 있는 제목 5개
                2. **설명란 (Description)**: 영상 핵심 내용 요약 및 시청 유도 문구 (3~4줄)
                3. **쉼표 구분 태그 (50개)**: 검색 노출을 위해 영상과 관련된 키워드 50개를 쉼표(,)로만 구분하여 작성하세요. 중복을 피하고 광범위한 키워드와 세부 키워드를 섞으세요.
                4. **해시태그 10개**: 설명란 하단용 (# 포함)
                5. **썸네일 카피**: 이미지에 들어갈 강렬한 문구 3개

                [스크립트]
                {script_text}
                """
                
                response = model.generate_content(prompt)
                
                st.success(f"✅ {selected_channel} 맞춤형 생성 완료!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            if "429" in str(e):
                st.error("🚨 할당량 초과(429): 모델을 바꾸거나 1분 뒤에 시도하세요.")
            else:
                st.error(f"오류 발생: {e}")
