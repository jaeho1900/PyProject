# ======================
# 폴더 안의 모든 파일을 하나의 DataFrame으로 통합
# ======================

import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# 1. 폴더 선택 창 열기
root = tk.Tk()
root.withdraw()

folder_selected = filedialog.askdirectory(
    title="Excel 파일이 있는 폴더를 선택하세요"
)

if not folder_selected:
    print("폴더가 선택되지 않았습니다.")
else:
    folder_path = Path(folder_selected)

    # 2. Excel 파일 목록 가져오기
    excel_files = [
        file_path
        for file_path in folder_path.iterdir()
        if file_path.suffix.lower() in [".xlsx", ".xls"]
    ]

    if not excel_files:
        print("선택한 폴더에 Excel 파일이 없습니다.")
    else:
        dataframes = []

        # 3. 모든 Excel 파일과 시트 읽기
        for file_path in excel_files:
            try:
                # sheet_name=None: 모든 시트를 딕셔너리 형태로 읽음
                sheets = pd.read_excel(
                    file_path,
                    sheet_name=None
                )

                for sheet_name, df in sheets.items():

                    # 완전히 빈 데이터프레임 제외
                    if df.empty:
                        continue

                    # 출처 정보 추가
                    df["원본파일명"] = file_path.name
                    df["시트명"] = sheet_name

                    dataframes.append(df)

                print(f"읽기 완료: {file_path.name}")

            except Exception as error:
                print(f"읽기 실패: {file_path.name}")
                print(f"오류 내용: {error}")

        # 4. 데이터프레임 통합
        if dataframes:
            combined_df = pd.concat(
                dataframes,
                ignore_index=True
            )

            # 5. Parquet 파일 저장
            output_path = folder_path / "통합데이터.parquet"

            combined_df.to_parquet(
                output_path,
                index=False,
                engine="pyarrow"
            )

            # combined_df.to_excel(folder_path / "통합데이터.xlsx", index=False)

            print("\n통합 완료")
            print(f"행 개수: {len(combined_df):,}")
            print(f"열 개수: {len(combined_df.columns):,}")
            print(f"저장 위치: {output_path}")

        else:
            print("통합할 데이터가 없습니다.")

# 총작업시간(분) 수정 ----------------------

# 시작일 ~ 완료일 작업을 24시간 작업으로 처리된 부분을 1일 8시간으로 수정

# 숫자형 변환 및 결측치 처리 (공란인 경우 0으로 처리)
df['작업시간(분)'] = pd.to_numeric(df['작업시간(분)'], errors='coerce').fillna(0)
df['총작업시간(분)'] = pd.to_numeric(df['총작업시간(분)'], errors='coerce').fillna(0)

# 작업시간(분) 기준 보정 시간 계산
step1_calc = np.select(
    [
        df['작업시간(분)'] <= 480,
        (df['작업시간(분)'] > 480) & (df['작업시간(분)'] <= 1440),
        df['작업시간(분)'] > 1440
    ],
    [
        df['작업시간(분)'],
        480,
        df['작업시간(분)'] - ((df['작업시간(분)'] // 1440) * 960)
    ],
    default=0
)

# 총작업시간 // 작업시간) * 1단계 결과 계산하여 '총작업시간(분)_E' 컬럼 생성
# 작업시간이 0인 경우 0으로 처리하여 ZeroDivisionError 방지
multiplier = np.where(df['작업시간(분)'] > 0, df['총작업시간(분)'] // df['작업시간(분)'], 0)
df['총작업시간(분)_E'] = multiplier * step1_calc
