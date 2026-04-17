import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 (완벽한 원페이지 레이아웃 및 사이드바 제거)
st.set_page_config(page_title="유튜브 PD 전용 툴 v5.5", layout="wide", initial_sidebar_state="collapsed")

# 사이드바를 완전히 제거하고 메인 영역을 넓게 쓰는 CSS
st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .main {padding-top: 1rem;}
        .stButton>button {width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 유튜브 업로드 자동화 v5.5")

# 2. 세션 상태 초기화 (프리셋 데이터)
if 'presets' not in st.session_state:
    st.session_state.presets = {
        "기본 설정": {
            "context": "일반적인 정보 전달 및 후킹 스타일",
            "template": "오늘의 영상 핵심 내용입니다!\n\n{summary}\n\n#구독 #좋아요"
        }
    }

# 3. [상단] 채널 프리셋 매니저
st.subheader("🗂️ 채널 프리셋 및 포맷 설정")
col_sel, col_add = st.columns([1, 1.5])

with col_sel:
    selected_ch = st.selectbox("📺 작업 채널 선택", list(st.session_state.presets.keys()))
    current_config = st.session_state.presets[selected_ch]

with col_add:
    with st.expander("➕ 새 채널 등록 및 설명란 포맷 지정"):
        new_name = st.text_input("채널 이름", placeholder="EX) 유로진 남성의원 부산점")
        new_context = st.text_input("채널 성격", placeholder="EX) 비뇨기과 전문의의 신뢰감 있는 톤")
        new_template = st.text_area(
            "설명란 포맷 (EX 참고)",
            placeholder="EX)\n💫 남성 건강의 시작, 유로진입니다 💫\n\n{summary}\n\n📍 위치 : 부산 부전동 257-3",
            height=150
        )
        if st.button("프리셋 저장"):
            if new_name and new_template:
                st.session_state.presets[new_name] = {"context": new_context, "template": new_template}
                st.success(f"'{new_name}' 저장 완료!")
                st.rerun()

st.divider()

# 4. [중단] 스크립트 입력창
script_text = st.text_area(
    f"📝 [{selected_ch}] 영상 스크립트 입력", 
    height=350,
    placeholder="전체 스크립트를 붙여넣으세요. 타임라인이 포함되어 있어도 AI가 정밀 분석합니다."
)

# 5. [하단] 데이터 생성 및 결과
if st.button("🚀 맞춤형 데이터 생성 시작"):
    if not script_text:
        st.warning("분석할 스크립트를 입력해주세요.")
    else:
        try:
            # Streamlit Secrets나 환경 변수에서 키를 자동으로 가져옴
            # 설정되지 않은 경우를 대비한 최소한의 예외 처리
            try:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            except:
                st.error("🚨 시스템에 GEMINI_API_KEY가 설정되어 있지 않습니다. Streamlit Secrets 설정을 확인하세요.")
                st.stop()

            model = genai.GenerativeModel("gemini-2.0-flash")
            
            with st.spinner(f"[{selected_ch}] 스타일에 맞춰 분석 중..."):
                prompt = f"""
                당신은 유튜브 SEO 전문가입니다. 다음 지침을 엄수하여 [스크립트]를 분석하세요.

                1. 추천 제목 리스트: 클릭 유도용 5개
                2. 요약문: 반드시 [[SUMMARY]] 내용 [[/SUMMARY]] 형식으로 작성.
                   - 시청자가 궁금증을 느껴 클릭하도록 호기심을 유발하는 포인트 2~3개만 축약 (3~4줄, 불릿 기호 사용).
                3. 쉼표 구분 태그 (50개): 연관 키워드 50개를 쉼표(,)로만 구분해 나열. (# 없음)
                4. 해시태그 10개: # 포함 10개
                5. 썸네일 카피: 강렬한 문구 3개

                [채널 성격: {current_config['context']}]
                [스크립트: {script_text}]
                """
                
                response = model.generate_content(prompt)
                res_text = response.text

                # 요약문 파싱 및 결합
                try:
                    summary_content = res_text.split("[[SUMMARY]]")[1].split("[[/SUMMARY]]")[0].strip()
                except:
                    summary_content = "요약 추출 오류"

                final_description = current_config['template'].replace("{summary}", summary_content)

                st.success("✅ 생성 완료!")
                st.divider()

                col_res1, col_res2 = st.columns([1, 1.3])
                
                with col_res1:
                    st.subheader("💡 AI 추천 데이터")
                    st.write(res_text.replace("[[SUMMARY]]", "").replace("[[/SUMMARY]]", ""))
                
                with col_res2:
                    st.subheader("📝 완성된 설명란 (복사용)")
                    st.text_area("그대로 복사해서 사용하세요.", value=final_description, height=600)

        except Exception as e:
            st.error(f"오류 발생: {e}")
