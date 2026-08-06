import streamlit as st
import google.generativeai as genai

# 웹 페이지 기본 설정
st.set_page_config(page_title="맞춤형 모의면접 질문 생성기", layout="centered")

st.title("🎓💼 맞춤형 모의면접 질문 생성 시스템")
st.caption("진로 희망(대입/취업·알바)에 맞춰 나만의 면접 질문을 생성하고 수행평가 활동지에 활용하세요.")

# Streamlit Secrets에서 API 키 로드 및 설정
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API 키 설정이 필요합니다. Streamlit Secrets 설정을 확인해주세요.")
    st.stop()

# 사용 가능한 최신 모델 자동 탐색 함수
@st.cache_resource
def get_working_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        for preferred in ['gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']:
            for m in available_models:
                if preferred in m:
                    return m
        
        if available_models:
            return available_models[0]
    except Exception:
        pass
    return "gemini-2.5-flash"

# 1. 면접 유형 선택 (Radio Button)
interview_type = st.radio(
    "📌 면접 유형을 선택하세요:",
    ("Type A: 대입 진학용 면접", "Type B: 취업/알바 구인용 면접"),
    horizontal=True
)

st.markdown("---")

# 2. 입력 폼 구성 (유형에 따라 동적 변경)
with st.form("interview_form"):
    student_id = st.text_input("학번 및 이름", placeholder="예: 30101 홍길동")
    
    if "Type A" in interview_type:
        major_or_job = st.text_input("지원 희망 전공/학과", placeholder="예: 컴퓨터공학과, 국어교육과 등")
        activity_or_exp = st.text_area(
            "생기부 핵심 탐구/활동 내용 (300자 이상 권장)",
            placeholder="예: 2학년 진로활동 시간에 AI 윤리와 가치관에 대한 보고서를 작성함...",
            height=180
        )
    else:
        major_or_job = st.text_input("지원 희망 직무 및 업종", placeholder="예: 카페 바리스타, 편의점 알바, 웹디자이너, 사무보조 등")
        activity_or_exp = st.text_area(
            "관련 경험, 강점 및 주요 역량 (300자 이상 권장)",
            placeholder="예: 성실함과 인내심이 강점임. 동아리 활동에서 부기장을 맡아 팀원 간의 의견 대립을 중재한 경험이 있으며, 서비스직 관련 기초 예절을 숙지함...",
            height=180
        )
        
    submitted = st.form_submit_button("면접 질문 생성하기")

# 3. 제출 클릭 시 AI 질문 생성
if submitted:
    if not student_id or not major_or_job or not activity_or_exp:
        st.warning("모든 항목을 입력해주세요.")
    else:
        with st.spinner("선택한 면접 유형에 맞춘 심화 질문을 추출하고 있습니다..."):
            try:
                # Type A (대입) 프롬프트
                if "Type A" in interview_type:
                    prompt = f"""
                    당신은 대한민국 주요 대학의 정시/수시 학종 전문 입학사정관이자 해당 전공 분야의 교수입니다.
                    학생이 제출한 정보와 활동 내용을 바탕으로, 실제 대입 면접에서 활용 가능한 고난도 면접 질문 3개를 생성하세요.

                    [학생 정보]
                    - 학번/이름: {student_id}
                    - 지원 전공: {major_or_job}
                    - 생기부 핵심 활동: {activity_or_exp}

                    [질문 생성 원칙 - 총 3문항]
                    1. [지식·탐구 검증 질문]: 제출한 활동에서 언급된 핵심 개념, 이론, 법칙의 학술적 정의나 원리를 구체적으로 확인하는 질문.
                    2. [심화·응용 질문]: 해당 탐구 내용이 실제 사회적 이슈, 최신 학문 동향, 또는 타 교과 개념과 어떻게 확장되는지 묻는 질문.
                    3. [태도·성찰 질문]: 탐구 과정에서 느낀 한계점이나 오류, 이를 극복하는 과정에서 일어난 학업적 변화를 묻는 질문.

                    [출력 형식]
                    - 각 질문마다 '질문 의도(평가 요소)'를 괄호로 명시할 것.
                    - 친절하면서도 예리한 입학사정관의 어조를 유지할 것.
                    """
                # Type B (취업/알바) 프롬프트
                else:
                    prompt = f"""
                    당신은 해당 채용 분야의 면접관이자 인사담당자(또는 매장 채용 매니저)입니다.
                    지원자가 제출한 정보와 역량/경험 내용을 바탕으로, 실제 채용 면접에서 활용 가능한 맞춤형 면접 질문 3개를 생성하세요.

                    [지원자 정보]
                    - 학번/이름: {student_id}
                    - 지원 직무/업종: {major_or_job}
                    - 주요 경험 및 역량: {activity_or_exp}

                    [질문 생성 원칙 - 총 3문항]
                    1. [지원 동기 및 직무 이해도]: 해당 직무에 지원한 이유와 본인이 이해하고 있는 주요 업무 수행 방식에 대해 묻는 질문.
                    2. [상황 대처 및 문제 해결 능력]: 해당 업무 현장에서 발생할 수 있는 실제 돌발 상황(예: 난처한 고객 응대, 업무 미숙, 동료와의 갈등 등)을 제시하고 어떻게 대처할 것인지 묻는 질문.
                    3. [책임감 및 조직 적응력]: 약속 준수, 근태관리, 조직 규율 준수 및 본인의 강점을 현장에 어떻게 적용할지 묻는 질문.

                    [출력 형식]
                    - 각 질문마다 '질문 의도(평가 요소)'를 괄호로 명시할 것.
                    - 실무적이면서도 지원자의 가능성을 확인하는 정중하고 명확한 어조를 유지할 것.
                    """

                target_model_name = get_working_model()
                model = genai.GenerativeModel(target_model_name)
                response = model.generate_content(prompt)
                generated_text = response.text

                st.success("면접 질문 생성이 완료되었습니다!")
                st.markdown("---")
                st.subheader(f"📌 {student_id} 학생({interview_type.split(':')[1].strip()})을 위한 맞춤형 면접 질문")
                
                # 화면 출력
                st.markdown(generated_text)
                
                st.markdown("---")
                st.info("💡 **활동지 작성 안내**: 아래 박스 우측 상단의 **복사 버튼(아이콘)**을 눌러 생성된 질문을 통째로 복사한 뒤 활동지에 붙여넣으세요!")

                # 복사 전용 텍스트 영역
                type_label = "지원전공" if "Type A" in interview_type else "지원직무"
                exp_label = "탐구활동" if "Type A" in interview_type else "경험/역량"
                
                copy_content = f"[학생 정보]\n구분: {interview_type}\n학번/이름: {student_id}\n{type_label}: {major_or_job}\n{exp_label}: {activity_or_exp}\n\n[생성된 면접 질문]\n{generated_text}"
                st.code(copy_content, language="text")

            except Exception as e:
                st.error(f"질문 생성 중 오류가 발생했습니다: {e}")
