import streamlit as st
import google.generativeai as genai
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 툴 v4.5", layout="wide")
st.title("🎬 유튜브 업로드 자동화 v4.5 (히스토리 로그 추가)")

# 2. 세션 상태 초기화 (프리셋 및 기록 저장소)
if 'presets' not in st.session_state:
    st.session_state.presets = {"기본 채널": {"context": "일반", "template": "{summary}"}}

if 'history' not in st.session_state:
    st.session_state.history = []  # 생성 기록을 담을 리스트

# 3. 사이드바 - 관리자 기능
with st.sidebar:
    st.header("⚙️ 시스템 및 기록")
    api_key = st.text_input("Gemini API Key 입력", type="password")
    
    # [기록 확인 섹션]
    st.divider()
    st.subheader("📜 오늘 생성한 기록")
    if not st.session_state.history:
        st.caption("아직 생성된 기록이 없습니다.")
    else:
        for idx, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{item['time']} - {item['channel']}"):
                st.write(f"**제목 후보:**\n{item['result'].split('2.')[0]}") # 제목 부분만 살짝 미리보기
                if st.button("상세보기", key=f"hist_{idx}"):
                    st.session_state.current_view = item # 상세보기 로직용

    st.divider()
    # [프리셋 관리 섹션]
    with st.expander("➕ 채널 포맷 등록/수정"):
        new_name = st.text_input("채널 이름")
        new_template = st.text_area("포맷 입력 ({summary} 포함)", height=200)
        if st.button("프리셋 저장"):
            st.session_state.presets[new_name] = {"context": "", "template": new_template}
            st.rerun()

    selected_ch = st.selectbox("📺 작업 채널 선택", list(st.session_state.presets.keys()))
    current_config = st.session_state.presets[selected_ch]

# 4. 메인 화면
script_text = st.text_area("영상 스크립트를 입력하세요", height=300)

if st.button("🚀 데이터 생성 및 기록 저장"):
    if not api_key or not script_text:
        st.error("입력값을 확인하세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            with st.spinner("AI 분석 및 기록 중..."):
                prompt = f"유튜브 전문가로서 아래 스크립트로 제목 5개, [[SUMMARY]]요약[[/SUMMARY]], 태그 50개, 해시태그 10개, 썸네일 카피를 작성하세요.\n\n[스크립트]\n{script_text}"
                response = model.generate_content(prompt)
                res_text = response.text
                
                # 요약 추출 및 합치기
                try:
                    summary_content = res_text.split("[[SUMMARY]]")[1].split("[[/SUMMARY]]")[0].strip()
                except:
                    summary_content = "요약 추출 실패"
                
                final_desc = current_config['template'].replace("{summary}", summary_content)

                # --- 기록 저장 로직 ---
                history_item = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "channel": selected_ch,
                    "result": res_text,
                    "final_description": final_desc
                }
                st.session_state.history.append(history_item)
                # ---------------------

                st.success("✅ 생성 및 기록 완료!")
                st.divider()
                
                c1, c2 = st.columns([1, 1.2])
                with c1:
                    st.subheader("💡 분석 결과")
                    st.write(res_text)
                with c2:
                    st.subheader("📝 완성된 설명란")
                    st.text_area("복사해서 사용하세요", value=final_desc, height=500)

        except Exception as e:
            st.error(f"오류: {e}")
