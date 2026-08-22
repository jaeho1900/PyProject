import pandas as pd
import numpy as np

# 메모리 부족하면 "필요한 컬럼만" 선택하여 고속으로 로드
# df_subset = pd.read_parquet("data.parquet", columns=["거래ID", "금액"])

file_path = r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
df = pd.read_parquet(file_path, index=False, engine="pyarrow", dtype_backend="pyarrow")

# 정제 ----------------------

# 특정 운영센터 제외
exclude_centers = ["마포", "에너지솔루션과천연구소"]
df = df[~df["운영센터명"].isin(exclude_centers)].reset_index(drop=True)

# 빈칸 -> "수시"
df["주기"] = df["주기"].fillna("수시").replace(r"^\s*$", "수시", regex=True)

# "오피스", "연구소" 분류 추가
office_list = ['트윈타워', '서울역빌딩', 'YTN상암PFM', '건와빌딩']
lab_list = ['전자양재R&D캠퍼스', '전자가산R&D캠퍼스', '전자서초R&D']
conditions = [
    df['운영센터명'].isin(office_list),
    df['운영센터명'].isin(lab_list)
]
choices = ['오피스', '연구소']
df['분류'] = np.select(conditions, choices, default='기타')

# "서비스LV1" == "시설" 필터링
df = df[df["서비스LV1"] == "시설"]

# "총작업시간(분)"" == NaN 필터링
# df["총작업시간(분)"].isna().sum()
df = df[df["총작업시간(분)"].notna()]

# 점검 파일 생성
# df.to_excel(r"C:\Users\Administrator\Desktop\seven_facility.xlsx", index=False)

# 통계 ----------------------
# 그룹핑 및 통계치(합계, 중앙값, 데이터 개수) 산출
result = (
    df.groupby(["분류", "운영센터명", "서비스LV2", "주기"])["총작업시간(분)"]
    .agg(합계="sum", 평균값="mean", 중앙값="median", 데이터갯수="count")
    .reset_index()
)

# 저장 ----------------------
result.to_excel(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과1.xlsx", index=False)
# result.to_parquet(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과.parquet', index=False, engine="pyarrow", compression="snappy")

# 내용 확인 ----------------------
df[(df["주기"] == "6년")]
