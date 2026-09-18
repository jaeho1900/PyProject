"""
# 폴더의 모든 파일을 DataFrame 1개로 통합
"""

from datetime import datetime
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import numpy as np
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

    # 2. Excel 파일 목록 가져오기 (임시 파일 및 생성 결과 파일 제외)
    excel_files = [
        file_path
        for file_path in folder_path.iterdir()
        if file_path.suffix.lower() in [".xlsx", ".xls"]
        and not file_path.name.startswith("~$")
        and not file_path.name.startswith("작업완료_")
    ]

    if not excel_files:
        print("선택한 폴더에 유효한 Excel 파일이 없습니다.")
    else:
        dataframes = []
        has_error = False

        # 3. 모든 Excel 파일과 시트 읽기
        for file_path in excel_files:
            try:
                # sheet_name=None: 모든 시트를 딕셔너리 형태로 로드
                sheets = pd.read_excel(file_path, sheet_name=None)

                for sheet_name, df in sheets.items():
                    if df.empty:
                        continue

                    # 컬럼명의 모든 줄바꿈 및 모든 공백 완전 제거
                    df.columns = (
                        df.columns
                        .astype(str)
                        .str.replace(r"\s+", "", regex=True)
                    )

                    # 요구사항 1: '표준설비' 컬럼 존재 여부 확인
                    if "표준설비" not in df.columns:
                        print(f"\n[오류] 파일명: {file_path.name} (시트명: {sheet_name})")
                        print("작업관리에서 분류 숨기기를 해제 후 다운로드하십시오")
                        has_error = True
                        break

                    # 원본 출처 컬럼 추가
                    df["원본파일명"] = file_path.name
                    df["시트명"] = str(sheet_name)

                    dataframes.append(df)

                if has_error:
                    # '표준설비' 컬럼이 없으면 전체 작업 즉시 중지
                    sys.exit()

                print(f"읽기 완료: {file_path.name}")

            except Exception as error:
                if has_error:
                    # 이미 표준설비 미존재로 중지된 경우 추가 에러 메시지 없이 종료
                    sys.exit()
                print(f"읽기 실패: {file_path.name} | 오류: {error}")

        # 4. 데이터프레임 통합 및 저장
        if dataframes:
            combined_df = pd.concat(dataframes, ignore_index=True)

            # 필터링
            combined_df = combined_df[combined_df['서비스LV1'] == '시설']   # 검침,보수,운전,점검,시설순찰,진단[Patrol],예방정비,법정검사/신고 선정
            combined_df = combined_df[~combined_df['총작업시간(분)'].isna()] # 미운전설비, 작업발행오류 등으로 제외

            # 총작업시간(분) 수정: 시작일 ~ 완료일 작업을 24시간 작업으로 처리된 부분을 1일 8시간으로 수정
            combined_df['작업시간(분)'] = pd.to_numeric(combined_df['작업시간(분)'], errors='coerce').fillna(0)
            combined_df['총작업시간(분)'] = pd.to_numeric(combined_df['총작업시간(분)'], errors='coerce').fillna(0)

            step1_calc = np.select(
                [
                    combined_df['작업시간(분)'] <= 480,
                    (combined_df['작업시간(분)'] > 480) & (combined_df['작업시간(분)'] <= 1440),
                    combined_df['작업시간(분)'] > 1440
                ],
                [
                    combined_df['작업시간(분)'],
                    480,
                    combined_df['작업시간(분)'] - ((combined_df['작업시간(분)'] // 1440) * 960)
                ],
                default=0
            )
            multiplier = np.where(combined_df['작업시간(분)'] > 0, combined_df['총작업시간(분)'] // combined_df['작업시간(분)'], 0)
            combined_df['총작업시간(분)_E'] = multiplier * step1_calc

            # ★ 생성일시(YYYYMMDD_HHMMSS)를 포함한 파일명 설정
            now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"작업완료_{now_str}.xlsx"
            output_path = folder_path / output_filename

            combined_df.to_excel(output_path, index=False)

            print("\n" + "=" * 30)
            print("통합 완료")
            print(f"행 개수: {len(combined_df):,}")
            print(f"열 개수: {len(combined_df.columns):,}")
            print(f"저장 위치: {output_path}")
            print("=" * 30)
        else:
            print("통합할 유효 데이터가 없습니다.")
