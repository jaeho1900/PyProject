# ----------------------
# atG 작업관리 분석
# ----------------------

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# 호출 ----------------------

file_path = r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
df = pd.read_parquet(file_path, engine="pyarrow", dtype_backend="pyarrow")

# df_subset = pd.read_parquet(file_path, columns=["서비스LV1", "서비스LV2"])

# 파악 ----------------------

df.columns
df.info()
df.count()   # NaN이 아닌 데이터의 수

df.head()
df[df["총작업시간(분)"] == 0]
df[df["총작업시간(분)"].isna()]

df.describe()
df[(df["총작업시간(분)"] < 0.68) | (df["총작업시간(분)"] > 40)]

# 필터링 파악 ----------------------

df["서비스LV1"].unique()

re = df[df["서비스LV1"] == "시설"]  # '검침', '보수', '운전', '점검', '시설순찰', '진단[Patrol]', '예방정비', '법정검사/신고'
re = df[df["서비스LV1"] == "관리"]  # 센터업무
re = df[df["서비스LV1"] == "PM"]   # 회계관리(YTN 만 존재)
re["서비스LV2"].unique()
re["작업명"].unique()
re["운영센터명"].unique()
re["총작업시간(분)"].describe()
re["총작업시간(분)"].sum()

df = df[df["서비스LV1"].isin(["시설", "관리"])]

# 그룹링 파악 ----------------------

result = (
    df.groupby(["분류", "운영센터명", "서비스LV2", "주기"])["총작업시간(분)"]
    .agg(합계="sum", 평균값="mean", 중앙값="median", 데이터갯수="count")
    .reset_index()
)


# 시각화 ----------------------

# 저장 ----------------------
result.to_excel(r"C:\Users\Administrator\Desktop\시설_작업시간_분석결과_{datetime.now().strftime('%y%m%d%H%M%S')}.xlsx", index=False)

