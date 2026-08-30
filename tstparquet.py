# ======================
# atG 작업관리 분석
# (오피스 및 연구소)
# ======================

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 필터링 ----------
# df[df['서비스LV1'] == '시설']   # 검침,보수,운전,점검,시설순찰,진단[Patrol],예방정비,법정검사/신고 선정
# df[df['서비스LV1'] == '관리']   # 센터업무 > 작업명 ==> 데이터 누락/오류분 과다로 제외
# df[df['서비스LV1'] == 'PM']     # 회계관리 > 작업명 ==> YTN센터 1개센터만 DATA 존재로 제외
# df[df['총작업시간(분)'].isna()] # 미운전설비, 작업발행오류 등으로 제외

# 호출 ----------------------
# file_path = r'C:\Users\Administrator\Desktop\●통합데이터.parquet'
file_path = r'C:\Users\Thanki\Desktop\com\●통합데이터.parquet'
df = pd.read_parquet(file_path, engine='pyarrow', dtype_backend='pyarrow')
# size: 251602 x 36

# 파악 ----------------------
df.info()
df.columns
df['총작업시간(분)_E'].isna().sum()
df['총작업시간(분)_E'].describe()


# 그룹핑 파악 ----------------------
re = df.copy()

re['서비스LV2'].unique()
re['표준설비'].unique()

# ('분류', '서비스LV2', '표준설비')
result_df = (
    re.groupby(['분류', '서비스LV2', '표준설비'])['총작업시간(분)_E']
    .agg(작업시간_분='sum', 작업건수='count')
    .reset_index()
)

# 분류별 총작업시간이 가장 많은 상위 5개 추출
top5_df = (
    result_df.groupby('분류', group_keys=True)
    .apply(lambda x: x.nlargest(10, '작업시간_분'))
    .reset_index(drop=True)
)

# ('운영센터', '서비스LV2')
result_df = (
    re.groupby(['운영센터', '서비스LV2'])['총작업시간(분)_E']
    .agg(총작업시간_분='sum', 작업건수='count')
    .reset_index()
)

# ('운영센터', '표준설비')
result_df = (
    re.groupby(['운영센터', '표준설비'])['총작업시간(분)_E']
    .agg(총작업시간_분='sum', 작업건수='count')
    .reset_index()
)

result_df

# 저장 ----------------------

# result.to_parquet(r'C:\Users\Administrator\Desktop\●통합데이터_세부.parquet',
#               index=False,
#               engine='pyarrow'
#              )

# result.to_excel(r'C:\Users\Administrator\Desktop\●통합데이터_세부.xlsx', index=False)

# 시각화 ----------------------

# -----------------------
# 작업건수와 총작업시간(분) 비교 누적막대
# -----------------------

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =========================================================================
# 1. 분석 기준 컬럼 및 운영센터 순서 설정
# =========================================================================

target_col = '표준설비'
# target_col = '서비스LV2'

center_order = [
    '트윈타워',
    '서울역빌딩',
    'YTN상암PFM',
    '건와빌딩',
    '전자양재R&D캠퍼스',
    '전자가산R&D캠퍼스',
    '전자서초R&D',
]

# =========================================================================
# 2. 데이터 필터링 및 그룹핑 집계
# =========================================================================
center_col = '운영센터' if '운영센터' in df.columns else '운영센터명'
facility_df = df[df['서비스LV1'] == '시설'].copy()

# target_col에 결측치(NaN)가 있을 경우 '기타/미지정'으로 대체
facility_df[target_col] = facility_df[target_col].fillna('기타/미지정')

result_df = (
    facility_df.groupby([center_col, target_col])['총작업시간(분)']
    .agg(작업건수='count', 총작업시간_분='sum')
    .reset_index()
)

# =========================================================================
# 3. 비중이 큰 항목이 상단에 쌓이도록 정렬 (오름차순 트레이스 추가)
# =========================================================================
target_totals = (
    result_df.groupby(target_col)['총작업시간_분'].sum().sort_values(ascending=True)
)
sorted_targets = target_totals.index.tolist()

# =========================================================================
# 4. 서브플롯 생성
# =========================================================================
fig = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        '<b>운영센터별 작업건수 비중 (100%)</b>',
        '<b>운영센터별 총작업시간(분) 비중 (100%)</b>',
    ),
    horizontal_spacing=0.12,
)

for item in sorted_targets:
    sub = result_df[result_df[target_col] == item]

    # 좌측: 작업건수
    fig.add_trace(
        go.Bar(
            x=sub[center_col],
            y=sub['작업건수'],
            name=str(item),
            legendgroup=str(item),
            hovertemplate=f'<b>{item}</b><br>센터: %{{x}}<br>건수: %{{y:,}}건<extra></extra>',
        ),
        row=1,
        col=1,
    )

    # 우측: 총작업시간
    fig.add_trace(
        go.Bar(
            x=sub[center_col],
            y=sub['총작업시간_분'],
            name=str(item),
            legendgroup=str(item),
            showlegend=False,
            hovertemplate=f'<b>{item}</b><br>센터: %{{x}}<br>시간: %{{y:,.1f}}분<extra></extra>',
        ),
        row=1,
        col=2,
    )

# =========================================================================
# 5. 여백 및 레이아웃 설정
# =========================================================================
# 서브플롯 제목 간격 넓히기
for annotation in fig['layout']['annotations']:
    annotation['yshift'] = 15

fig.update_layout(
    title=dict(
        text=f'<b>[시설] 운영센터 및 {target_col}별 100% 기준 작업 현황</b>',
        y=0.98,
    ),
    barmode='stack',
    barnorm='percent',
    template='plotly_white',
    height=600,
    margin=dict(t=100, b=80, l=60, r=60),
    legend=dict(
        title=dict(text=f'<b>{target_col}</b>'), traceorder='reversed'
    ),
)

fig.update_xaxes(
    categoryorder='array', categoryarray=center_order, tickangle=45
)
fig.update_yaxes(ticksuffix='%', range=[0, 100])

fig.show()

# fig.write_html(r'C:\Users\Administrator\Desktop\facility_analysis.html')


# -----------------------
# LV1의 시설, 관리 비중 및 개별설비의 비중 파이 차트
# -----------------------

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# -------------------------------------------------------------------------
# 1. 조건별 기준 컬럼('작업구분') 생성 및 집계
# -------------------------------------------------------------------------
df['작업구분'] = np.where(
    df['서비스LV1'] == '시설',
    df['서비스LV2'],
    np.where(df['서비스LV1'] == '관리', df['작업명'], np.nan),
)

filtered_df = df[df['서비스LV1'].isin(['시설', '관리'])].copy()

agg_df = (
    filtered_df.groupby(['운영센터명', '작업구분'])['총작업시간(분)']
    .agg(건수='count', 총작업시간_합계='sum')
    .reset_index()
)

# -------------------------------------------------------------------------
# 2. 서브플롯 구성: 각 센터별 1행 할당 (왼쪽: 총작업시간, 오른쪽: 작업건수)
# -------------------------------------------------------------------------
centers = agg_df['운영센터명'].unique()
rows = len(centers)
cols = 2

# 각 서브플롯의 제목 생성
subplot_titles = []
for center in centers:
    subplot_titles.append(f'<b>[{center}] 총작업시간(분) 비중</b>')
    subplot_titles.append(f'<b>[{center}] 작업건수 비중</b>')

# 파이 차트용 domain 타입 스펙 설정
specs = [[{'type': 'domain'}, {'type': 'domain'}] for _ in range(rows)]

fig = make_subplots(
    rows=rows,
    cols=cols,
    specs=specs,
    subplot_titles=subplot_titles,
    vertical_spacing=0.08,
    horizontal_spacing=0.05,
)

# -------------------------------------------------------------------------
# 3. 파이 차트 추가 (도넛 형태로 가독성 향상)
# -------------------------------------------------------------------------
for idx, center in enumerate(centers):
    r = idx + 1
    sub_df = agg_df[agg_df['운영센터명'] == center]

    # [좌측: Column 1] 총작업시간 파이차트
    fig.add_trace(
        go.Pie(
            labels=sub_df['작업구분'],
            values=sub_df['총작업시간_합계'],
            name=f'{center}_시간',
            hole=0.3,  # 도넛 형태
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>총작업시간: %{value:,.1f}분<br>비율: %{percent}<extra></extra>',
            showlegend=(
                idx == 0
            ),  # 첫 번째 행에서만 범례를 표시하여 중복 방지
        ),
        row=r,
        col=1,
    )

    # [우측: Column 2] 작업건수 파이차트
    fig.add_trace(
        go.Pie(
            labels=sub_df['작업구분'],
            values=sub_df['건수'],
            name=f'{center}_건수',
            hole=0.3,  # 도넛 형태
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>작업건수: %{value:,}건<br>비율: %{percent}<extra></extra>',
            showlegend=False,
        ),
        row=r,
        col=2,
    )

# 4. 전체 레이아웃 설정
fig.update_layout(
    title_text='<b>[운영센터별] 총작업시간 vs 작업건수 비중 비교</b>',
    template='plotly_white',
    height=400 * rows,  # 센터 개수에 맞춰 전체 세로 높이 자동 조절
)

fig.show()
