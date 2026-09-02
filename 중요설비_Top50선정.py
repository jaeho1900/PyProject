"""
연구소, 오피스별 표준설비 평가순위 TOP50
- 각 분류 안에서 설비중요도·업무부하·관리빈도·품질성과를 계산
- 각 분류의 전체평가순위 TOP50을 선정
- 해당 분류에 존재하는 모든 설비분류LV1을 포함하고, 각 LV1 최소 2개 보장
- 정확히 50개를 유지하도록 낮은 순위 설비를 대체
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px

DATA_PATH = Path(r'C:\Users\Administrator\Desktop\Integrated_data.parquet')
OUTPUT_DIR = DATA_PATH.parent / 'facility_sla_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLASS_LIST = ['연구소', '오피스']
TOP_N = 50
MIN_PER_LV1 = 2
VALID_STATUSES = ['작업완료', '지연완료']

SAFETY_5 = ['소화', '감지', '발신기', '수신기', '방화', '피난', '가스', '누수', '차단기', '변압기', '발전기', 'UPS', '배터리', '비상']
SAFETY_4 = ['전기', '분전반', 'MCC', '모터컨트롤', '냉동기', '보일러', '냉각탑', '공기조화기', '승강기', '엘리베이터', '펌프']
OPERATION_5 = ['MAIN', '차단기', '변압기', '발전기', 'UPS', '배터리', '수신기', '소화펌프', '냉동기', '냉각탑', '공기조화기', '보일러']
OPERATION_4 = ['SUB', '분전반', 'MCC', '모터컨트롤', '방화', '소화', '감지', '발신기', '가스']

def contains_any(value, keywords):
    text = '' if pd.isna(value) else str(value).upper()
    return any(k.upper() in text for k in keywords)

def safety_score(value):
    return 5 if contains_any(value, SAFETY_5) else 4 if contains_any(value, SAFETY_4) else 2

def operation_score(value):
    return 5 if contains_any(value, OPERATION_5) else 4 if contains_any(value, OPERATION_4) else 2

def percentile_score(s):
    return s.rank(method='average', pct=True) * 100

def priority_table(data, class_name):
    x = data[data['분류'].eq(class_name) & data['표준설비'].notna()].copy()
    x['_row_id'] = np.arange(len(x))
    x['표준설비'] = x['표준설비'].astype('string').str.strip()
    x['설비분류LV1'] = x['설비분류LV1'].astype('string').str.strip()
    x['작업상태'] = x['작업상태'].astype('string').str.strip()
    x['법정관리'] = x['법정관리'].astype('string').str.strip()
    x['총작업시간(분)_E'] = pd.to_numeric(x['총작업시간(분)_E'], errors='coerce')
    x = x[x['총작업시간(분)_E'].notna()].copy()
    r = x.groupby(['설비분류LV1', '표준설비'], observed=True).agg(
        작업건수=('_row_id', 'size'),
        총작업시간_분_E=('총작업시간(분)_E', 'sum'),
        완료건수=('작업상태', lambda s: s.isin(VALID_STATUSES).sum()),
        기한내완료건수=('작업상태', lambda s: (s == '작업완료').sum()),
        지연완료건수=('작업상태', lambda s: (s == '지연완료').sum()),
        법정관리건수=('법정관리', lambda s: (s == '법정').sum()),
    ).reset_index()
    r['총작업시간_시간_E'] = r['총작업시간_분_E'] / 60
    r['이행률'] = r['완료건수'] / r['작업건수'].replace(0, np.nan)
    r['지연률'] = r['지연완료건수'] / r['작업건수'].replace(0, np.nan)
    r['법정관리표시율'] = r['법정관리건수'] / r['작업건수'].replace(0, np.nan)
    r['안전영향도'] = r['표준설비'].map(safety_score)
    r['법정·규제영향도'] = np.select(
        [r['법정관리표시율'].ge(.8), r['법정관리표시율'].ge(.5), r['법정관리표시율'].gt(0)],
        [5, 4, 3], default=2
    )
    r['운영중단영향도'] = r['표준설비'].map(operation_score)
    r['설비중요도점수'] = r['안전영향도'] / 5 * 40 + r['법정·규제영향도'] / 5 * 30 + r['운영중단영향도'] / 5 * 30
    r['업무부하점수'] = percentile_score(r['총작업시간_분_E'])
    r['관리빈도점수'] = percentile_score(r['작업건수'])
    r['품질성과점수'] = 0.5 * r['이행률'] * 100 + 0.5 * (1 - r['지연률']) * 100
    r['종합우선순위점수'] = (r['설비중요도점수'] + r['업무부하점수'] + r['관리빈도점수'] + r['품질성과점수']) / 4
    r = r.sort_values(['종합우선순위점수', '설비중요도점수', '총작업시간_분_E', '작업건수'], ascending=False).reset_index(drop=True)
    r['전체평가순위'] = np.arange(1, len(r) + 1)
    r['분류'] = class_name
    return r

def select_top50(priority, top_n=TOP_N, minimum=MIN_PER_LV1):
    selected = priority.head(top_n).copy()
    selected['_선정사유'] = '분류별 전체평가순위 TOP50'
    all_classes = priority['설비분류LV1'].dropna().unique().tolist()
    if len(all_classes) * minimum > top_n:
        raise ValueError(f'설비분류LV1 수({len(all_classes)}) × 최소개수({minimum})가 TOP_N({top_n})보다 큽니다.')
    for lv1 in all_classes:
        available = priority[priority['설비분류LV1'] == lv1]['표준설비'].nunique()
        target = min(minimum, available)
        count = (selected['설비분류LV1'] == lv1).sum()
        if count >= target:
            continue
        candidates = priority[(priority['설비분류LV1'] == lv1) & (~priority['표준설비'].isin(selected['표준설비']))].head(target - count)
        for _, candidate in candidates.iterrows():
            selected = pd.concat([selected, candidate.to_frame().T], ignore_index=True)
            selected.loc[selected.index[-1], '_선정사유'] = f'{lv1} 최소 {minimum}개 보정'
            counts = selected['설비분류LV1'].value_counts(dropna=False)
            removable = selected[selected['설비분류LV1'].map(counts).gt(minimum)].sort_values('전체평가순위', ascending=False)
            if removable.empty:
                raise ValueError(f'{lv1} 최소개수 조건으로 TOP{top_n}을 구성할 수 없습니다.')
            selected = selected.drop(index=removable.index[0]).reset_index(drop=True)
    selected = selected.sort_values('전체평가순위').reset_index(drop=True)
    selected['보정후순위'] = np.arange(1, len(selected) + 1)
    return selected

def summarize(top50):
    s = top50.groupby('설비분류LV1', dropna=False, observed=True).agg(
        포함설비수=('표준설비', 'nunique'), 작업건수=('작업건수', 'sum'), 총작업시간_분_E=('총작업시간_분_E', 'sum'),
        평균종합점수=('종합우선순위점수', 'mean'), 최고평가순위=('전체평가순위', 'min')
    ).reset_index().sort_values('평균종합점수', ascending=False)
    s["평균종합점수"] = s["평균종합점수"].round(2)
    s['작업건수_비중(%)'] = (s['작업건수'] / s['작업건수'].sum() * 100).round(2)
    s['작업시간_비중(%)'] = (s['총작업시간_분_E'] / s['총작업시간_분_E'].sum() * 100).round(2)
    s['최소2개_충족여부'] = s['포함설비수'].ge(MIN_PER_LV1)
    return s

def run(data, class_name):
    p = priority_table(data, class_name)
    t = select_top50(p)
    s = summarize(t)
    prefix = f'{class_name}_표준설비'
    p.to_csv(OUTPUT_DIR / f'{prefix}_전체평가순위.csv', index=False, encoding='utf-8-sig')
    t.to_csv(OUTPUT_DIR / f'{prefix}_TOP50_분류보정.csv', index=False, encoding='utf-8-sig')
    s.to_csv(OUTPUT_DIR / f'{prefix}_TOP50_설비분류LV1_요약.csv', index=False, encoding='utf-8-sig')

    plot = s.sort_values("포함설비수", ascending=False).copy()
    bar_order = plot["설비분류LV1"].tolist()

    # Legend도 막대그래프와 동일한 순서로 설정
    plot["Legend"] = plot.apply(
        lambda row: (
            f"{row['설비분류LV1']} "
            f"({row['평균종합점수']:.2f})"
        ),
        axis=1
    )
    legend_order = plot["Legend"].tolist()

    legend_color_map = {
        row["Legend"]: LV1_COLOR_MAP[row["설비분류LV1"]]
        for _, row in plot.iterrows()
    }

    fig = px.bar(
        plot,
        x="포함설비수",
        y="설비분류LV1",
        orientation="h",
        text="포함설비수",
        color="Legend",
        color_discrete_map=legend_color_map,
        category_orders={"Legend": legend_order},
        title=(
            f"{class_name} 표준설비 평가순위 TOP50 - "
            "설비분류LV1 구성"
        ),
        labels={
            "포함설비수": "TOP50 포함 설비 수",
            "설비분류LV1": "설비분류LV1",
            "Legend": "평균 종합점수"
        }
    )

    fig.update_traces(
        textposition="outside",
        hovertemplate=(
            "설비분류LV1: %{y}<br>"
            "TOP50 포함 설비 수: %{x}<br>"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        template="plotly_white",
        height=500,
        yaxis=dict(
            categoryorder="array",
            categoryarray=bar_order[::-1]
        ),
        legend=dict(
            title="평균 종합점수",
            traceorder="normal"
        )
    )
    fig.write_html(
        OUTPUT_DIR / f"{prefix}_TOP50_설비분류LV1.html",
        include_plotlyjs="cdn"
    )
    return p, t, s

df = pd.read_parquet(DATA_PATH, engine='pyarrow', dtype_backend='pyarrow')

for col in ['분류','표준설비','설비분류LV1']:
    df[col] = df[col].astype('string').str.strip()

# 설비분류LV1별 고정 색상
lv1_list = (
    df["설비분류LV1"]
    .dropna()
    .astype(str)
    .str.strip()
    .drop_duplicates()
    .sort_values()
    .tolist()
)
color_palette = px.colors.qualitative.Set2
LV1_COLOR_MAP = {
    lv1: color_palette[i % len(color_palette)]
    for i, lv1 in enumerate(lv1_list)
}

for class_name in CLASS_LIST:
    p, t, s = run(df, class_name)
    print(f'\n[{class_name}] 설비분류LV1 요약')
    print(s.to_string(index=False))
    print(f'\n[{class_name}] TOP50')
    print(t[['보정후순위','전체평가순위','설비분류LV1','표준설비','종합우선순위점수','_선정사유']].to_string(index=False))
