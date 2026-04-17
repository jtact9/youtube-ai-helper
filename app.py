import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="유튜브 PD 전용 툴", layout="wide")
st.title("🎬 유튜브 업로드 세팅 자동화")

with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    
    # [디버그 기능] 현재 사용 가능한 모델 목록 확인 버튼
    if st.button("사용 가능 모델 목록 확인"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                st.write(models)
            except Exception as e:
                st.error(f"목록 확인 실패: {e}")
        else:
            st.warning("API 키를 먼저 입력하세요.")

script_text = st.text_area("영상 스크립트를 입력하세요", height=400)

if st.button("🚀 메타데이터 생성 시작"):
    if not api_key:
        st.error("API 키가 없습니다.")
    elif not script_text:
        st.warning("스크립트를 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            
            # 가장 범용적인 모델명 3개를 순차적으로 시도 (Fallback 전략)
            success = False
            for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']:
                try:
                    model = genai.GenerativeModel(model_name)
                    # 테스트 호출 (짧게)
                    test_res = model.generate_content("test")
                    success = True
                    target_model = model_name
                    break
                except:
                    continue
            
            if not success:
                st.error("현재 계정으로 사용 가능한 Gemini 모델을 찾을 수 없습니다. API 키를 다시 확인하거나 '모델 목록 확인' 버튼을 눌러보세요.")
            else:
                with st.spinner(f"{target_model} 모델로 분석 중..."):
                    prompt = f"""
                    당신은 유튜브 SEO 전문가입니다. 아래 스크립트를 분석하여 다음을 작성하세요.
                    1. 추천 제목 5개
                    2. 설명란 요약 (3-4줄)
                    3. 쉼표 구분 태그 20개
                    4. # 해시태그 10개
                    5. 썸네일 카피 3개
                    
                    [스크립트]
                    {script_text}
                    """
                    response = model.generate_content(prompt)
                    st.success(f"분석 완료! (사용 모델: {target_model})")
                    st.markdown("---")
                    st.markdown(response.text)
                    
        except Exception as e:
            st.error(f"오류 발생: {e}")
