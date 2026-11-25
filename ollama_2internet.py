from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from ddgs import DDGS

def fetch_web_search_data(query, max_results=5):
    """
    ddgs 모듈을 통해 인터넷에서 최신 건물관리/프롭테크 관련 트렌드를 검색합니다.
    (사내망/보안 환경 인증서 오류 방지를 위해 verify=False 적용)
    """
    print(f"=== [인터넷 서칭 중] 키워드: '{query}' ===")
    search_snippets = []
    try:
        with DDGS(verify=False) as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                title = r.get('title', '')
                body = r.get('body', '')
                url = r.get('href', '')
                search_snippets.append(f"- **제목:** {title}\n  **요약:** {body}\n  **출처:** {url}")
        print("[성공] 최신 웹 데이터를 성공적으로 수집했습니다.\n")
    except Exception as e:
        print(f"[경고] 웹 검색 중 오류가 발생했습니다: {e}")
        search_snippets.append("- 웹 검색 데이터를 가져오지 못했습니다. 사전 학습된 지식을 기반으로 작성합니다.")

    return "\n\n".join(search_snippets)

# 1. llm 객체 생성
llm = ChatOllama(
    model="qwen2.5:3b",
    # model="exaone3.5:7.8b",
    temperature=0.4,
)

# 2. 템플릿 정의
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """당신은 국내 최고 권위의 프롭테크 및 부동산 빌딩관리(FM/PM) 산업 수석 경영 전략 컨설턴트입니다.
제공된 실시간 웹 검색 데이터와 최신 산업 동향을 바탕으로, 기존의 틀에 박힌 형식을 탈피하고 최고 경영진이 즉시 의사결정에 활용할 수 있는 최고급 전략 보고서를 작성해 주세요.
보고서 구조(Executive Summary, 시장 환경 분석, 구조적 리스크, 다차원 생존 전략, 실행 로드맵 및 KPI)를 스스로 최적화하여 구성하세요."""
        ),
        (
            "user",
            """아래의 최신 웹 검색 참고 자료를 분석하고, 형식의 제약 없이 가장 전문적이고 통찰력 있는 '대한민국 건물관리(FM/PM) 산업 구조적 현실 및 생존 전략' 보고서를 작성해 줘.

[실시간 웹 검색 참고 자료]
{search_context}

[작성 필수 지침]
1. 두괄식으로 핵심 메시지를 명확히 전달할 것.
2. 마크다운 표, 소제목, 글머리 기호를 적극 활용하여 가독성을 극대화할 것.
3. 단순한 정보 나열을 지양하고, 현업 실무 및 경영진 관점에서 실효성 있는 인사이트와 대안을 도출할 것."""
        ),
    ]
)

# 3. 체인(Chain) 구성
chain = prompt | llm

# 4. 체인 실행(chain.invoke)
def generate_intelligent_report():
    try:
        # Step 1: ddgs를 활용한 최신 트렌드 서칭
        search_query = "대한민국 건물관리 FM PM 트렌드 스마트건물 유지관리 위기"
        search_context = fetch_web_search_data(search_query, max_results=5)

        print("=== [로컬 LLM 분석 및 보고서 생성 중...] ===")

        # Step 2: 수집된 웹 컨텍스트를 로컬 LLM에 전달
        response = chain.invoke({"search_context": search_context})
        report_content = response.content

        # Step 3: 보고서 메타데이터 포맷팅
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_report = f"""# [EXECUTIVE STRATEGIC REPORT] 대한민국 건물관리(FM/PM) 산업 고도화 및 생존 전략
- **작성 일시:** {current_time}
- **주관 부서:** 사업밸류업팀

---

{report_content}
"""

        # Step 4: 콘솔 출력 및 마크다운 파일 저장
        print(formatted_report)

        filename = f"Advanced_Building_Management_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_report)
        print(f"\n[성공] 고품질 보고서가 파일로 안전하게 저장되었습니다: {filename}")

    except Exception as e:
        print(f"보고서 생성 프로세스 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    generate_intelligent_report()
