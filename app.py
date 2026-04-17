import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 툴 v4.0", layout="wide")
st.title("🎬 유튜브 업로드 자동화 v4.0 (다이나믹 프리셋)")

# 2. 프로그램 메모리(Session State) 초기화
if 'presets' not in st.session_state:
    # 기본 예시 데이터 하나만 넣어둡니다.
    st.session_state.presets = {
        "기본 채널": {
            "context": "일반적인 톤",
            "template": "오늘의 요약: {summary}\n\n#구독 #좋아요"
        }
    }

# 3. 사이드바 - 프리셋 관리자
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    
    st.divider()
    st.subheader("🗂️ 채널 프리셋 관리")
    
    # [추가/수정 섹션]
    with st.expander("➕ 채널 추가 및 포맷 지정"):
        ch_name = st.text_input("채널명 (예: ㅁㅁ의원)")
        ch_context = st.text_input("채널 성격 (예: 의학 정보)")
        ch_template = st.text_area(
            "설명란 포맷 입력", 
            value="[고정 문구 시작]\n{summary}\n[고정 문구 끝]",
            help="{summary}라고 적힌 곳에 AI 요약이 들어갑니다.",
            height=200
        )
        if st.button("프리셋 저장/업데이트"):
            if ch_name and ch_template:
                st.session_state.presets[ch_name] = {"context": ch_context, "template": ch_template}
                st.success(f"'{ch_name}' 프리셋이 저장되었습니다.")
                st.rerun() # UI 즉시 갱신
            else:
                st.error("이름과 포맷을 입력하세요.")

    # [삭제 섹션]
    if len(st.session_state.presets) > 1:
        with st.expander("🗑️ 프리셋 삭제"):
            target_del = st.selectbox("삭제할 프리셋 선택", list(st.session_state.presets.keys()))
            if st.button("삭제 실행"):
                del st.session_state.presets[target_del]
                st.success("삭제 완료")
                st.rerun()

    st.divider()
    # [작업 대상 선택]
    selected_channel = st.selectbox("📺 현재 작업 채널 선택", list(st.session_state.presets.keys()))
    current_config = st.session_state.presets[selected_channel]
    selected_model = st.selectbox("🤖 AI 모델 선택", ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"])

# 4. 메인 화면 - 입력창
script_text = st.text_area(f"[{selected_channel}] 영상 스크립트를 입력하세요", height=400)

if st.button("🚀 맞춤형 데이터 생성 시작"):
    if not api_key or not script_text:
        st.error("API 키와 스크립트를 입력해주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model)
            
            with st.spinner(f"[{selected_channel}] 포맷에 맞춰 제작 중..."):
                prompt = f"""
                유튜브 SEO 전문가로서 다음 지침에 따라 데이터를 작성하세요.
                
                1. 추천 제목: 5개
                2. 요약문: 반드시 [[SUMMARY]] 요약내용 [[/SUMMARY]] 형식으로 작성 (3~4줄, {current_config['context']})
                3. 태그 50개: 쉼표로만 구분된 리스트 (# 없음)
                4. 해시태그 10개: # 포함
                5. 썸네일 카피: 3개

                [스크립트]
                {script_text}
                """
                response = model.generate_content(prompt)
                res_text = response.text

                # 요약문 파싱 및 템플릿 결합
                try:
                    extracted = res_text.split("[[SUMMARY]]")[1].split("[[/SUMMARY]]")[0].strip()
                except:
                    extracted = "요약문 추출 오류"

                final_description = current_config['template'].replace("{summary}", extracted)

                st.success("✅ 생성 완료!")
                st.divider()

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("📋 AI 분석 원본")
                    st.write(res_text)
                with col2:
                    st.subheader("✍️ 완성된 채널별 설명란")
                    st.text_area("그대로 복사해서 사용하세요.", value=final_description, height=500)

        except Exception as e:
            st.error(f"오류 발생: {e}")
