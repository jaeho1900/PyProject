from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
import textwrap

# 1. llm 객체 생성
llm = ChatOllama(
    model="qwen2.5:3b",
    # model="exaone3.5:7.8b",
    temperature=0.4,
)

# 2. 템플릿 정의
# # ------------------
# # 1안) 단문응답
# response = llm.invoke("건물관리와 빌딩관리의 가장 큰 차이점을 설명해줘.")

# wrapped_text = textwrap.fill(response.content, width=40)
# print(wrapped_text)
# # ------------------

# 2안) 역할부여 및 질의응답
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 부동산 및 건물관리(FM/PM) 산업 전문 경영 전략 컨설턴트입니다."),
        ("user", """현시점 대한민국 건물관리 회사가 직면한 구조적 현실과 위기를 극복하기 위한 핵심 생존 전략 3가지를 두괄식으로 제언해 줘.
반드시 마크다운 표, 소제목, 글머리 기호를 활용하여 사람이 읽기 쉬운 비즈니스 보고서 형태로 작성해 줘."""),
    ]
)

# 3. 체인(Chain) 구성
chain = prompt | llm

# 4. 체인 실행(chain.invoke)
def generate_building_management_report():
    try:
        print("=== Ollama 활용 보고서 생성 중... ===")

        # 로컬 LLM 실행 (네트워크 요청 대신 체인 invoke 사용)
        response = chain.invoke({})
        report_content = response.content

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_report = f"""# 건물관리(FM/PM) 산업 현실 및 생존 전략
- **작성 일시:** {current_time}

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
