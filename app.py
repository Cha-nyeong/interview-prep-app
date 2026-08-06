import streamlit as st
import google.generativeai as genai

# 웹 페이지 기본 설정
st.set_page_config(page_title="고교 3학년 맞춤형 면접질문 생성기", layout="centered")

st.title("🎓 대입 모의면접 질문 생성 시스템")
st.caption("자신의 희망 전공과 핵심 생기부 활동을 입력하면 입학사정관 수준의 질문이 생성됩니다.")

# Streamlit Secrets에서 API 키 로드
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

# 입력 폼
with st.form("interview_form"):
    student_id = st.text_input("학번 및 이름", placeholder="예: 30101 홍길동")
    major = st.text_input("지원 희망 전공/학과", placeholder="예: 컴퓨터공학과, 국어교육과 등")
    activity = st.text_area(
        "생기부 핵심 탐구/활동 내용 (300자 이상 권장)",
        placeholder="예: 2학년 진로활동 시간에 AI 윤리와 가치관에 대한 보고서를 작성함. 인공지능의 편향성 문제를 주제로 법적 규제의 필요성을 탐구함...",
        height=180
    )
    submitted = st.form_submit_button("면접 질문 생성하기")

# 제출 클릭 시 AI 질문 생성
if submitted:
    if not student_id or not major or not activity:
        st.warning("모든 항목을 입력해주세요.")
    else:
        with st.spinner("입학사정관 관점에서 심화 질문을 추출하고 있습니다..."):
            try:
                # 프롬프트 설계
                prompt = f"""
                당신은 대한민국 주요 대학의 정시/수시 학종 전문 입학사정관이자 해당 전공 분야의 교수입니다.
                학생이 제출한 정보와 활동 내용을 바탕으로, 실제 대입 면접에서 활용 가능한 고난도 면접 질문 3개를 생성하세요.

                [학생 정보]
                - 학번/이름: {student_id}
                - 지원 전공: {major}
                - 생기부 핵심 활동: {activity}

                [질문 생성 원칙 - 총 3문항]
                1. [지식·탐구 검증 질문]: 제출한 활동에서 언급된 핵심 개념, 이론, 법칙의 학술적 정의나 원리를 구체적으로 확인하는 질문.
                2. [심화·응용 질문]: 해당 탐구 내용이 실제 사회적 이슈, 최신 학문 동향, 또는 타 교과 개념과 어떻게 확장되는지 묻는 질문.
                3. [태도·성찰 질문]: 탐구 과정에서 느낀 한계점이나 오류, 이를 극복하는 과정에서 일어난 학업적 변화를 묻는 질문.

                [출력 형식]
                - 각 질문마다 '질문 의도(평가 요소)'를 괄호로 명시할 것.
                - 친절하면서도 예리한 입학사정관의 어조를 유지할 것.
                """

                # Gemini 모델 호출
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)

                st.success("면접 질문 생성이 완료되었습니다!")
                st.markdown("---")
                st.subheader(f"📌 {student_id} 학생을 위한 맞춤형 면접 질문")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"질문 생성 중 오류가 발생했습니다: {e}")
