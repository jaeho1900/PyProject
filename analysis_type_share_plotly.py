from pathlib import Path
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ------------------------------------------------------------
# 0. 설정
# ------------------------------------------------------------
INPUT = Path(r'C:\Users\Thanki\Desktop\Integrated_data.xlsx')
OUTDIR = INPUT.parent / 'analysis_type_share_plotly'
OUTDIR.mkdir(parents=True, exist_ok=True)
# os.makedirs(OUTDIR, exist_ok=True)

CENTER = "운영센터"
CLASS = "분류"                 # 연구소 / 오피스
SERVICE = "서비스LV2"
EQUIPMENT = "표준설비"
RECORD_ID = "_record_id"

# 분석에 포함할 분류 및 상위 유형 수
CLASS_ORDER = ["연구소", "오피스"]
TOP_N_SERVICE = 12
TOP_N_EQUIPMENT = 20

# ------------------------------------------------------------
# 1. 원자료 적재 및 기본 정제
# ------------------------------------------------------------
df = pd.read_excel(INPUT)
df = df.copy()
df[RECORD_ID] = np.arange(len(df))

required = [CENTER, CLASS, SERVICE, EQUIPMENT]
missing = [c for c in required if c not in df.columns]
if missing:
    raise KeyError(f"필수 컬럼이 없습니다: {missing}")

df = df[df[CLASS].isin(CLASS_ORDER)].copy()
for c in [CENTER, CLASS, SERVICE, EQUIPMENT]:
    df[c] = df[c].astype("string").str.strip()

# 표준설비 결측은 유형 비교에서 제외하되, 서비스LV2 분석은 모두 포함
service_df = df.dropna(subset=[SERVICE]).copy()
equipment_df = df.dropna(subset=[EQUIPMENT]).copy()

# ------------------------------------------------------------
# 2. 핵심 함수: 운영센터 내부 비율 → 분류별 평균
# ------------------------------------------------------------
def center_normalized_share(data, type_col, classes=CLASS_ORDER):
    """
    각 운영센터-분류 안에서 유형별 비율을 계산한다.
    이후 분류별로 운영센터 평균(macro average)을 내므로
    작업량이 큰 운영센터가 결과를 독점하지 않는다.
    """
    counts = (
        data.groupby([CENTER, CLASS, type_col], observed=True)
             .size()
             .rename("records")
             .reset_index()
    )

    # 각 운영센터-분류의 전체 기록 수
    denom = (
        counts.groupby([CENTER, CLASS], observed=True)["records"]
              .sum()
              .rename("center_class_records")
              .reset_index()
    )
    counts = counts.merge(denom, on=[CENTER, CLASS], how="left", validate="many_to_one")
    counts["within_center_share"] = counts["records"] / counts["center_class_records"]

    # 모든 센터에 유형이 없는 경우도 0으로 반영하기 위한 센터 목록
    centers = data[[CENTER, CLASS]].drop_duplicates()
    types = counts[[type_col]].drop_duplicates()
    grid = centers.merge(types, how="cross")
    counts = grid.merge(
        counts[[CENTER, CLASS, type_col, "records", "center_class_records", "within_center_share"]],
        on=[CENTER, CLASS, type_col], how="left"
    )
    counts["records"] = counts["records"].fillna(0).astype(int)
    counts["center_class_records"] = counts["center_class_records"].fillna(0)
    counts["within_center_share"] = counts["within_center_share"].fillna(0.0)

    # 분류별 평균/중앙값: 센터별 비율을 동일 가중치로 집계
    summary = (
        counts.groupby([CLASS, type_col], observed=True)
              .agg(
                  mean_share=("within_center_share", "mean"),
                  median_share=("within_center_share", "median"),
                  sd_share=("within_center_share", "std"),
                  centers_observed=("within_center_share", lambda s: int((s > 0).sum())),
                  n_centers=(CENTER, "nunique"),
              )
              .reset_index()
    )
    summary["sd_share"] = summary["sd_share"].fillna(0)
    summary["share_pct"] = summary["mean_share"] * 100
    summary["median_pct"] = summary["median_share"] * 100
    summary["sd_pct"] = summary["sd_share"] * 100

    # 연구소-오피스 차이: 양수면 연구소 비율이 높음
    pivot = summary.pivot(index=type_col, columns=CLASS, values="mean_share").fillna(0)
    for c in CLASS_ORDER:
        if c not in pivot.columns:
            pivot[c] = 0
    pivot["연구소_minus_오피스"] = pivot["연구소"] - pivot["오피스"]
    pivot["abs_difference"] = pivot["연구소_minus_오피스"].abs()
    diff = pivot.reset_index().sort_values("abs_difference", ascending=False)
    return counts, summary, diff

service_center, service_summary, service_diff = center_normalized_share(service_df, SERVICE)
equip_center, equip_summary, equip_diff = center_normalized_share(equipment_df, EQUIPMENT)

# ------------------------------------------------------------
# 3. 상위 유형 선정: 두 분류 중 한 곳이라도 비율이 높은 유형
# ------------------------------------------------------------
def select_top_types(summary, type_col, n):
    p = summary.pivot(index=type_col, columns=CLASS, values="mean_share").fillna(0)
    for c in CLASS_ORDER:
        if c not in p.columns:
            p[c] = 0
    p["max_share"] = p[CLASS_ORDER].max(axis=1)
    return p.sort_values("max_share", ascending=False).head(n).index.tolist()

service_top = select_top_types(service_summary, SERVICE, TOP_N_SERVICE)
equip_top = select_top_types(equip_summary, EQUIPMENT, TOP_N_EQUIPMENT)

# ------------------------------------------------------------
# 4. 표 출력 및 저장
# ------------------------------------------------
def export_tables(summary, diff, type_col, name):
    out_summary = summary[summary[type_col].isin(
        select_top_types(summary, type_col, TOP_N_SERVICE if type_col == SERVICE else TOP_N_EQUIPMENT)
    )].copy()
    out_summary = out_summary.sort_values([CLASS, "mean_share"], ascending=[True, False])
    out_diff = diff.copy()
    out_summary.to_csv(f"{OUTDIR}/{name}_center_normalized_summary.csv", index=False, encoding="utf-8-sig")
    out_diff.to_csv(f"{OUTDIR}/{name}_research_vs_office_difference.csv", index=False, encoding="utf-8-sig")
    return out_summary, out_diff

service_out, service_diff_out = export_tables(service_summary, service_diff, SERVICE, "service_lv2")
equip_out, equip_diff_out = export_tables(equip_summary, equip_diff, EQUIPMENT, "standard_equipment")

# ------------------------------------------------------------
# 5. Plotly 시각화
# ------------------------------------------------------------
def grouped_bar(summary, type_col, selected, title, filename):
    p = summary[summary[type_col].isin(selected)].copy()
    p = p.sort_values("mean_share", ascending=True)
    fig = px.bar(
        p,
        x="share_pct",
        y=type_col,
        color=CLASS,
        orientation="h",
        barmode="group",
        category_orders={CLASS: CLASS_ORDER},
        color_discrete_map={"연구소": "#1f77b4", "오피스": "#ff7f0e"},
        title=title,
        labels={"share_pct": "운영센터 내부 평균 비율(%)", type_col: "작업 유형", CLASS: "분류"},
        hover_data={"share_pct": ":.2f", "median_pct": ":.2f", "sd_pct": ":.2f", "centers_observed": True},
    )
    fig.update_layout(template="plotly_white", height=max(550, 28 * len(selected) + 150), legend_title_text="")
    fig.update_xaxes(ticksuffix="%", rangemode="tozero")
    fig.write_html(f"{OUTDIR}/{filename}", include_plotlyjs="cdn")
    return fig

fig_service = grouped_bar(
    service_summary, SERVICE, service_top,
    "서비스LV2: 운영센터 내부 비율 기준 연구소 vs 오피스",
    "service_lv2_center_normalized.html",
)
fig_equip = grouped_bar(
    equip_summary, EQUIPMENT, equip_top,
    "표준설비: 운영센터 내부 비율 기준 연구소 vs 오피스",
    "standard_equipment_center_normalized.html",
)

# 차이 중심 막대그래프: 연구소 비중 - 오피스 비중

def difference_bar(diff, type_col, title, filename, n=20):
    p = diff.head(n).copy().sort_values("연구소_minus_오피스")
    p["direction"] = np.where(p["연구소_minus_오피스"] >= 0, "연구소 높음", "오피스 높음")
    fig = px.bar(
        p,
        x="연구소_minus_오피스",
        y=type_col,
        color="direction",
        orientation="h",
        color_discrete_map={"연구소 높음": "#1f77b4", "오피스 높음": "#ff7f0e"},
        title=title,
        labels={"연구소_minus_오피스": "연구소 비율 - 오피스 비율(%p)", type_col: "작업 유형", "direction": "차이 방향"},
        hover_data={"연구소_minus_오피스": ":.2f", "연구소": ":.2%", "오피스": ":.2%"},
    )
    fig.add_vline(x=0, line_width=1, line_color="black")
    fig.update_layout(template="plotly_white", height=max(550, 28 * len(p) + 150), legend_title_text="")
    fig.update_xaxes(ticksuffix="%p")
    fig.write_html(f"{OUTDIR}/{filename}", include_plotlyjs="cdn")
    return fig

fig_service_diff = difference_bar(
    service_diff, SERVICE,
    "서비스LV2: 연구소와 오피스의 운영센터 내부 비율 차이",
    "service_lv2_research_office_difference.html",
    n=TOP_N_SERVICE,
)
fig_equip_diff = difference_bar(
    equip_diff, EQUIPMENT,
    "표준설비: 연구소와 오피스의 운영센터 내부 비율 차이",
    "standard_equipment_research_office_difference.html",
    n=TOP_N_EQUIPMENT,
)

# 운영센터별 비율 heatmap: 분류별로 별도 생성

def heatmap_center(data, type_col, selected, class_value, title, filename):
    p = data[(data[CLASS] == class_value) & (data[type_col].isin(selected))].copy()
    piv = p.pivot(index=type_col, columns=CENTER, values="within_center_share").fillna(0) * 100
    piv = piv.loc[piv.mean(axis=1).sort_values().index]
    fig = px.imshow(
        piv,
        aspect="auto",
        color_continuous_scale="Blues",
        text_auto=".1f",
        labels={"x": "운영센터", "y": "작업 유형", "color": "센터 내부 비율(%)"},
        title=title,
    )
    fig.update_layout(template="plotly_white", height=max(550, 25 * len(selected) + 150))
    fig.write_html(f"{OUTDIR}/{filename}", include_plotlyjs="cdn")
    return fig

for cls in CLASS_ORDER:
    heatmap_center(service_center, SERVICE, service_top, cls, f"서비스LV2 - {cls}: 운영센터 내부 비율", f"service_lv2_{cls}_heatmap.html")
    heatmap_center(equip_center, EQUIPMENT, equip_top, cls, f"표준설비 - {cls}: 운영센터 내부 비율", f"standard_equipment_{cls}_heatmap.html")

# ------------------------------------------------------------
# 6. 콘솔에서 핵심 결과 확인
# ------------------------------------------------------------
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 180)
print("[서비스LV2] 연구소-오피스 차이 상위")
print(service_diff.head(TOP_N_SERVICE).to_string(index=False))
print("\n[표준설비] 연구소-오피스 차이 상위")
print(equip_diff.head(TOP_N_EQUIPMENT).to_string(index=False))
print("\n생성 파일:")
for f in sorted(os.listdir(OUTDIR)):
    if f.endswith((".csv", ".html")):
        print(os.path.join(OUTDIR, f))
