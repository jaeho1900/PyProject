import pandas as pd

file_path = r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
df = pd.read_parquet(file_path)

# 정제 ----------------------
# 빈칸 -> "수시"
df["주기"] = df["주기"].fillna("수시").replace(r"^\s*$", "수시", regex=True)

# '서비스LV1' == '시설' 이고 '총작업시간(분)' == NaN 필터링
df_filtered = df[df["서비스LV1"] == "시설"].copy()
# df_filtered.dtypes
# df_filtered[df_filtered["총작업시간(분)"].isna()]
df_filtered = df_filtered[df_filtered["총작업시간(분)"].notna()]

# df_filtered['운영센터명'].unique()

# 통계 ----------------------
# 그룹핑 및 통계치(합계, 중앙값, 데이터 개수) 산출
result = (
    df_filtered.groupby(["운영센터명", "서비스LV2", "주기"])["총작업시간(분)"]
    .agg(합계="sum", 평균값="mean", 중앙값="median", 데이터갯수="count")
    .reset_index()
)

# 저장 ----------------------
print(result)
result.to_excel(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과1.xlsx", index=False)
# result.to_parquet(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과.parquet', index=False)

# 내용 확인 ----------------------
df[(df["주기"] == "6년")]
df[(df["운영센터명"] == "YTN상암PFM") & (df["주기"] == "6년")]

