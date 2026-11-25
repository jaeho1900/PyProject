import os
import urllib3
from dotenv import load_dotenv
from datetime import datetime
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
api_key = os.getenv("EXAONE_API_KEY")
if api_key:
    print("API 키를 성공적으로 불러왔습니다!")
else:
    print("경고: API 키를 찾을 수 없습니다. .env 파일을 확인하세요.")

url = "https://api.exaone.ai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

strategic_prompt = """
현시점 대한민국 건물관리 회사가 직면한 구조적 현실과 위기를 극복하기 위한 핵심 생존 전략 3가지를 두괄식으로 제언해 줘.
반드시 마크다운 표, 소제목, 글머리 기호를 활용하여 사람이 읽기 쉬운 비즈니스 보고서 형태로 작성해 줘.
"""

payload = {
    "model": "k-exaone_v2.5",
    "messages": [
        {
            "role": "system",
            "content": "당신은 부동산 및 건물관리(FM/PM) 산업 전문 경영 전략 컨설턴트입니다."
        },
        {
            "role": "user",
            "content": strategic_prompt
        }
    ],
    "temperature": 0.9,
    "reasoning_effort": "low",
    "max_tokens": 4096,
    "stream": False,
    "top_p": 0.95
}

def generate_building_management_report():
    try:
        print("=== 보고서 생성 중... ===")
        # 타임아웃을 300초로 상향
        response = requests.post(url=url, headers=headers, json=payload, timeout=300, verify=False)

        if response.status_code == 200:
            res_json = response.json()

            # 실제 모델이 생성한 답변 텍스트 추출 (message.content)
            message_data = res_json.get("choices", [{}])[0].get("message", {})
            report_content = message_data.get("content", "")

            # 만약 content가 비어있고 reasoning_content만 있는 경우 대비 예외 처리
            if not report_content and "reasoning_content" in message_data:
                print("[알림] content 필드가 비어 있어 내부 추론 내용을 대체 출력합니다.")
                report_content = message_data.get("reasoning_content", "")

            if not report_content:
                print("\n[경고] 서버로부터 수신된 텍스트 내용이 없습니다.")
                print(f"전체 응답 JSON: {res_json}")
                return

            # 보고서 헤더 장식 (들여쓰기 제거하여 마크다운 깨짐 방지)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_report = (
                f"# [EXECUTIVE REPORT] 대한민국 건물관리(FM/PM) 산업 현실 및 생존 전략\n"
                f"- **작성 일시:** {current_time}\n"
                f"- **주관 부서:** 사업밸류업팀\n\n"
                f"---\n\n"
                f"{report_content}\n"
            )

            # 1. 콘솔에 출력
            print(formatted_report)

            # 2. 마크다운 파일(.md)로 자동 저장
            filename = f"Building_Management_Strategy_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(formatted_report)
            print(f"\n[성공] 보고서가 파일로 저장되었습니다: {filename}")

        else:
            print(f"API 요청 실패 (Status Code: {response.status_code})")
            print(f"응답 내용: {response.text}")

    except Exception as e:
        print(f"\n요청 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    generate_building_management_report()
