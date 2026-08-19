import pandas as pd

file_path = r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
df = pd.read_parquet(file_path)

# 3. '주기' 컬럼 결측치 및 빈 문자열을 '수시'로 채우기
df["주기"] = df["주기"].fillna("수시").replace(r"^\s*$", "수시", regex=True)

# 4. '서비스LV1'이 '시설'인 데이터 필터링
df_filtered = df[df["서비스LV1"] == "시설"].copy()

# 5. '총작업시간(분)' 컬럼이 숫자가 아닐 경우를 대비해 수치형 변환
df_filtered["총작업시간(분)"] = pd.to_numeric(
    df_filtered["총작업시간(분)"], errors="coerce"
)

# 6. 그룹화 및 통계치(합계, 중앙값, 데이터 개수) 산출
result = (
    df_filtered.groupby(["운영센터명", "서비스LV2", "주기"])["총작업시간(분)"]
    .agg(합계="sum", 중앙값="median", 데이터갯수="count")
    .reset_index()
)

# 7. 결과 확인
print(result)

# 필요 시 엑셀 또는 CSV로 저장
result.to_excel(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과.xlsx", index=False)
# result.to_parquet(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과.parquet', index=False)


df[(df["주기"] == "6년")]
df[(df["운영센터명"] == "YTN상암PFM") & (df["주기"] == "6년")]

