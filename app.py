import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 스타일 (출력창을 더 넓게 설정)
st.set_page_config(page_title="유튜브 PD 전용 툴 v4.1", layout="wide")
st.title("🎬 박사원의 유튜브 업로드세팅 자동화 ")

# 2. 세션 상태 초기화
if 'presets' not in st.session_state:
    st.session_state.presets = {
        "샘플 채널": {
            "context": "의학 정보 전달",
            "template": "💫 제목 또는 인삿말 💫\n\n{summary}\n\n📍 위치: 서울 어딘가\n📞 문의: 010-0000-0000"
        }
    }

# 3. 사이드바 - 프리셋 관리자
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    
    st.divider()
    st.subheader("🗂️ 채널 프리셋 매니저")
    
    with st.expander("➕ 새 채널 포맷 등록하기"):
        new_name = st.text_input("채널 이름")
        new_context = st.text_input("AI가 참고할 채널 성격")
        # 여기서 두 번째 사진 같은 텍스트를 통째로 붙여넣습니다.
        new_template = st.text_area(
            "두 번째 사진의 텍스트를 아래에 붙여넣으세요.\n내용이 바뀔 부분만 {summary}로 적어주세요.",
            height=300
        )
        if st.button("프리셋 저장"):
            if new_name and new_template:
                st.session_state.presets[new_name] = {"context": new_context, "template": new_template}
                st.success(f"'{new_name}' 등록 완료!")
                st.rerun()

    st.divider()
    selected_ch = st.selectbox("📺 작업할 채널 선택", list(st.session_state.presets.keys()))
    current_config = st.session_state.presets[selected_ch]
    selected_model = st.selectbox("🤖 모델", ["gemini-2.0-flash", "gemini-flash-latest"])

# 4. 메인 화면
script_text = st.text_area("영상 스크립트를 입력하세요", height=300)

if st.button("🚀 템플릿에 맞춰 생성하기"):
    if not api_key or not script_text:
        st.error("API 키와 스크립트를 입력해주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(selected_model)
            
            # AI에게 템플릿의 분위기에 맞춰 요약하라고 지시 강화
            prompt = f"""
            유튜브 마케팅 전문가로서 [스크립트]를 분석하세요.
            
            결과물 가이드:
            1. 제목 5개
            2. 요약문: [[SUMMARY]] 이 부분은 {current_config['context']} 톤으로, 시청자의 고민을 터치하며 영상 내용을 궁금하게 만드는 문체로 작성하세요. (3~5줄) [[/SUMMARY]]
            3. 태그 50개: 쉼표로 구분
            4. 해시태그 10개: # 포함
            5. 썸네일 카피 3개

            [스크립트]
            {script_text}
            """
            
            with st.spinner("분석 및 포맷팅 중..."):
                response = model.generate_content(prompt)
                res_text = response.text
                
                try:
                    summary_content = res_text.split("[[SUMMARY]]")[1].split("[[/SUMMARY]]")[0].strip()
                except:
                    summary_content = "요약 추출 실패"

                # 템플릿 합치기
                final_desc = current_config['template'].replace("{summary}", summary_content)

                st.success("✅ 생성 완료!")
                st.divider()
                
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    st.subheader("💡 추천 제목 & 태그")
                    st.write(res_text.replace(f"[[SUMMARY]]{summary_content}[[/SUMMARY]]", "완료"))
                with c2:
                    st.subheader("📝 완성된 설명란 (복사용)")
                    st.text_area("이 내용을 그대로 유튜브에 붙여넣으세요.", value=final_desc, height=600)

        except Exception as e:
            st.error(f"오류: {e}")
