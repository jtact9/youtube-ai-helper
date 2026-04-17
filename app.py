import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 툴 v3.0", layout="wide")
st.title("🎬 유튜브 업로드 자동화 v3.0 (템플릿 엔진)")

# 2. 채널별 프리셋 및 고정 설명란 포맷 정의
# {summary} 라고 적힌 부분에 AI가 쓴 요약문이 들어갑니다.
CHANNEL_PRESETS = {
    "유로진 남성의원 부산점": {
        "context": "의학 전문 채널. 신뢰감 있고 전문적인 톤.",
        "template": """안녕하세요! 유로진 남성의원 부산점입니다.
        
{summary}

📍 위치: 부산광역시 OO구 OO로 123
📞 상담문의: 051-XXX-XXXX
🌐 홈페이지: http://example.com
✨ 구독과 좋아요는 원장님에게 큰 힘이 됩니다!"""
    },
    "꿈찾사 (교도관 채널)": {
        "context": "인생 이야기와 직업관을 다루는 진정성 있는 톤.",
        "template": """꿈을 찾는 사람들, 꿈찾사입니다. 오늘 영상의 핵심 요약입니다.

{summary}

✉️ 출연/협업 문의: dream@example.com
📸 인스타그램: @dream_searcher
오늘도 당신의 꿈을 응원합니다."""
    },
    "일반 설정 (기본)": {
        "context": "일반적인 유튜브 채널 톤앤매너.",
        "template": """영상을 시청해주셔서 감사합니다!

{summary}

#구독 #좋아요 #알림설정"""
    }
}

# 3. 사이드바 설정
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    st.divider()
    
    # 채널 프리셋 선택
    selected_channel_name = st.selectbox("📺 대상 채널 선택", list(CHANNEL_PRESETS.keys()))
    current_preset = CHANNEL_PRESETS[selected_channel_name]
    
    # 모델 선택
    available_models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
    selected_model = st.selectbox("🤖 AI 모델 선택", available_models)

# 4. 메인 화면 - 입력창
script_text = st.text_area("영상 스크립트를 입력하세요", height=400)

# 5. 생성 및 출력 로직
if st.button("🚀 템플릿 기반 데이터 생성"):
    if not api_key:
        st.error("API 키를 입력하세요.")
    elif not script_text:
        st.warning("스크립트를 입력하세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner(f"[{selected_channel_name}] 포맷에 맞춰 제작 중..."):
                prompt = f"""
                당신은 유튜브 마케팅 전문가입니다. 
                다음 [채널 성격]을 반영하여 [스크립트]를 분석하고 데이터를 작성하세요.

                [채널 성격]
                {current_preset['context']}

                [요구사항]
                1. 추천 제목 리스트: 클릭 유도용 5개
                2. 영상 요약문: 영상의 핵심을 3~4줄로 요약 (템플릿 내 {{summary}}에 들어갈 내용)
                3. 쉼표 구분 태그 (50개): 검색 노출용 키워드 50개를 쉼표(,)로만 구분하여 나열 (# 금지)
                4. 해시태그 10개: # 포함
                5. 썸네일 카피: 강렬한 문구 3개

                [스크립트]
                {script_text}
                """
                
                response = model.generate_content(prompt)
                full_text = response.text
                
                # AI 응답에서 요약문 부분만 추출하는 것은 복잡하므로, 
                # 여기서는 전체 결과를 보여주되, 설명란 영역은 템플릿을 적용하여 별도로 상단에 노출합니다.
                
                st.success(f"✅ {selected_channel_name} 데이터 생성 완료!")
                st.divider()
                
                # 결과 출력 섹션
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📋 추천 제목 & 요약")
                    st.info("아래 요약문을 채널 템플릿과 합쳐서 사용하세요.")
                    st.write(full_text)
                
                with col2:
                    st.subheader("📝 채널 맞춤형 설명란 (복사용)")
                    # 실제 서비스라면 정규식 등으로 AI 응답에서 요약 부분만 뽑아 템플릿에 넣겠지만, 
                    # 현재는 전체 내용을 확인 후 요약 부분만 템플릿에 직접 넣어 활용하는 구조입니다.
                    st.text_area("이 내용을 복사해서 영상 설명란에 붙여넣으세요.", 
                                 value=current_preset['template'].replace("{summary}", "(위의 생성된 요약문을 여기에 넣으세요)"), 
                                 height=300)

        except Exception as e:
            st.error(f"오류 발생: {e}")
