"""
표준설비 분석 시각화
 - 상위15개 총 작업시간 및 평균 공수
 - 공수패턴: 작업 빈도(건수) vs 건당 평균 소요시간
"""

import pandas as pd
import plotly.express as px

file_path = (
    r"C:\Users\Administrator\Desktop\Integrated_data.parquet"
)
df = pd.read_parquet(file_path)

# 컬럼명 수치형 변환
df["총작업시간(분)_E"] = pd.to_numeric(df["총작업시간(분)_E"], errors="coerce")
df = df.dropna(subset=["총작업시간(분)_E"]).reset_index(drop=True)

# [집계 1] 운영센터 및 건물 유형별 분석
center_summary = (
    df.groupby(["분류", "운영센터"])
    .agg(
        작업건수=("No.", "count"),
        총작업시간_분=("총작업시간(분)_E", "sum"),
        평균작업시간_분=("총작업시간(분)_E", "mean"),
    )
    .reset_index()
    .sort_values(by=["분류", "총작업시간_분"], ascending=[True, False])
)

event_type_ratio = (
    pd.crosstab(df["분류"], df["발생유형"], normalize="index")
    .stack()
    .reset_index()
    .rename(columns={0: "비율(%)"})
)
event_type_ratio["비율(%)"] = (event_type_ratio["비율(%)"] * 100).round(2)

# -------------------------------------------------------------------------
# 1. [집계 2] ('운영센터명', '표준설비', '서비스LV2') 상세 그룹화
# -------------------------------------------------------------------------
facility_summary = (
    df.groupby(["분류", "운영센터", "표준설비", "서비스LV2"])["총작업시간(분)_E"]
    .agg(
        작업건수="count",
        총작업시간_분="sum",
        평균작업시간_분="mean",
        중앙작업시간_분="median",
        최대작업시간_분="max",
    )
    .reset_index()
)

facility_summary[["평균작업시간_분", "중앙작업시간_분", "총작업시간_분"]] = (
    facility_summary[
        ["평균작업시간_분", "중앙작업시간_분", "총작업시간_분"]
    ].round(2)
)

# 차트 라벨용 복합 명칭 생성
facility_summary["설비라벨"] = (
    facility_summary["운영센터"]
    + " | "
    + facility_summary["표준설비"].astype(str)
    + " ("
    + facility_summary["서비스LV2"]
    + ")"
)

# '서비스LV2'가 '보수'이거나 '표준설비'에 '건물'이 포함된 행을 제외
condition = (facility_summary['서비스LV2'] == '보수') | (facility_summary['표준설비'].str.contains('건물', na=False))
facility_summary = facility_summary[~condition].reset_index(drop=True)
facility_summary.to_csv(f'표준설비분류_기타분석.csv', index=False, encoding='utf-8-sig')

# -------------------------------------------------------------------------
# 2. Plotly 시각화: 총 투입시간 상위 15대 표준설비 (Treemap / Bar)
# -------------------------------------------------------------------------
top15_facility = facility_summary.sort_values(
    by="총작업시간_분", ascending=False
).head(15)

fig1 = px.bar(
    top15_facility.sort_values(by="총작업시간_분", ascending=True),
    x="총작업시간_분",
    y="설비라벨",
    color="분류",
    orientation="h",
    hover_data=["작업건수", "평균작업시간_분", "중앙작업시간_분"],
    title="<b>[상위 15개 고부하 표준설비] 총 작업시간 및 평균 공수</b>",
    labels={
        "총작업시간_분": "총 작업시간 (분)",
        "설비라벨": "운영센터 | 표준설비 (서비스)",
    },
    template="plotly_white",
    height=600,
)
fig1.show(renderer="browser")
fig1.write_html(f'상위15개고부하표준설비.html', include_plotlyjs='cdn')

# -------------------------------------------------------------------------
# 3. Plotly 시각화: 설비별 작업건수 vs 평균 작업시간 산점도 (공수 패턴 탐색)
# -------------------------------------------------------------------------
# 건수가 20건 이상인 유의미한 설비만 필터링
scatter_data = facility_summary[facility_summary["작업건수"] >= 20]

fig2 = px.scatter(
    scatter_data,
    x="작업건수",
    y="평균작업시간_분",
    size="총작업시간_분",
    color="서비스LV2",
    hover_name="설비라벨",
    log_x=True,
    title="<b>[표준설비별 공수 패턴] 작업 빈도(건수) vs 건당 평균 소요시간</b>",
    labels={
        "작업건수": "작업 발생건수 (Log Scale)",
        "평균작업시간_분": "건당 평균 작업시간 (분)",
    },
    template="plotly_white",
    height=600,
)
fig2.show(renderer="browser")
fig2.write_html(f'표준설비_공수_패턴.html', include_plotlyjs='cdn')
