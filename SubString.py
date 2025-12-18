import os

folder_path = r"E:\12345"

# 해당 폴더가 존재하는지 확인
if not os.path.exists(folder_path):
    print(f"Error: The folder '{folder_path}' does not exist.")
else:
    # 폴더 내의 모든 파일 목록 가져오기
    try:
        files = os.listdir(folder_path)

        for filename in files:
            # 파일 이름이 2글자보다 길 때만 변경
            if len(filename) > 2:
                old_filepath = os.path.join(folder_path, filename)
                new_filename = filename[2:] # 앞의 2글자 제외
                new_filepath = os.path.join(folder_path, new_filename)

                # 파일명 변경
                os.rename(old_filepath, new_filepath)
                print(f"Renamed: '{filename}' -> '{new_filename}'")
            else:
                print(f"Skipped: '{filename}' (filename is 2 characters or less)")

    except Exception as e:
        print(f"An error occurred: {e}")
