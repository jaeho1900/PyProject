import webbrowser
from datetime import datetime

def open_teams_url():
    """
    오늘 날짜를 기준으로 LG 스크랩 PDF 파일 URL을 생성하고 웹 브라우저에서 엽니다.
    """
    try:
        # 4. 생성된 URL 출력 및 웹 브라우저에서 열기
        url = f"https://teams.microsoft.com/v2/#"
        print("웹 브라우저에서 해당 URL을 엽니다...")
        webbrowser.open(url)

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    open_teams_url()
