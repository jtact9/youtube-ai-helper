import streamlit as st
import google.generativeai as genai

# 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 메타데이터 생성기", layout="wide")

st.title("🎬 유튜브 업로드 세팅 자동화")
st.info("영상 스크립트를 입력하면 제목, 설명, 태그를 자동으로 생성합니다.")

# 사이드바에서 API 키 입력
with st.sidebar:
    st.header("설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.caption("발급받은 API 키를 넣어야 작동합니다.")

# 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400, placeholder="여기에 스크립트 전체 내용을 붙여넣으세요.")

if st.button("🚀 메타데이터 생성 시작"):
    if not api_key:
        st.error("API 키가 없습니다. 사이드바에 입력해 주세요.")
    elif not script_text:
        st.warning("스크립트를 입력해 주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            
            prompt = f"""
            당신은 전문 유튜브 PD이자 마케터입니다. 아래 제공되는 [영상 스크립트]를 정밀 분석하여 다음 요청사항에 맞춰 답변하세요.

            1. **추천 제목 리스트**: 클릭률(CTR)이 높을 법한 제목 5개를 리스트 형태로 제시하세요.
            2. **설명란 (Description)**: 영상의 핵심 내용을 요약하고 시청을 유도하는 3-4줄의 문구를 작성하세요.
            3. **쉼표 구분 태그**: 유튜브 백엔드 태그용 단축어 20개를 쉼표(,)로 구분하여 한 줄로 나열하세요. (# 없이 단어만)
            4. **해시태그 10개**: 영상 설명란 하단에 넣을 핵심 키워드 10개를 #를 붙여서 작성하세요.
            5. **썸네일 제목 추천**: 썸네일 이미지에 크게 들어갈 임팩트 있는 짧은 카피 3가지를 추천하세요.

            [영상 스크립트]
            {script_text}
            """
            
            with st.spinner("제미나이가 스크립트를 분석 중입니다..."):
                response = model.generate_content(prompt)
                
                st.success("분석 완료!")
                st.markdown("---")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
