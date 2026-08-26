import pandas as pd

excel_path = (
    r"C:\Users\Administrator\Desktop\오피스, 연구소 엣지 작업데이터_260811.xlsx"
)
output_parquet_path = (
    r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
)

all_sheets = pd.read_excel(excel_path, sheet_name=None, engine="calamine")

df_list = []
for sheet_name, df in all_sheets.items():
    if not df.empty:
        df.insert(0, "운영센터명", sheet_name)
        df_list.append(df)

combined_df = pd.concat(df_list, ignore_index=True)
combined_df.columns = combined_df.columns.str.replace("\n", "")
combined_df.to_parquet(output_parquet_path, engine="pyarrow", index=False)

print(f"총 {len(df_list)}개 시트 병합 완료!")
print(f"전체 데이터 행 수: {len(combined_df)}")
print(f"저장 경로: {output_parquet_path}")

# ---------------------
# 특정 운영센터 제외
df['운영센터명'].unique()

exclude_centers = ["마포", "에너지솔루션과천연구소"]
df = df[~df["운영센터명"].isin(exclude_centers)].reset_index(drop=True)

# 컬럼 추가: "오피스", "연구소" 분류
office_list = ['트윈타워', '서울역빌딩', 'YTN상암PFM', '건와빌딩']
lab_list = ['전자양재R&D캠퍼스', '전자가산R&D캠퍼스', '전자서초R&D']
conditions = [
    df['운영센터명'].isin(office_list),
    df['운영센터명'].isin(lab_list)
]
choices = ['오피스', '연구소']
df['분류'] = np.select(conditions, choices, default='기타')

# ---------------------

# 필터링 ----------------------
df = df[df["서비스LV1"] == "시설"]    # 검침,보수,운전,점검,시설순찰,진단[Patrol],예방정비,법정검사/신고
# df[df["서비스LV1"] == "관리"]       # 센터업무 > 작업명 ==> 데이터 누락/오류분 과다
# df[df["서비스LV1"] == "PM"]        # 회계관리 > 작업명 ==> YTN센터 1개센터만 DATA 존재
df = df[~df["총작업시간(분)"].isna()]

df.to_parquet(r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합1.parquet", index=False, engine="pyarrow", compression="snappy")

