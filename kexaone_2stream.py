import requests
import json
import os
import urllib3
from dotenv import load_dotenv
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
api_key = os.getenv("EXAONE_API_KEY")

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
        {"role": "system", "content": "당신은 부동산 및 건물관리(FM/PM) 산업 전문 경영 전략 컨설턴트입니다."},
        {"role": "user", "content": strategic_prompt}
    ],
    "temperature": 0.9,
    "reasoning_effort": "low",
    "max_tokens": 4096,
    "stream": True,
    "top_p": 0.95
}

def generate_building_management_report():
    try:
        print("=== 보고서 생성 중... (최대 300초 대기) ===\n")
        # 타임아웃을 300초로 넉넉하게 설정
        response = requests.post(url=url, headers=headers, json=payload, timeout=300, verify=False, stream=True)

        if response.status_code == 200:
            full_content = []

            for raw_line in response.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue

                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line

                if line.startswith("data: "):
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_json = json.loads(data_str)
                        choices = chunk_json.get("choices")

                        # [핵심 방어 코드] choices가 비어있거나 없으면 건너뜀 (list index out of range 방지)
                        if not choices:
                            continue

                        delta = choices[0].get("delta", {})
                        content_piece = delta.get("content", "")

                        if content_piece:
                            print(content_piece, end="", flush=True)
                            full_content.append(content_piece)

                    except json.JSONDecodeError:
                        continue

            report_content = "".join(full_content)

            # 답변이 완전히 비어있다면 서버 응답 점검 필요
            if not report_content:
                print("\n[경고] 서버로부터 수신된 텍스트 내용이 없습니다. 페이로드나 모델 상태를 확인하세요.")
                return

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_report = (
                f"# [EXECUTIVE REPORT] 대한민국 건물관리(FM/PM) 산업 현실 및 생존 전략\n"
                f"- **작성 일시:** {current_time}\n"
                f"- **주관 부서:** 사업밸류업팀\n\n"
                f"---\n\n"
                f"{report_content}\n"
            )

            filename = f"Building_Management_Strategy_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(formatted_report)
            print(f"\n\n[성공] 보고서가 파일로 저장되었습니다: {filename}")

        else:
            print(f"API 요청 실패 (Status Code: {response.status_code})")
            print(f"응답 내용: {response.text}")

    except Exception as e:
        print(f"\n요청 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    generate_building_management_report()
