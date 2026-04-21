import streamlit as st
import google.generativeai as genai
import json
import os
import base64
from docx import Document
import PyPDF2
import random
from datetime import datetime
from io import BytesIO

# 1. 페이지 브랜딩 및 디자인 설정 (다크 테마 및 라이트 모드 시인성 강제 고정)
st.set_page_config(page_title="박사원의 만능 워크벤치", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: #FFFFFF !important; }
    section[data-testid="stSidebar"] { background-color: #161b22 !important; }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] .stRadio label { color: #FFFFFF !important; }
    .marquee {
        width: 100%; line-height: 50px; background-color: #f1c40f; color: #000000 !important;
        white-space: nowrap; overflow: hidden; box-sizing: border-box;
        border-radius: 10px; margin-bottom: 20px; font-weight: bold;
    }
    .marquee p { display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; margin: 0; color: #000000 !important; }
    @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #E74C3C; color: white !important; font-weight: bold; border: none; }
    .notice-card-pinned { background-color: #2d333b; padding: 20px; border-radius: 10px; border-left: 8px solid #f1c40f; margin-bottom: 15px; border-top: 1px solid #f1c40f; color: #FFFFFF !important; }
    .notice-card { background-color: #21262d; padding: 20px; border-radius: 10px; border-left: 5px solid #E74C3C; margin-bottom: 15px; color: #FFFFFF !important; }
    .tag-box { background-color: #1e1e1e; padding: 20px; border-radius: 10px; border: 2px solid #00FF00; color: #00FF00 !important; font-family: monospace; font-size: 1rem; line-height: 1.6; word-break: break-all; }
    label, p, span, h1, h2, h3 { color: #FFFFFF !important; }
    .stTextArea textarea, .stTextInput input { background-color: #1c2128 !important; color: #FFFFFF !important; border: 1px solid #30363d !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 저장 및 자동 복구 로직 (KeyError 완전 방지)
NOTICES_FILE = 'notices.json'

def load_notices():
    default_notice = [{"id": 1, "date": datetime.now().strftime("%Y-%m-%d"), "tag": "필독", "content": "🚨 [가이드] 생성 중 메뉴 이동 시 초기화됩니다. 에러 시 엔진 변경 후 1분 뒤 재시도 바랍니다. 🚨", "image": None, "pinned": True}]
    if os.path.exists(NOTICES_FILE):
        try:
            with open(NOTICES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    if not isinstance(item, dict): continue
                    if 'id' not in item: item['id'] = random.randint(100000, 999999)
                    if 'pinned' not in item: item['pinned'] = False
                return data
        except: return default_notice
    return default_notice

def save_notices(notices):
    with open(NOTICES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notices, f, ensure_ascii=False, indent=4)

if 'notices' not in st.session_state:
    st.session_state.notices = load_notices()

# 3. 최상단 동적 공지
pinned_list = [n for n in st.session_state.notices if n.get('pinned', False)]
marquee_content = f"📌 [고정] {pinned_list[0]['content']}" if pinned_list else (st.session_state.notices[0]['content'] if st.session_state.notices else "공지 없음")
st.markdown(f'<div class="marquee"><p>{marquee_content}</p></div>', unsafe_allow_html=True)

# 4. 시스템 엔진 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("⚠️ Secrets 설정에서 GEMINI_API_KEY를 확인하세요.")
    st.stop()

# 5. 사이드바 구성 (공지게시판 최상단)
with st.sidebar:
    st.title("🛠️ 워크벤치")
    menu = st.radio("업무 선택", ["📋 공지게시판", "🎬 유튜브 업로드 세팅", "📧 비즈니스 격식 변환기", "📝 콘텐츠 기획 콘티"])
    st.divider()
    selected_model = st.selectbox("엔진 선택", ["gemini-2.0-flash", "gemini-2.5-flash"])
    if 'tokens' not in st.session_state: st.session_state.tokens = 0
    st.metric("마지막 작업 토큰", f"{st.session_state.tokens} pts")

def img_to_base64(file):
    return base64.b64encode(file.read()).decode() if file else None

# ==========================================
# 6. 기능 1: 공지게시판 (삭제 및 고정 포함)
# ==========================================
if menu == "📋 공지게시판":
    st.title("📋 팀 공지게시판")
    with st.expander("➕ 새 공지 등록 (관리자 전용)"):
        n_tag = st.selectbox("태그", ["필독", "안내", "업데이트", "긴급"])
        n_content = st.text_area("내용")
        n_img = st.file_uploader("이미지 첨부", type=["png", "jpg", "jpeg"])
        n_pass = st.text_input("관리자 인증 번호", type="password")
        if st.button("📢 등록"):
            if n_pass == "0914" and n_content:
                img_data = img_to_base64(n_img)
                new = {"id": random.randint(100000, 999999), "date": datetime.now().strftime("%Y-%m-%d"), "tag": n_tag, "content": n_content, "image": img_data, "pinned": False}
                st.session_state.notices.insert(0, new); save_notices(st.session_state.notices); st.rerun()
            else: st.error("인증 실패")

    st.markdown("---")
    sorted_notices = sorted(st.session_state.notices, key=lambda x: x.get('pinned', False), reverse=True)
    for n in sorted_notices:
        notice_id = n.get('id')
        idx = next(i for i, item in enumerate(st.session_state.notices) if item.get('id') == notice_id)
        is_p = n.get("pinned", False)
        st.markdown(f'<div class="{"notice-card-pinned" if is_p else "notice-card"}"><small>[{n.get("date")}] <b>{n.get("tag")}</b> {"📌 상단 고정됨" if is_p else ""}</small><br><p>{n.get("content")}</p></div>', unsafe_allow_html=True)
        if n.get("image"):
            try: st.image(base64.b64decode(n["image"]), width=500)
            except: pass
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            with st.popover("📌 고정"):
                if st.text_input("인증", type="password", key=f"p_{notice_id}") == "0914":
                    if st.button("설정/해제", key=f"pb_{notice_id}"):
                        if not is_p:
                            for item in st.session_state.notices: item["pinned"] = False
                            st.session_state.notices[idx]["pinned"] = True
                        else: st.session_state.notices[idx]["pinned"] = False
                        save_notices(st.session_state.notices); st.rerun()
        with c2:
            with st.popover("🗑️ 삭제"):
                if st.text_input("인증", type="password", key=f"d_{notice_id}") == "0914":
                    if st.button("확인", key=f"db_{notice_id}"):
                        st.session_state.notices.pop(idx); save_notices(st.session_state.notices); st.rerun()

# ==========================================
# 7. 기능 2: 유튜브 업로드 세팅 (레이아웃 및 데이터 보정)
# ==========================================
elif menu == "🎬 유튜브 업로드 세팅":
    st.title("🎬 유튜브 업로드 세팅")
    
    with st.expander("🛠️ 설명란 양식 편집"):
        # 이미지 3c5a3c.png 에러 수정: 따옴표를 정확히 닫았습니다.
        default_template = """💫 남성 건강의 시작, 유로진에서 함께하세요 💫

{summary}

📍 위치 : 부산 부산진구 부전동 257-3
✔️ 홈페이지 : http://busan.urogyn.co.kr/"""
        desc_template = st.text_area("템플릿", value=default_template, height=180)
        fixed_hashtags = st.text_input("고정 해시태그", value="#유로진남성의원 #부산비뇨기과 #남성건강")

    uploaded_file = st.file_uploader("스크립트 파일 업로드", type=["txt", "docx", "pdf"])
    final_script = ""
    if uploaded_file:
        try:
            ftype = uploaded_file.name.split('.')[-1].lower()
            if ftype == 'txt': final_script = uploaded_file.read().decode("utf-8")
            elif ftype == 'docx': final_script = "\n".join([p.text for p in Document(uploaded_file).paragraphs])
            elif ftype == 'pdf':
                for p in PyPDF2.PdfReader(uploaded_file).pages: final_script += (p.extract_text() or "") + "\n"
        except: st.error("파일 로드 실패")
    else: final_script = st.text_area("직접 입력", height=150)

    if st.button("🚀 데이터 추출하기"):
        if not final_script: st.warning("분석할 내용을 입력하세요.")
        else:
            try:
                model = genai.GenerativeModel(selected_model)
                with st.spinner("🎬 데이터를 생성 중..."):
                    # 프롬프트 고도화: 요약, 제목, 썸네일 카피 명시적 요청
                    prompt = f"""유튜브 PD로서 다음 스크립트를 분석해.
                    1. 요약: 4~5줄, 줄바꿈 필수, 이모지 포함, 호기심 유발 (key: "요약")
                    2. 추천 제목: 클릭을 유도하는 제목 3개 (key: "제목")
                    3. 썸네일 카피: 강렬한 문구 3개 (key: "썸네일")
                    4. 태그: 쉼표로 구분된 50개 키워드. 특수문자나 따옴표 금지 (key: "태그")
                    결과를 JSON으로 줘. 스크립트: {final_script}"""
                    
                    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                    data = json.loads(response.text)
                    st.session_state.tokens = response.usage_metadata.total_token_count
                    
                    # 레이아웃 구성: 좌측 설명란 / 우측 추천 정보
                    col_l, col_r = st.columns(2)
                    
                    with col_l:
                        st.markdown("### 📋 복사용 설명란")
                        # 데이터 매핑 보정
                        summary_val = data.get("요약", "요약 데이터를 생성하지 못했습니다.")
                        final_desc = desc_template.replace("{summary}", summary_val)
                        st.code(f"{final_desc}\n\n{fixed_hashtags}", language="text")
                    
                    with col_r:
                        st.markdown("### 💡 추천 제목 & 썸네일")
                        titles = data.get("제목", [])
                        for t in titles: st.write(f"📍 {t}")
                        st.divider()
                        st.markdown("#### 🖼️ 썸네일 카피 추천")
                        copies = data.get("썸네일", [])
                        for c in copies: st.info(f"✨ {c}")

                    st.markdown("---")
                    st.markdown("### 🏷️ 태그 (쉼표 구분)")
                    # 태그 포맷 보정
                    raw_tags = data.get("태그", "")
                    if isinstance(raw_tags, list): clean_tags = ", ".join(raw_tags)
                    else: clean_tags = str(raw_tags).replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                    st.markdown(f'<div class="tag-box">{clean_tags}</div>', unsafe_allow_html=True)
                    
            except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 8. 기능 3: 비즈니스 격식 변환기
# ==========================================
elif menu == "📧 비즈니스 격식 변환기":
    st.title("📧 비즈니스 격식 변환기")
    biz_tone = st.selectbox("변환 톤", ["아주 정중하게", "부드럽고 친절하게", "단호하고 명확하게"])
    raw_text = st.text_area("내용 입력", height=150)
    if st.button("✨ 변환하기"):
        try:
            model = genai.GenerativeModel(selected_model)
            prompt = f"비즈니스 전문가로서 '영상팀 박진성 사원' 명의로 다음을 '{biz_tone}'으로 변환. {raw_text}"
            response = model.generate_content(prompt)
            st.code(response.text, language="text")
        except Exception as e: st.error(f"오류: {e}")

# ==========================================
# 9. 기능 4: 콘텐츠 기획 콘티 (시즌 7 메커니즘 탑재)
# ==========================================
elif menu == "📝 콘텐츠 기획 콘티":
    st.title("📝 콘텐츠 기획 콘티 (시즌 7 Style)")
    client_name = st.text_input("업체명", value="유로진 부산점")
    q_count = st.slider("질문 개수", 3, 10, 6)
    
    st.markdown("### 🎯 주제별 상세 가이드")
    # 레이블 수정: 박 PD님 -> PD님
    st.info("각 주제에서 어떤 내용을 중점적으로 다룰지 PD님의 의도를 적어주세요.")
    
    c1, c2 = st.columns(2)
    with c1:
        f1 = st.text_input("주제 1 가이드", value="도입부 위험성 강조")
        f2 = st.text_input("주제 2 가이드", value="민간요법 팩트체크")
    with c2:
        f3 = st.text_input("주제 3 가이드", value="수술 상세 과정")
        f4 = st.text_input("주제 4 가이드", value="사후 관리 및 당부")

    ref_text = st.text_area("레퍼런스 입력", height=150)
    if st.button("💡 시즌 7 스타일 콘티 생성"):
        try:
            model = genai.GenerativeModel(selected_model)
            # 시즌 7 메커니즘: 주제-핵심포인트-질문리스트 구성 강제 [cite: 1, 2, 14, 15]
            prompt = f"""당신은 전문 콘텐츠 전략가입니다. 업체 '{client_name}'를 위한 시즌 7 스타일의 콘티를 작성하세요.
            [가이드] 주제1:{f1}, 주제2:{f2}, 주제3:{f3}, 주제4:{f4}
            [형식 규칙]
            - 각 주제는 '주제 X. [제목]'으로 시작.
            - 제목 바로 아래 '핵심 포인트 : [한 줄 요약]' 명시.
            - 질문은 반드시 '#' 번호를 매기고 구어체(예: '원장님, ~인가요?')로 {q_count}개씩 작성.
            레퍼런스: {ref_text}"""
            
            response = model.generate_content(prompt)
            st.markdown('<div class="notice-card">', unsafe_allow_html=True)
            st.write(response.text)
            st.markdown('</div>', unsafe_allow_html=True)
            st.balloons()
        except Exception as e: st.error(f"오류: {e}")
