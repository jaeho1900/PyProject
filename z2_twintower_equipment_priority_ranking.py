"""트윈타워 전체 표준설비 우선순위 분석
기준: 설비 중요도, 업무 부하, 관리 빈도, 품질성과
주의: 중요도는 SLA 협의를 위한 1차 규칙기반 평가이며 법적 확정판정이 아님.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px

# Windows 11: 실제 엑셀 경로로 수정
DATA_PATH = Path(r'C:\Users\사용자명\Downloads\Integrated_data.xlsx')
# 예: DATA_PATH = Path(__file__).resolve().parent / 'Integrated_data.xlsx'
OUTPUT_DIR = DATA_PATH.parent / 'facility_sla_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
center = '트윈타워'

# 중요도 평가용 키워드 규칙: 설비명 기준으로 재현 가능하게 고정
SAFETY_5 = ['소화', '감지', '발신기', '수신기', '방화', '피난', '가스', '누수', '차단기', '변압기', '발전기', 'UPS', '배터리', '비상']
SAFETY_4 = ['전기', '분전반', 'MCC', '모터컨트롤', '냉동기', '보일러', '냉각탑', '공기조화기', '승강기', '엘리베이터', '펌프']
OPERATION_5 = ['MAIN', '차단기', '변압기', '발전기', 'UPS', '배터리', '수신기', '소화펌프', '냉동기', '냉각탑', '공기조화기', '보일러']
OPERATION_4 = ['SUB', '분전반', 'MCC', '모터컨트롤', '방화', '소화', '감지', '발신기', '가스']

# 실제 상태값에 맞게 정의
VALID_STATUSES = ['작업완료', '지연완료']


def contains_any(text, keywords):
    text = '' if pd.isna(text) else str(text).upper()
    return any(k.upper() in text for k in keywords)


def score_safety(name):
    if contains_any(name, SAFETY_5): return 5
    if contains_any(name, SAFETY_4): return 4
    return 2


def score_operation(name):
    if contains_any(name, OPERATION_5): return 5
    if contains_any(name, OPERATION_4): return 4
    return 2


def pct_rank(s):
    """동점은 평균순위로 처리한 0~100 백분위 점수."""
    return s.rank(method='average', pct=True) * 100


df = pd.read_excel(DATA_PATH)
df = df[df['운영센터'].eq(center)].copy()
df['_row_id'] = np.arange(len(df))
df['표준설비'] = df['표준설비'].astype('string').str.strip()
df['작업상태'] = df['작업상태'].astype('string').str.strip()
df['법정관리'] = df['법정관리'].astype('string').str.strip()
df['총작업시간(분)_E'] = pd.to_numeric(df['총작업시간(분)_E'], errors='coerce')
df = df[df['표준설비'].notna() & df['총작업시간(분)_E'].notna()].copy()

# 표준설비별 운영 실적 집계
r = df.groupby('표준설비', observed=True).agg(
    작업건수=('_row_id', 'size'),
    총작업시간_분_E=('총작업시간(분)_E', 'sum'),
    완료건수=('작업상태', lambda s: s.isin(VALID_STATUSES).sum()),
    기한내완료건수=('작업상태', lambda s: (s == '작업완료').sum()),
    지연완료건수=('작업상태', lambda s: (s == '지연완료').sum()),
    법정관리건수=('법정관리', lambda s: (s == '법정').sum()),
).reset_index()
r['총작업시간_시간_E'] = r['총작업시간_분_E'] / 60.0
r['이행률'] = r['완료건수'].div(r['작업건수'].replace(0, np.nan))
r['기한내이행률'] = r['기한내완료건수'].div(r['작업건수'].replace(0, np.nan))
r['지연률'] = r['지연완료건수'].div(r['작업건수'].replace(0, np.nan))
r['법정관리표시율'] = r['법정관리건수'].div(r['작업건수'].replace(0, np.nan))

# 중요도: 안전 40 + 법정·규제 30 + 운영중단 30
r['안전영향도'] = r['표준설비'].map(score_safety)
r['법정·규제영향도'] = np.select(
    [r['법정관리표시율'].ge(.8), r['법정관리표시율'].ge(.5), r['법정관리표시율'].gt(0)],
    [5, 4, 3], default=2
)
r['운영중단영향도'] = r['표준설비'].map(score_operation)
r['설비중요도점수'] = (
    r['안전영향도'] / 5 * 40
    + r['법정·규제영향도'] / 5 * 30
    + r['운영중단영향도'] / 5 * 30
)

# 업무부하·관리빈도: 원자료 값을 보존하고, 설비 간 비교는 백분위로 표준화
r['업무부하점수'] = pct_rank(r['총작업시간_분_E'])
r['관리빈도점수'] = pct_rank(r['작업건수'])

# 품질성과: 완료율은 높을수록, 지연률은 낮을수록 좋음
r['품질성과점수'] = (
    0.5 * r['이행률'] * 100
    + 0.5 * (1 - r['지연률']) * 100
)

# 4개 기준 동일 가중치. 중요도 내부에서는 이미 40/30/30 가중 적용
r['종합우선순위점수'] = (
    0.25 * r['설비중요도점수']
    + 0.25 * r['업무부하점수']
    + 0.25 * r['관리빈도점수']
    + 0.25 * r['품질성과점수']
)

r = r.sort_values(
    ['종합우선순위점수', '설비중요도점수', '총작업시간_분_E', '작업건수'],
    ascending=[False, False, False, False]
).reset_index(drop=True)
r['우선순위'] = np.arange(1, len(r) + 1)
r['운영센터'] = center

columns = [
    '우선순위', '운영센터', '표준설비', '작업건수',
    '총작업시간_분_E', '총작업시간_시간_E', '안전영향도',
    '법정·규제영향도', '운영중단영향도', '설비중요도점수',
    '업무부하점수', '관리빈도점수', '완료건수', '기한내완료건수',
    '지연완료건수', '이행률', '기한내이행률', '지연률',
    '법정관리표시율', '품질성과점수', '종합우선순위점수'
]
r = r[columns]

# 보고서용 데이터 저장
r.to_csv(OUTPUT_DIR / f'{center}_전체표준설비_우선순위.csv', index=False, encoding='utf-8-sig')
r.head(10).to_csv(OUTPUT_DIR / f'{center}_표준설비_우선순위_TOP10.csv', index=False, encoding='utf-8-sig')

# Plotly: 상위 20개
plot = r.head(20).sort_values('종합우선순위점수', ascending=True)
fig = px.bar(
    plot, x='종합우선순위점수', y='표준설비', orientation='h',
    color='설비중요도점수', text='종합우선순위점수',
    color_continuous_scale='Blues',
    title=f'{center} 표준설비 우선순위 TOP20',
    labels={'종합우선순위점수': '종합 우선순위 점수', '표준설비': '표준설비', '설비중요도점수': '설비 중요도 점수'},
    hover_data=['작업건수', '총작업시간_시간_E', '이행률', '지연률', '업무부하점수', '관리빈도점수']
)
fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
fig.update_layout(template='plotly_white', height=700, coloraxis_showscale=False)
fig.write_html(OUTPUT_DIR / f'{center}_표준설비_우선순위_TOP20.html', include_plotlyjs='cdn')

print(r.head(10).to_string(index=False))
