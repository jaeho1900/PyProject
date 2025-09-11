import webbrowser
from datetime import datetime

def open_lg_pdf_url():
    """
    오늘 날짜를 기준으로 LG 스크랩 PDF 파일 URL을 생성하고 웹 브라우저에서 엽니다.
    """
    try:
        # 1. 오늘 날짜 정보 가져오기
        today = datetime.now()

        # 2. URL 형식에 맞게 날짜 포맷팅
        # yyyymm 형식 (예: 202310)
        yyyymm = today.strftime("%Y%m")
        # yyyymmdd 형식 (예: 20231026)
        yyyymmdd = today.strftime("%Y%m%d")

        # 3. f-string을 사용하여 최종 URL 생성
        url = f"https://image7.lg.co.kr/scrap/{yyyymm}/lg__{yyyymmdd}.pdf"

        # 4. 생성된 URL 출력 및 웹 브라우저에서 열기
        print(f"오늘의 PDF 파일 URL: {url}")
        print("웹 브라우저에서 해당 URL을 엽니다...")
        webbrowser.open(url)

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    open_lg_pdf_url()
