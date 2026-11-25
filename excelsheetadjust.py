import pandas as pd

# 파일 경로 설정
file_path = r"C:\Users\Administrator\Desktop\작업.xlsx"
output_path = r"C:\Users\Administrator\Desktop\작업_통합결과.xlsx"

try:
  # 1. 엑셀 파일의 모든 시트를 딕셔너리 형태로 읽어오기
  # 첨부 이미지의 헤더 구조(엑셀 기준 4번째 행)에 맞춰 header=3으로 지정했습니다.
  # 만약 헤더 위치가 다르다면 이 숫자를 조정해 주세요.
  sheets_dict = pd.read_excel(file_path, sheet_name=None, header=3)
  sheet_names = list(sheets_dict.keys())

  # 2. '서울1'부터 'U+사업팀'까지의 시트 이름 범위 추출
  start_idx = sheet_names.index("서울1")
  end_idx = sheet_names.index("U+사업팀")
  target_sheets = sheet_names[start_idx : end_idx + 1]

  print(f"병합 대상 시트 목록 ({len(target_sheets)}개): {target_sheets}")

  # 3. 대상 시트 데이터를 순회하며 병합 리스트에 담기
  combined_df_list = []
  for sheet_name in target_sheets:
    df = sheets_dict[sheet_name]

    # 완전히 빈 행은 제외
    df = df.dropna(how="all")

    # 데이터 출처를 알 수 있도록 원본 시트명 컬럼 추가 (선택 사항)
    df["소속"] = sheet_name

    combined_df_list.append(df)

  # 4. 데이터프레임 통합
  if combined_df_list:
    result_df = pd.concat(combined_df_list, ignore_index=True)

    # 5. 결과 파일을 새로운 엑셀 파일로 저장 ('통합시트' 이름으로 생성)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
      result_df.to_excel(writer, sheet_name="통합시트", index=False)

    print(f"모든 시트가 성공적으로 병합되었습니다!\n저장 경로: {output_path}")
  else:
    print("병합할 데이터가 없습니다.")

except ValueError as e:
  print(
      f"시트 이름을 찾는 중 오류가 발생했습니다. '서울1' 또는 'U+사업팀' 시트"
      f" 이름을 확인해주세요.\n상세 에러: {e}"
)
except Exception as e:
  print(f"작업 중 오류가 발생했습니다: {e}")
