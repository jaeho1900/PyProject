import os
import re
from pathlib import Path

# 대상 폴더 경로
folder_path = r"D:\we\kbs"

# 파일명 패턴 (yyyy-mm-dd로 시작하는 파일)
pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})(.*)')

# 폴더 내 파일 순회
for filename in os.listdir(folder_path):
    # 디렉토리는 건너뛰기
    file_path = os.path.join(folder_path, filename)
    if os.path.isdir(file_path):
        continue

    # 패턴 매칭
    match = pattern.match(filename)
    if match:
        year, month, day, rest = match.groups()

        # 새 파일명 생성 (yy-mm-dd 형식)
        new_filename = f"{year[2:]}{month}{day}{rest}"
        new_file_path = os.path.join(folder_path, new_filename)

        # 파일명 변경
        try:
            os.rename(file_path, new_file_path)
            print(f"변경 완료: {filename} → {new_filename}")
        except Exception as e:
            print(f"오류 발생 ({filename}): {e}")
    else:
        print(f"패턴 불일치: {filename}")

print("\n파일명 변경 작업 완료!")
