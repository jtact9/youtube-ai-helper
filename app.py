import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="유튜브 PD 전용 툴 v4.6", layout="wide")
st.title("🎬 박사원의 야무진 업로드 세팅 툴")

# 2. 세션 상태 초기화
if 'presets' not in st.session_state:
    st.session_state.presets = {
        "기본 채널": {
            "context": "일반적인 정보 전달",
            "template": "오늘의 영상 요약입니다!\n\n{summary}\n\n구독과 좋아요 부탁드려요!"
        }
    }

# 3. 사이드바 - 프리셋 관리자
with st.sidebar:
    st.header("⚙️ 시스템 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password", placeholder="구글 AI 스튜디오에서 발급받은 키를 넣으세요")
    
    st.divider()
    st.subheader("🗂️ 채널 프리셋 매니저")
    
    with st.expander("➕ 새 채널 등록 (예시 보기)", expanded=True):
        new_name = st.text_input(
            "채널 이름", 
            placeholder="EX) 유로진 남성의원 부산점"
        )
        new_context = st.text_input(
            "채널 성격 (AI 지시용)", 
            placeholder="EX) 비뇨기과 전문의의 차분하고 신뢰감 있는 톤"
        )
        new_template = st.text_area(
            "설명란 포맷 (자동 병합 틀)",
            placeholder="""EX)
💫 남성 건강의 시작, 유로진입니다 💫

{summary}

---
📍 위치 : 부산 부산진구 부전동 257-3
🌐 홈페이지 : http://busan.urogyn.co.kr/""",
            height=250,
            help="{summary}라고 적은 위치에 AI가 쓴 영상 요약이 자동으로 들어갑니다."
        )
        
        if st.button("프리셋 저장"):
            if new_name and new_template:
                st.session_state.presets[new_name] = {"context": new_context, "template": new_template}
                st.success(f"'{new_name}' 프리셋 저장 완료!")
                st.rerun()
            else:
                st.error("채널명과 포맷을 모두 입력해주세요.")

    st.divider()
    selected_ch = st.selectbox("📺 현재 작업 채널 선택", list(st.session_state.presets.keys()))
    current_config = st.session_state.presets[selected_ch]

# 4. 메인 화면 - 입력창
script_text = st.text_area(
    f"[{selected_ch}] 영상 스크립트를 입력하세요", 
    height=400,
    placeholder="""여기에 영상 전체 스크립트를 붙여넣으세요. 
타임라인(00:00)이나 대화 내용이 포함되어 있어도 AI가 알아서 분석합니다."""
)

if st.button("🚀 맞춤형 데이터 생성 시작"):
    if not api_key or not script_text:
        st.error("API 키와 스크립트를 입력해주세요.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            with st.spinner(f"[{selected_ch}] 스타일에 맞춰 분석 중..."):
                prompt = f"""
                유튜브 SEO 전문가로서 다음 지침에 따라 데이터를 작성하세요.
                
                1. 추천 제목: 클릭률이 높은 제목 5개
                2. 요약문: 반드시 [[SUMMARY]] 요약내용 [[/SUMMARY]] 형식으로 작성 (3~4줄, {current_config['context']})
                3. 태그 50개: 쉼표로만 구분 (# 없음)
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
                    extracted = "요약문 추출 오류가 발생했습니다."

                final_description = current_config['template'].replace("{summary}", extracted)

                st.success("✅ 생성 완료!")
                st.divider()

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader("📋 AI 분석 원본")
                    st.write(res_text.replace("[[SUMMARY]]", "").replace("[[/SUMMARY]]", ""))
                with col2:
                    st.subheader("✍️ 완성된 설명란 (즉시 복사)")
                    st.text_area("유튜브 업로드 시 그대로 붙여넣으세요.", value=final_description, height=600)

        except Exception as e:
            st.error(f"오류 발생: {e}")
