"""
설비분류별 작업건수 분석 시각화
"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# 0. 셋팅
# ============================================================
DATA_PATH = Path(r'C:\Users\Administrator\Desktop\Integrated_data.parquet')

if not DATA_PATH.exists():
    download_path = Path.home() / 'Downloads' / 'Integrated_data.xlsx'
    documents_path = Path.home() / 'Documents' / 'Integrated_data.xlsx'

    if download_path.exists():
        DATA_PATH = download_path
    elif documents_path.exists():
        DATA_PATH = documents_path
    else:
        raise FileNotFoundError(
            'Integrated_data.xlsx 파일을 찾을 수 없습니다.\n'
            f'확인한 경로: {DATA_PATH}\n'
            f'다운로드 폴더: {download_path}\n'
            f'문서 폴더: {documents_path}\n\n'
            'DATA_PATH를 실제 엑셀 파일 경로로 수정하세요.'
        )

OUTPUT_DIR = DATA_PATH.parent / 'facility_sla_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_LIST = ['연구소', '오피스']
CLASS_COL = '분류'
EQUIPMENT_COL = '표준설비'
LV1_COL = '설비분류LV1'

# 권장 기준
TARGET_RATIO = 0.20       # 전체 표준설비의 20%
MIN_CANDIDATES = 20       # 최소 후보군
MAX_CANDIDATES = 50       # 최대 후보군
MIN_PER_LV1 = 2           # 설비분류LV1별 최소 표준설비 수
SENSITIVITY_SIZES = [20, 30, 40, 50, 70]

# ============================================================
# 1. 로드
# ============================================================
df = pd.read_parquet(DATA_PATH, engine='pyarrow', dtype_backend='pyarrow')

required_cols = [CLASS_COL, EQUIPMENT_COL, LV1_COL]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    raise KeyError(f'필수 컬럼이 없습니다: {missing_cols}')

for col in required_cols:
    df[col] = df[col].astype('string').str.strip()

# 표준설비 결측은 설비 수 산정에서 제외
base = df.dropna(subset=[CLASS_COL, EQUIPMENT_COL]).copy()
base = base[base[CLASS_COL].isin(CLASS_LIST)].copy()

# ============================================================
# 2. 표준설비 파악
# ============================================================
def recommended_count(total_equipment, target_ratio=TARGET_RATIO,
                      minimum=MIN_CANDIDATES, maximum=MAX_CANDIDATES):
    """전체 표준설비의 일정 비율을 후보군 수로 변환하고 최소·최대 범위 적용."""
    ratio_count = int(np.ceil(total_equipment * target_ratio))
    return int(np.clip(ratio_count, minimum, maximum))

def minimum_required_count(data, class_name, min_per_lv1=MIN_PER_LV1):
    """모든 설비분류LV1을 포함하기 위해 필요한 최소 후보군 수."""
    x = data[data[CLASS_COL].eq(class_name)].copy()
    x = x.dropna(subset=[LV1_COL, EQUIPMENT_COL])

    # 분류별 표준설비 수가 1개인 경우에는 존재하는 1개까지만 요구
    lv1_counts = (
        x.groupby(LV1_COL)[EQUIPMENT_COL]
         .nunique()
    )
    required_by_lv1 = lv1_counts.clip(upper=min_per_lv1)
    return int(required_by_lv1.sum())

def make_recommendation(data, class_name):
    x = data[data[CLASS_COL].eq(class_name)].copy()
    total_equipment = x[EQUIPMENT_COL].nunique()

    ratio_recommendation = recommended_count(total_equipment)
    lv1_minimum = minimum_required_count(data, class_name)

    # 전체 표준설비 수보다 후보군 수가 커지지 않도록 제한
    final_recommendation = min(
        total_equipment,
        max(ratio_recommendation, lv1_minimum)
    )

    return {
        CLASS_COL: class_name,
        '전체표준설비수': total_equipment,
        '20%계산값': int(np.ceil(total_equipment * TARGET_RATIO)),
        '기본추천후보수': ratio_recommendation,
        '설비분류LV1최소조건수': lv1_minimum,
        '최종추천후보수': final_recommendation,
        '전체대비비율(%)': final_recommendation / total_equipment * 100
        if total_equipment else np.nan,
        '판정': (
            '20% 기준' if final_recommendation == ratio_recommendation
            else '설비분류LV1 최소조건 보정'
        )
    }

recommendation_df = pd.DataFrame([
    make_recommendation(base, class_name)
    for class_name in CLASS_LIST
])

# 전체 기준도 함께 산출
all_total = base[EQUIPMENT_COL].nunique()
all_ratio_recommendation = recommended_count(all_total)
all_lv1_minimum = (
    base.dropna(subset=[LV1_COL])
        .groupby(LV1_COL)[EQUIPMENT_COL]
        .nunique()
        .clip(upper=MIN_PER_LV1)
        .sum()
)
all_final = min(all_total, max(all_ratio_recommendation, int(all_lv1_minimum)))

all_row = pd.DataFrame([{
    CLASS_COL: '전체',
    '전체표준설비수': all_total,
    '20%계산값': int(np.ceil(all_total * TARGET_RATIO)),
    '기본추천후보수': all_ratio_recommendation,
    '설비분류LV1최소조건수': int(all_lv1_minimum),
    '최종추천후보수': all_final,
    '전체대비비율(%)': all_final / all_total * 100 if all_total else np.nan,
    '판정': '20% 기준' if all_final == all_ratio_recommendation else '설비분류LV1 최소조건 보정'
}])
recommendation_df = pd.concat([recommendation_df, all_row], ignore_index=True)

# ============================================================
# 3. 설비분류LV1별 파악
# ============================================================
def lv1_summary(data, class_name):
    x = data[data[CLASS_COL].eq(class_name)].copy()
    x = x.dropna(subset=[LV1_COL, EQUIPMENT_COL])

    result = (
        x.groupby(LV1_COL, observed=True)
         .agg(
             전체표준설비수=(EQUIPMENT_COL, 'nunique'),
             전체작업건수=(EQUIPMENT_COL, 'size')
         )
         .reset_index()
    )
    result['최소포함권장수'] = result['전체표준설비수'].clip(upper=MIN_PER_LV1)
    result[CLASS_COL] = class_name
    return result

lv1_df = pd.concat(
    [lv1_summary(base, class_name) for class_name in CLASS_LIST],
    ignore_index=True
)

lv1_df.to_csv(
    OUTPUT_DIR / '설비분류별_작업건수_분석.csv',
    index=False,
    encoding='utf-8-sig'
)

# ============================================================
# 4. Plotly 시각화
# ============================================================

lv1_df["설비당_작업건수"] = (lv1_df["전체작업건수"] / lv1_df["전체표준설비수"]).round(1)

fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=(
        "<b>1. 설비분류별 작업건수 비교 (연구소 vs 오피스)</b>",
        "<b>2. 설비 1기당 평균 작업부하 (작업건수 / 설비수)</b>",
        "<b>3. 설비수 대비 작업건수 포지셔닝 맵</b>",
        "<b>4. 사이트별 작업 비중 (연구소 / 오피스)</b>",
    ),
    specs=[
        [{"type": "bar"}, {"type": "bar"}],
        [{"type": "scatter"}, {"type": "pie"}],
    ],
    vertical_spacing=0.15,
    horizontal_spacing=0.12,
)

# 색상 팔레트 정의
colors = {"연구소": "#636EFA", "오피스": "#EF553B"}

# --- Chart 1: 설비분류별 전체작업건수 ---
for category in ["연구소", "오피스"]:
    sub = lv1_df[lv1_df["분류"] == category]
    fig.add_trace(
        go.Bar(
            x=sub["설비분류LV1"],
            y=sub["전체작업건수"],
            name=category,
            marker_color=colors[category],
            hovertemplate="설비: %{x}<br>작업건수: %{y:,}건<extra></extra>",
            legendgroup=category,
        ),
        row=1,
        col=1,
    )

# --- Chart 2: 설비 1기당 작업건수 ---
for category in ["연구소", "오피스"]:
    sub = lv1_df[lv1_df["분류"] == category]
    fig.add_trace(
        go.Bar(
            x=sub["설비분류LV1"],
            y=sub["설비당_작업건수"],
            name=category,
            marker_color=colors[category],
            hovertemplate="설비: %{x}<br>기당 작업수: %{y:,.1f}건/기<extra></extra>",
            legendgroup=category,
            showlegend=False,
        ),
        row=1,
        col=2,
    )

# --- Chart 3: 포지셔닝 산점도 (설비수 vs 작업건수) ---
for category in ["연구소", "오피스"]:
    sub = lv1_df[lv1_df["분류"] == category]
    fig.add_trace(
        go.Scatter(
            x=sub["전체표준설비수"],
            y=sub["전체작업건수"],
            mode="markers+text",
            text=sub["설비분류LV1"],
            textposition="top center",
            name=category,
            marker=dict(
                size=sub["설비당_작업건수"],
                sizemode="area",
                sizeref=2.0 * max(lv1_df["설비당_작업건수"]) / (40**2),
                sizemin=8,
                color=colors[category],
                opacity=0.7,
                line=dict(width=1, color="DarkSlateGrey"),
            ),
            hovertemplate="<b>%{text}</b> ("
            + category
            + ")<br>"
            + "설비수: %{x}개<br>작업건수: %{y:,}건<br>기당 부하: %{marker.size:.1f}<extra></extra>",
            legendgroup=category,
            showlegend=False,
        ),
        row=2,
        col=1,
    )

# --- Chart 4: 전체 작업 비중 (도넛 차트) ---
site_totals = lv1_df.groupby("분류")["전체작업건수"].sum().reset_index()
fig.add_trace(
    go.Pie(
        labels=site_totals["분류"],
        values=site_totals["전체작업건수"],
        hole=0.45,
        marker=dict(colors=[colors[c] for c in site_totals["분류"]]),
        textinfo="label+percent",
        hovertemplate="사이트: %{label}<br>총 작업건수: %{value:,}건 (%{percent})<extra></extra>",
    ),
    row=2,
    col=2,
)

# 3. 레이아웃 세부 설정
fig.update_layout(
    title=dict(
        text="<b>설비분류별 작업건수 분석 대시보드</b>",
        font=dict(size=20),
        x=0.5,
    ),
    barmode="group",
    template="plotly_white",
    height=850,
    width=1200,
    showlegend=False,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1
    ),
)

fig.update_xaxes(title_text="설비분류", row=1, col=1)
fig.update_xaxes(title_text="설비분류", row=1, col=2)
fig.update_xaxes(title_text="전체 표준 설비 수 (개)", row=2, col=1)
fig.update_yaxes(title_text="전체 작업 건수 (건)", row=1, col=1)
fig.update_yaxes(title_text="설비 1기당 작업 건수 (건/기)", row=1, col=2)
fig.update_yaxes(title_text="전체 작업 건수 (건)", row=2, col=1)

fig.write_html(
    OUTPUT_DIR / '설비분류별_작업건수_분석.html',
    include_plotlyjs='cdn'
)

pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 180)
