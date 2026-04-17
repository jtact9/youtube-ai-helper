import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 SEO 툴 v2.1", layout="wide")
st.title("🎬 유튜브 업로드 세팅 자동화")

# 2. 사이드바 설정 (모델 선택 기능 추가)
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    
    # 당신의 계정에서 확인된 사용 가능 모델 리스트
    available_models = [
        "gemini-2.0-flash", 
        "gemini-2.5-flash", 
        "gemini-flash-latest", 
        "gemini-2.0-flash-lite"
    ]
    selected_model = st.selectbox("사용할 AI 모델 선택", available_models)
    
    st.info(f"선택된 모델: {selected_model}")
    st.caption("팁: 한 모델에서 할당량 초과(429)가 나면 다른 모델로 바꿔보세요.")

# 3. 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400)

# 4. 생성 로직
if st.button("🚀 메타데이터 생성 시작"):
    if not api_key:
        st.error("API 키를 입력해 주세요.")
    elif not script_text:
        st.warning("스크립트 내용을 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 선택한 모델로 호출
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner(f"{selected_model} 모델이 분석 중입니다..."):
                prompt = f"""
                당신은 유튜브 SEO 전문가입니다. 아래 스크립트로 제목 5개, 설명란, 태그 20개, 해시태그 10개, 썸네일 카피 3개를 작성하세요.
                결과는 한국어로 출력하세요.

                [스크립트]
                {script_text}
                """
                response = model.generate_content(prompt)
                
                st.success("✅ 생성 완료!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            if "429" in str(e):
                st.error("🚨 할당량 초과(429): 현재 모델의 무료 사용량을 다 썼습니다. 왼쪽 사이드바에서 모델을 다른 것으로 바꿔서 시도해보세요.")
            elif "404" in str(e):
                st.error("🚨 모델 없음(404): 선택한 모델명이 정확하지 않습니다. 리스트에 있는 다른 모델을 선택하세요.")
            else:
                st.error(f"오류 발생: {e}")
