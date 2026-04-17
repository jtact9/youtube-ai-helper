import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 SEO 툴", layout="wide")
st.title("🎬 유튜브 업로드 세팅 자동화 (v2.0)")

# 2. 사이드바 설정
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.info("현재 Gemini 2.0 Flash 모델을 사용하도록 설정되어 있습니다.")

# 3. 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400, placeholder="여기에 스크립트 전체 내용을 붙여넣으세요.")

# 4. 생성 로직
if st.button("🚀 메타데이터 생성 시작"):
    if not api_key:
        st.error("API 키를 입력해 주세요.")
    elif not script_text:
        st.warning("스크립트 내용을 입력해 주세요.")
    else:
        try:
            # API 설정
            genai.configure(api_key=api_key)
            
            # 확인된 리스트 중 가장 최적화된 모델 선택
            # 'models/' 접두사를 제외한 순수 모델명을 사용합니다.
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner("최신 Gemini 2.0 AI가 스크립트를 정밀 분석 중입니다..."):
                prompt = f"""
                당신은 유튜브 SEO 및 마케팅 전문가입니다. 
                제공된 [스크립트]를 바탕으로 시청자의 클릭을 유도하고 검색 노출에 최적화된 데이터를 작성하세요.

                1. **추천 제목 리스트**: 호기심을 자극하는 제목 5개
                2. **설명란 (Description)**: 영상 핵심 내용 요약 및 시청 유도 문구 (3~4줄)
                3. **쉼표 구분 태그**: 검색용 키워드 20개 (쉼표로 구분, # 없음)
                4. **해시태그 10개**: 설명란 하단용 (# 포함)
                5. **썸네일 카피**: 이미지에 들어갈 강렬한 문구 3개

                [스크립트]
                {script_text}
                """
                
                response = model.generate_content(prompt)
                
                st.success("✅ 생성이 완료되었습니다!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            # 에러 발생 시 상세 메시지 출력
            st.error(f"구동 중 오류가 발생했습니다: {e}")
            st.info("만약 모델 인식 문제라면 'gemini-2.0-flash' 대신 리스트에 있던 다른 명칭을 시도해야 합니다.")
