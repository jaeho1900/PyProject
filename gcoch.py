import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------------------------------
# 1. 데이터 로드 및 전처리
# -------------------------------------------------------------------------
file_path = (
    r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
)
df = pd.read_parquet(file_path)

exclude_centers = ["마포", "에너지솔루션과천연구소"]
df = df[~df["운영센터명"].isin(exclude_centers)].reset_index(drop=True)

# 빈칸 -> "수시"
df["주기"] = df["주기"].fillna("수시").replace(r"^\s*$", "수시", regex=True)

# "서비스LV1" == "시설" 필터링
df = df[df["서비스LV1"] == "시설"]

# 컬럼명 수치형 변환
df["총작업시간(분)"] = pd.to_numeric(df["총작업시간(분)"], errors="coerce")
df = df.dropna(subset=["총작업시간(분)"]).reset_index(drop=True)

# '분류' 컬럼 생성 (오피스 / 연구소)
office_list = ["트윈타워", "서울역빌딩", "YTN상암PFM", "건와빌딩"]
lab_list = ["전자양재R&D캠퍼스", "전자가산R&D캠퍼스", "전자서초R&D"]

conditions = [df["운영센터명"].isin(office_list), df["운영센터명"].isin(lab_list)]
choices = ["오피스", "연구소"]
df["분류"] = np.select(conditions, choices, default="기타")

# -------------------------------------------------------------------------
# 2. [집계 1] 운영센터 및 건물 유형별 분석
# -------------------------------------------------------------------------
center_summary = (
    df.groupby(["분류", "운영센터명"])
    .agg(
        작업건수=("No.", "count"),
        총작업시간_분=("총작업시간(분)", "sum"),
        평균작업시간_분=("총작업시간(분)", "mean"),
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
# 3. [집계 2] ('운영센터명', '개별설비/장소', '서비스LV2') 상세 그룹화
# -------------------------------------------------------------------------
facility_summary = (
    df.groupby(["분류", "운영센터명", "개별설비/장소", "서비스LV2"])["총작업시간(분)"]
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
    facility_summary["운영센터명"]
    + " | "
    + facility_summary["개별설비/장소"].astype(str)
    + " ("
    + facility_summary["서비스LV2"]
    + ")"
)

# -------------------------------------------------------------------------
# 4. Plotly 시각화 1: 운영센터별 총 작업시간 및 유형별 비중 대시보드
# -------------------------------------------------------------------------
fig1 = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        "운영센터별 총 작업시간(분)",
        "건물 분류별 발생유형 비중(%)",
    ),
    horizontal_spacing=0.12,
)

# 좌측: 센터별 총 작업시간 막대 차트
for category in ["오피스", "연구소"]:
    sub_data = center_summary[center_summary["분류"] == category]
    fig1.add_trace(
        go.Bar(
            x=sub_data["총작업시간_분"],
            y=sub_data["운영센터명"],
            orientation="h",
            name=f"{category} 작업시간",
        ),
        row=1,
        col=1,
    )

# 우측: 발생유형별 누적 비율 차트
for event in event_type_ratio["발생유형"].unique():
    sub_ratio = event_type_ratio[event_type_ratio["발생유형"] == event]
    fig1.add_trace(
        go.Bar(x=sub_ratio["분류"], y=sub_ratio["비율(%)"], name=event),
        row=1,
        col=2,
    )

fig1.update_layout(
    title_text="<b>[FM 작업 분석] 운영센터 및 건물 유형별 작업 패턴</b>",
    barmode="stack",
    template="plotly_white",
    height=550,
)
fig1.show(renderer="browser")  # 브라우저 새 탭으로 출력

# -------------------------------------------------------------------------
# 5. Plotly 시각화 2: 총 투입시간 상위 15대 설비/장소 (Treemap / Bar)
# -------------------------------------------------------------------------
top15_facility = facility_summary.sort_values(
    by="총작업시간_분", ascending=False
).head(15)

fig2 = px.bar(
    top15_facility.sort_values(by="총작업시간_분", ascending=True),
    x="총작업시간_분",
    y="설비라벨",
    color="분류",
    orientation="h",
    hover_data=["작업건수", "평균작업시간_분", "중앙작업시간_분"],
    title="<b>[상위 15개 고부하 설비/장소] 총 작업시간 및 평균 공수</b>",
    labels={
        "총작업시간_분": "총 작업시간 (분)",
        "설비라벨": "운영센터 | 설비/장소 (서비스)",
    },
    template="plotly_white",
    height=600,
)
fig2.show(renderer="browser")

# -------------------------------------------------------------------------
# 6. Plotly 시각화 3: 설비별 작업건수 vs 평균 작업시간 산점도 (공수 패턴 탐색)
# -------------------------------------------------------------------------
# 건수가 20건 이상인 유의미한 설비만 필터링
scatter_data = facility_summary[facility_summary["작업건수"] >= 20]

fig3 = px.scatter(
    scatter_data,
    x="작업건수",
    y="평균작업시간_분",
    size="총작업시간_분",
    color="서비스LV2",
    hover_name="설비라벨",
    log_x=True,
    title="<b>[설비별 공수 패턴] 작업 빈도(건수) vs 건당 평균 소요시간</b>",
    labels={
        "작업건수": "작업 발생건수 (Log Scale)",
        "평균작업시간_분": "건당 평균 작업시간 (분)",
    },
    template="plotly_white",
    height=600,
)
fig3.show(renderer="browser")

