from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime

# 1. Ollama를 이용한 로컬 LLM 초기화 (local.py 참고)
llm = ChatOllama(
    model="qwen2.5:14b",  # 로컬에 설치된 모델명 (상황에 따라 "exaone3.5:7.8b" 등으로 변경 가능)
    temperature=0.3,      # network.py의 창의성 설정값 유지
)

# 2. 프롬프트 템플릿 설정 (network.py의 시스템 및 유저 프롬프트 반영)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "당신은 부동산 및 건물관리(FM/PM) 산업 전문 경영 전략 컨설턴트입니다."
        ),
        (
            "user",
            """현시점 대한민국 건물관리 회사가 직면한 구조적 현실과 위기를 극복하기 위한 핵심 생존 전략 3가지를 두괄식으로 제언해 줘.
반드시 마크다운 표, 소제목, 글머리 기호를 활용하여 사람이 읽기 쉬운 비즈니스 보고서 형태로 작성해 줘."""
        ),
    ]
)

# 체인(Chain) 구성
chain = prompt | llm

def generate_building_management_report():
    try:
        print("=== Ollama 활용 보고서 생성 중... ===")

        # 3. 로컬 LLM 실행 (네트워크 요청 대신 체인 invoke 사용)
        response = chain.invoke({})
        report_content = response.content

        # 4. 보고서 헤더 장식 (network.py의 파일 저장 및 포맷팅 로직 유지)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_report = f"""# [EXECUTIVE REPORT] 대한민국 건물관리(FM/PM) 산업 현실 및 생존 전략
- **작성 일시:** {current_time}
- **주관 부서:** 사업밸류업팀

---

{report_content}
"""

        # 콘솔 출력
        print(formatted_report)

        # 마크다운 파일(.md)로 자동 저장
        filename = f"Building_Management_Strategy_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_report)
        print(f"\n[성공] 보고서가 파일로 저장되었습니다: {filename}")

    except Exception as e:
        print(f"오프라인 모델 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    generate_building_management_report()
