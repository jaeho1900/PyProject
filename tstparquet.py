import pandas as pd
# import pyarrow as pa
# import pyarrow.parquet as pq

from_file = r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
to_file = r"C:\Users\Administrator\Desktop\to_오피스_연구소_엣지_작업데이터_통합.parquet"

df = pd.read_parquet(from_file)
# df_subset = pd.read_parquet(from_file, columns=["거래ID", "금액"])

unique_list = df['운영센터명'].unique().tolist()
print(unique_list)

filtered_df = df[df["운영센터명"] == "건와빌딩"]
filtered_df.to_excel(r"C:\Users\Administrator\Desktop\to_건와빌딩.xlsx")

# df.to_parquet(to_file, index=False)

# 그룹핑 기준 컬럼 리스트 정의 (실제 줄바꿈 '\n' 반영)
group_cols = [
    "서비스\nLV1",
    "서비스\nLV2",
    "층",
    "개별설비/장소",
    "작업명",
    "통합작업",
    "주기",
]

# 그룹별 평균 및 표준편차 계산
result = (
    filtered_df.groupby(group_cols)["총작업\n시간(분)"]
    .agg(평균="mean", 표준편차="std")
    .reset_index()
)

# (선택) 데이터가 1개여서 표준편차가 NaN으로 나오는 경우 0으로 채우기
result["표준편차"] = result["표준편차"].fillna(0)

# 4. 결과 확인 및 저장
print(result.head())
# result.to_excel("그룹별_작업시간_통계.xlsx", index=False)
# result.to_parquet("그룹별_작업시간_통계.parquet", index=False)

unique_list = df['작업명'].unique().tolist()
print(unique_list)






