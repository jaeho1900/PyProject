"""트윈타워 표준설비 평가순위 TOP50의 설비분류LV1 분류 분석
- 기존 우선순위 모형: 중요도·업무부하·관리빈도·품질성과
- TOP50을 먼저 선정한 뒤, 설비분류LV1별 최소 2개 조건을 보정
- 정확히 50개를 유지하도록 과다 대표 분류의 최하위 순위를 교체
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px

# Windows 11에서 수정할 부분
DATA_PATH = Path(r'C:\Users\사용자명\Downloads\Integrated_data.xlsx')
# 예: DATA_PATH = Path(__file__).resolve().parent / 'Integrated_data.xlsx'
OUTPUT_DIR = DATA_PATH.parent / 'facility_sla_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
center = '트윈타워'

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


def percentile_score(series):
    return series.rank(method='average', pct=True) * 100


def get_priority_table(data):
    data = data[data['표준설비'].notna()].copy()
    data['_row_id'] = np.arange(len(data))
    data['표준설비'] = data['표준설비'].astype('string').str.strip()
    data['설비분류LV1'] = data['설비분류LV1'].astype('string').str.strip()
    data['작업상태'] = data['작업상태'].astype('string').str.strip()
    data['법정관리'] = data['법정관리'].astype('string').str.strip()
    data['총작업시간(분)_E'] = pd.to_numeric(data['총작업시간(분)_E'], errors='coerce')
    data = data[data['총작업시간(분)_E'].notna()].copy()

    r = data.groupby(['설비분류LV1', '표준설비'], observed=True).agg(
        작업건수=('_row_id', 'size'),
        총작업시간_분_E=('총작업시간(분)_E', 'sum'),
        완료건수=('작업상태', lambda s: s.isin(VALID_STATUSES).sum()),
        기한내완료건수=('작업상태', lambda s: (s == '작업완료').sum()),
        지연완료건수=('작업상태', lambda s: (s == '지연완료').sum()),
        법정관리건수=('법정관리', lambda s: (s == '법정').sum()),
    ).reset_index()
    r['총작업시간_시간_E'] = r['총작업시간_분_E'] / 60
    r['이행률'] = r['완료건수'] / r['작업건수'].replace(0, np.nan)
    r['기한내이행률'] = r['기한내완료건수'] / r['작업건수'].replace(0, np.nan)
    r['지연률'] = r['지연완료건수'] / r['작업건수'].replace(0, np.nan)
    r['법정관리표시율'] = r['법정관리건수'] / r['작업건수'].replace(0, np.nan)

    r['안전영향도'] = r['표준설비'].map(safety_score)
    r['법정·규제영향도'] = np.select(
        [r['법정관리표시율'].ge(.8), r['법정관리표시율'].ge(.5), r['법정관리표시율'].gt(0)],
        [5, 4, 3], default=2
    )
    r['운영중단영향도'] = r['표준설비'].map(operation_score)
    r['설비중요도점수'] = (
        r['안전영향도'] / 5 * 40
        + r['법정·규제영향도'] / 5 * 30
        + r['운영중단영향도'] / 5 * 30
    )
    r['업무부하점수'] = percentile_score(r['총작업시간_분_E'])
    r['관리빈도점수'] = percentile_score(r['작업건수'])
    r['품질성과점수'] = 0.5 * r['이행률'] * 100 + 0.5 * (1 - r['지연률']) * 100
    r['종합우선순위점수'] = (
        r['설비중요도점수'] + r['업무부하점수']
        + r['관리빈도점수'] + r['품질성과점수']
    ) / 4
    r = r.sort_values(
        ['종합우선순위점수', '설비중요도점수', '총작업시간_분_E', '작업건수'],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)
    r['전체평가순위'] = np.arange(1, len(r) + 1)
    return r


def select_top50_with_minimum_by_class(priority, class_col='설비분류LV1', top_n=50, minimum=2):
    """정확히 top_n개를 유지하면서 분류별 최소 minimum개를 보장한다."""
    selected = priority.head(top_n).copy()
    selected['_selected_reason'] = '전체평가순위 TOP50'

    for class_name in priority[class_col].dropna().unique():
        current_count = (selected[class_col] == class_name).sum()
        if current_count >= minimum:
            continue

        need = minimum - current_count
        candidates = priority[
            (priority[class_col] == class_name)
            & (~priority['표준설비'].isin(selected['표준설비']))
        ].head(need)
        for _, candidate in candidates.iterrows():
            selected = pd.concat([selected, candidate.to_frame().T], ignore_index=True)
            selected.loc[selected.index[-1], '_selected_reason'] = f'{class_name} 최소 {minimum}개 보정'

            # 다른 분류에서 현재 선택 수가 minimum보다 큰 가장 낮은 순위부터 제거
            selected_counts = selected[class_col].value_counts(dropna=False)
            removable = selected[
                selected[class_col].map(selected_counts).gt(minimum)
                & (selected['표준설비'] != candidate['표준설비'])
            ].sort_values('전체평가순위', ascending=False)
            if removable.empty:
                raise ValueError('최소 분류 수를 보장하면서 정확한 TOP50을 만들 수 없습니다.')
            remove_idx = removable.index[0]
            selected = selected.drop(index=remove_idx).reset_index(drop=True)

    selected = selected.sort_values('전체평가순위').reset_index(drop=True)
    selected['보정후순위'] = np.arange(1, len(selected) + 1)
    return selected


df = pd.read_excel(DATA_PATH)
center_df = df[df['운영센터'].eq(center)].copy()
priority = get_priority_table(center_df)
top50 = select_top50_with_minimum_by_class(priority, top_n=50, minimum=2)

# 분류별 요약
group_summary = top50.groupby('설비분류LV1', dropna=False, observed=True).agg(
    포함설비수=('표준설비', 'nunique'),
    작업건수=('작업건수', 'sum'),
    총작업시간_분_E=('총작업시간_분_E', 'sum'),
    평균종합점수=('종합우선순위점수', 'mean'),
    최고평가순위=('전체평가순위', 'min'),
).reset_index().sort_values('평균종합점수', ascending=False)
group_summary['작업건수_비중(%)'] = group_summary['작업건수'] / group_summary['작업건수'].sum() * 100
group_summary['작업시간_비중(%)'] = group_summary['총작업시간_분_E'] / group_summary['총작업시간_분_E'].sum() * 100

# 저장
priority.to_csv(OUTPUT_DIR / f'{center}_전체표준설비_평가순위.csv', index=False, encoding='utf-8-sig')
top50.to_csv(OUTPUT_DIR / f'{center}_표준설비_TOP50_분류보정.csv', index=False, encoding='utf-8-sig')
group_summary.to_csv(OUTPUT_DIR / f'{center}_표준설비_TOP50_설비분류LV1_요약.csv', index=False, encoding='utf-8-sig')

# 시각화: 분류별 TOP50 포함 설비 수
fig = px.bar(
    group_summary.sort_values('포함설비수'),
    x='포함설비수', y='설비분류LV1', orientation='h',
    text='포함설비수', color='평균종합점수', color_continuous_scale='Blues',
    title=f'{center} 표준설비 평가순위 TOP50 - 설비분류LV1별 구성',
    labels={'포함설비수': 'TOP50 포함 설비 수', '설비분류LV1': '설비분류LV1', '평균종합점수': '평균 종합점수'}
)
fig.update_traces(textposition='outside')
fig.update_layout(template='plotly_white', height=500, coloraxis_showscale=False)
fig.write_html(OUTPUT_DIR / f'{center}_표준설비_TOP50_설비분류LV1.html', include_plotlyjs='cdn')

print('[TOP50 설비분류LV1별 요약]')
print(group_summary.to_string(index=False))
print('\n[TOP50 목록]')
print(top50[['보정후순위', '전체평가순위', '설비분류LV1', '표준설비', '종합우선순위점수', '_selected_reason']].to_string(index=False))
