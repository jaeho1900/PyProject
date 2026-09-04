"""
센터별 총작업시간 vs 작업건수 비중 시각화(파이차트)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 호출
file_path = r"C:\Users\Administrator\Desktop\Integrated_data.parquet"
df = pd.read_parquet(file_path, engine='pyarrow', dtype_backend='pyarrow')

df['작업구분'] = np.where(
    df['서비스LV1'] == '시설',
    df['서비스LV2'],
    np.where(df['서비스LV1'] == '관리', df['작업명'], np.nan),
)

filtered_df = df[df['서비스LV1'].isin(['시설', '관리'])].copy()

agg_df = (
    filtered_df.groupby(['운영센터', '작업구분'])['총작업시간(분)_E']
    .agg(건수='count', 총작업시간_합계='sum')
    .reset_index()
)

# 서브플롯 구성: 각 센터별 1행 할당 (왼쪽: 총작업시간, 오른쪽: 작업건수)
centers = agg_df['운영센터'].unique()
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

for idx, center in enumerate(centers):
    r = idx + 1
    sub_df = agg_df[agg_df['운영센터'] == center]

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
    height=500 * rows,  # 센터 개수에 맞춰 전체 세로 높이 자동 조절
)
# fig.show(renderer="browser")
fig.write_html(f'센터별_작업시간_작업건수_비교.html', include_plotlyjs='cdn')
