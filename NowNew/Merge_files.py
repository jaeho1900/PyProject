# ======================
# 특정 폴더 속의 모든 파일을 하나의 DataFrame으로 통합
# ======================

import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import pandas as pd

# 1. 폴더 선택 창 열기
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)  # 선택 창이 다른 창 뒤에 숨지 않도록 최상단 고정

folder_selected = filedialog.askdirectory(title="Excel 파일이 있는 폴더를 선택하세요")
root.destroy()

if not folder_selected:
    print("폴더가 선택되지 않았습니다.")
else:
    folder_path = Path(folder_selected)

    # 2. Excel 파일 목록 가져오기 (엑셀 임시 파일 '~$' 및 이전 통합 파일 제외)
    excel_files = [
        file_path
        for file_path in folder_path.iterdir()
        if file_path.suffix.lower() in [".xlsx", ".xls"]
        and not file_path.name.startswith("~$")
        and file_path.name not in ["통합데이터.xlsx", "통합데이터.parquet"]
    ]

    if not excel_files:
        print("선택한 폴더에 유효한 Excel 파일이 없습니다.")
    else:
        dataframes = []

        # 3. 모든 Excel 파일과 시트 읽기
        for file_path in excel_files:
            try:
                # sheet_name=None: 모든 시트를 딕셔너리 형태로 로드
                sheets = pd.read_excel(file_path, sheet_name=None)

                for sheet_name, df in sheets.items():
                    if df.empty:
                        continue

                    # 원본 출처 컬럼 추가
                    df["원본파일명"] = file_path.name
                    df["시트명"] = str(sheet_name)

                    dataframes.append(df)

                print(f"읽기 완료: {file_path.name}")

            except Exception as error:
                print(f"읽기 실패: {file_path.name} | 오류: {error}")

        # 4. 데이터프레임 통합
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)

            # 5. 저장 경로 지정
            parquet_path = folder_path / "통합데이터.parquet"
            excel_path = folder_path / "통합데이터.xlsx"

            # Parquet 저장을 위한 혼합 컬럼 타입 처리 (열 이름 문자열 변환)
            combined_df.columns = combined_df.columns.astype(str)

            # 컬럼명의 줄바꿈(\n) 제거
            combined_df.columns = (
                combined_df.columns
                .astype(str)
                .str.replace("\n", " ", regex=False)
                .str.strip()
            )

            # 파일 저장
            combined_df.to_parquet(parquet_path, index=False, engine="pyarrow")
            combined_df.to_excel(excel_path, index=False)

            print("\n" + "=" * 30)
            print("통합 완료")
            print(f"행 개수: {len(combined_df):,}")
            print(f"열 개수: {len(combined_df.columns):,}")
            print(f"저장 위치: {folder_path}")
            print("=" * 30)
        else:
            print("통합할 유효 데이터가 없습니다.")
