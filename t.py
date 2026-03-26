import os
import re
from bs4 import BeautifulSoup

folder_path = r"C:\Users\Administrator\Desktop\foldd"  # 대상 폴더 경로
output_file = os.path.join(folder_path, "merged_vertical.html")

# ✅ 숫자 기준 정렬 (3,4,5,...16)
def numeric_sort_key(filename):
    numbers = re.findall(r'\d+', filename)
    return int(numbers[0]) if numbers else float('inf')

html_files = [f for f in os.listdir(folder_path) if f.endswith(".html")]
html_files.sort(key=numeric_sort_key)

merged_head_tags = []
merged_body_content = ""
seen_head_elements = set()

for file in html_files:
    file_path = os.path.join(folder_path, file)

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

        # ✅ head 통합 (디자인 유지)
        if soup.head:
            for tag in soup.head.find_all(["link", "style", "script"]):
                tag_str = str(tag)
                if tag_str not in seen_head_elements:
                    merged_head_tags.append(tag_str)
                    seen_head_elements.add(tag_str)

        # ✅ body → 세로 페이지 블록 생성
        if soup.body:
            section = f"""
<div class="page">
    <div class="page-inner">
        {soup.body.decode_contents()}
    </div>
</div>
"""
            merged_body_content += section

# ✅ 최종 HTML (Vertical 레이아웃 핵심 적용)
final_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Merged Vertical Pages</title>

{''.join(merged_head_tags)}

<style>

/* 🔑 핵심: 완전한 세로 흐름 */
body {{
    display: flex;
    flex-direction: column;  /* 👉 Vertical */
    align-items: stretch;
    margin: 0;
    padding: 20px;
    background: #f0f0f0;
}}

/* 🔑 각 HTML을 독립 페이지처럼 */
.page {{
    width: 100%;
    margin-bottom: 50px;
}}

/* 🔑 콘텐츠 영역 (겹침 방지 핵심) */
.page-inner {{
    width: 90%;
    margin: 0 auto;
    background: white;
    padding: 30px;

    /* 🔥 핵심 설정 */
    position: relative;
    display: block;
    overflow: visible;
    height: auto;

    box-sizing: border-box;
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
}}

/* float 레이아웃 깨짐 방지 */
.page-inner::after {{
    content: "";
    display: block;
    clear: both;
}}

/* 이미지 overflow 방지 */
img {{
    max-width: 100%;
    height: auto;
}}

</style>

</head>
<body>

{merged_body_content}

</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_html)

print("Vertical 병합 완료:", output_file)
