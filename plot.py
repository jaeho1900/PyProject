# =====================
# EDA (Exploratory Dada Analysis) - Plotly 버전
# =====================

#  [4가지 주제]
#  1. 저항성의 강조: 이상치 등 부분적 변동에 대한 민감성 확인
#  2. 잔차계산: 관찰 값들이 주 경향에서 벗어난 정도 파악
#  3. 자료변수의 재표현: 변수를 적당한 척도롤 바꾸는 것
#  4. 그래프를 통한 현시성: 분석 결과를 이해하기 쉽게 시각화하는 것


# =====================
# 단일 그래프 그리기
# =====================

import plotly.graph_objects as go
import plotly.express as px

x = [1, 2, 3, 4]
y = [100000, 400000, 900000, 1600000]

# >>> 한글 폰트 사용 -----
# (Plotly는 OS별 폰트 분기 없이 layout.font.family로 한 번에 지정)
# (Plotly는 matplotlib의 axes.unicode_minus 같은 별도 옵션이 없음. 마이너스 기호는 기본 지원)

fig = go.Figure()
fig.update_layout(font=dict(family='Malgun Gothic'))

# >>> 사이즈 -----

fig.update_layout(width=14 * 80, height=5 * 80)  # inch*dpi 개념 대신 픽셀(px) 직접 지정

# >>> 범례 -----

fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='그래프1'))
fig.update_layout(showlegend=True)

fig.update_layout(legend=dict(x=1, y=1, xanchor='right', yanchor='top'))
# loc 옵션 : Plotly는 legend=dict(x=.., y=.., xanchor=.., yanchor=..)로 좌표 직접 지정

# >>> 타이틀 -----

fig.update_layout(title=dict(text='Title', font=dict(size=17, color='black'), x=0.5, xanchor='center'))

# >>> 축 레이블 -----

fig.update_xaxes(title_text='X label(원)', title_font=dict(size=15, color='black'))
fig.update_yaxes(title_text='Y label(명)', title_font=dict(size=15, color='black'))

# >>> 축 범위 -----

fig.update_xaxes(range=[0.0, 5.0])
fig.update_yaxes(range=[min(y), max(y) + 1])

fig.update_layout(xaxis=dict(range=[0, 6]), yaxis=dict(range=[0, 20]))  # xmin, xmax, ymin, ymax

# >>> 눈금 -----

# 눈금 값 및 눈금 값 서식
fig.update_xaxes(tickmode='array', tickvals=[1, 1.5, 3, 3.5], ticktext=['갑', '점오', 'Three', '정'],
                 tickangle=30, tickfont=dict(color='red'))

# 눈금 값 서식(천단위) : Plotly는 tickformat 옵션 한 줄로 처리(별도 get/set 불필요)
fig.update_yaxes(tickformat=',.0f')

# 눈금 값 서식 및 눈금 서식
fig.update_yaxes(tickfont=dict(size=10, color='green'), tickangle=-25,
                 tickcolor='red', ticks='inside', ticklen=3, tickwidth=5)
# axis       Plotly는 update_xaxes/update_yaxes로 축별 개별 지정(both 옵션 없음, 둘 다 적용시 각각 호출)
# direction  ticks 옵션(inside, outside, '' 로 없음)
# length     ticklen
# width      tickwidth
# pad        ticklabelstandoff (버전에 따라 미지원 가능)

# >>> 그리드 -----

fig.update_yaxes(showgrid=True, gridcolor='gray', griddash='dash')  # alpha는 rgba 색상으로 표현 필요(예: 'rgba(128,128,128,0.5)')

fig.update_yaxes(showgrid=False)
fig.update_xaxes(showgrid=False)

# >>> 주석 표시 -----

# 화살표
fig.add_annotation(
    x=0.2, y=0.1,          # 화살표의 머리 부분(ax/ay 대비 도착점)
    ax=0.6, ay=0.8,        # 화살표의 꼬리 부분
    xref='x', yref='y', axref='x', ayref='y',
    showarrow=True, arrowhead=2, arrowcolor='skyblue', arrowwidth=5
)
# 텍스트
fig.add_annotation(
    text='주석입력',
    x=0.3, y=0.6,
    textangle=-60,          # Plotly textangle은 시계방향이 반대이므로 부호 반전
    showarrow=False,
    font=dict(size=12),
    align='left'
)

# >>> 수직,수평선 그리기 -----

# 수평선 : add_shape(y기준값, x시작값, x끝값), 점과 점 연결
fig.add_shape(type='line', x0=1, x1=1.6, y0=4, y1=4, line=dict(color='red', width=3))

# 수평선 : add_hline(y기준값), 축 전체 비율 지정은 xref='paper'로 근사
fig.add_hline(y=1.5, line=dict(color='gray', dash='dash', width=1))

# 수직선 : add_shape(x기준값, y시작값, y끝값), 점과 점 연결
fig.add_shape(type='line', x0=1, x1=1, y0=1, y1=4, line=dict(color='pink', width=3))

# 수직선 : add_vline(x기준값), 축 전체 비율 지정은 yref='paper'로 근사
fig.add_vline(x=1.5, line=dict(color='green', dash='dot', width=2))

# >>> 그래프 영역 채우기 -----

x = [1, 3, 5, 7, 9]
y1 = [1, 2, 4, 6, 8]
y2 = [1, 3, 7, 10, 12]

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=x, y=y1, mode='lines'))
fig2.add_trace(go.Scatter(x=x, y=y2, mode='lines'))

# Y축의 0값 부터 4개의 점을 잇는 영역
fig2.add_trace(go.Scatter(x=x[2:4], y=y1[2:4], fill='tozeroy', mode='lines', opacity=0.5))

# X측의 0값 부터 4개의 점을 잇는 영역 : Plotly는 fill_betweenx에 대응하는 직접 함수가 없어 shape/trace로 근사 구현 필요
fig2.add_trace(go.Scatter(x=x[2:4], y=y2[2:4], fill='tozerox', mode='lines',
                          line=dict(color='pink'), opacity=0.5))

# 두 그래프 사이의 영역 채우기
fig2.add_trace(go.Scatter(x=x[1:3], y=y1[1:3], mode='lines', line=dict(color='blue')))
fig2.add_trace(go.Scatter(x=x[1:3], y=y2[1:3], mode='lines', fill='tonexty',
                          line=dict(color='blue'), opacity=0.5))

# 임의의 영역 채우기 : 시계 방향 -> go.Scatter fill='toself'로 다각형 채우기
fig2.add_trace(go.Scatter(x=[7, 7, 9, 9], y=[5, 12, 10.5, 6.5],
                          fill='toself', mode='lines', line=dict(color='yellow'), opacity=0.5))

# >>> 그래프 랜더링 -----

# (nbformat이 패키지 필요)
fig2.show()

# >>> 그래프 저장 -----

# PNG, PDF, SVG, JPG 등 저장 (python-kaleido 패키지 필요)
fig2.write_image('figure.png', scale=300 / 96)  # dpi 대신 scale로 해상도 배율 지정

# 투명 배경 저장
fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
fig2.write_image('figure_transparent.png')

# >>> 자동 스타일 -----

# 자동 스타일 종류
import plotly.io as pio

# 사용 가능한 템플릿 목록 확인
# ggplot2, seaborn, simple_white, plotly, plotly_white, plotly_dark, presentation, xgridoff, ygridoff, gridon, none
# Plotly 내장 템플릿은 matplotlib 스타일명과 1:1 대응하지 않으며 개념적으로 유사한 것을 선택
pio.templates

# 자동 스타일 적용은 모든 그래프에 적용됨
pio.templates.default = 'ggplot2'

# 기본 스타일로 되돌리기
pio.templates.default = 'plotly'

# 임시 스타일 적용 : 해당 fig 생성시에만 template 인자로 지정(with문 방식 없음)
fig3 = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[1, 2, 3])])
fig3.update_layout(template='ggplot2')
fig3.show()


# =====================
# 다중 그래프 그리기
# =====================

# >>> 하나의 좌표평면에 다중 그래프 그리기 -----

x1 = list(range(1, 10))
x2 = list(range(1, 8))
x3 = list(range(3, 12))
y1 = [2, 3, 4, 5, 6, 7, 8, 9, 10]
y2 = [10, 9, 8, 7, 6, 5, 4]
y3 = [5, 5, 5, 5, 5, 5, 5, 5, 5]

fig4 = go.Figure()

# 하나의 좌표평면에 다중 그래프 그리기
fig4.add_trace(go.Scatter(x=x1, y=y1, mode='lines', name='그래프 1'))
fig4.add_trace(go.Scatter(x=x2, y=y2, mode='lines', name='그래프 2'))
fig4.add_trace(go.Scatter(x=x3, y=y3, mode='lines', name='그래프 3'))

# 범례 표시
fig4.update_layout(showlegend=True)

# 그래프 제목 및 축 라벨 추가
fig4.update_layout(title='제목: 다중 선 그래프 그리기')
fig4.update_xaxes(title_text='X축')
fig4.update_yaxes(title_text='Y축')

# 그래프 보여주기
fig4.show()

# >>> 하나의 창에 각각의 좌표평면을 가지는 서브 플롯 그리기 -----

# make_subplots(rows, cols)는 각각 행, 열의 개수를 지정하며, add_trace(trace, row=, col=)로
# 각 서브플롯 위치를 지정. Plotly는 인덱스 하나로 위치를 지정하는 subplot(nrows,ncols,index) 방식이 아니라
# row/col 번호를 각각 명시적으로 지정

from plotly.subplots import make_subplots

x = [1, 2, 3, 4]
y = [1, 4, 9, 16]
z = [109, 190, 200, 150]

# 그림틀 객체 생성 (2행 2열, 세 번째 서브플롯은 보조 y축 사용)
fig5 = make_subplots(rows=2, cols=2,
                     specs=[[{}, {}], [{'secondary_y': True}, {}]],
                     subplot_titles=('서브플롯 1', '서브플롯 2', '서브플롯 3', ''))

# 첫 번째 서브플롯 -----
fig5.add_trace(go.Scatter(x=x, y=y, mode='lines'), row=1, col=1)
fig5.update_xaxes(title_text='x축', title_font=dict(size=10), row=1, col=1)
fig5.update_yaxes(title_text='y축', title_font=dict(size=10), range=[min(y), max(y)], row=1, col=1)
fig5.update_xaxes(tickmode='array', tickvals=[-1, 0, 1, 4, 5], ticktext=['-1', '0', '갑', '을', '병'],
                  tickangle=30, row=1, col=1)
fig5.update_xaxes(tickfont=dict(size=10, color='blue'), row=1, col=1)  # 눈금 서식

# 두 번째 서브플롯 : 겹쳐서 그리기 -----
fig5.add_trace(go.Scatter(y=[12, 15, 19], mode='markers', name='line'), row=1, col=2)
fig5.add_trace(go.Bar(x=[2, 4, 6], y=[12, 15, 11], name='bar'), row=1, col=2)
fig5.update_layout(showlegend=True)

# 세 번째 서브플롯 : 트윈 축(x축 공유) 그리기 -----
fig5.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='blue')), row=2, col=1, secondary_y=False)
fig5.add_trace(go.Bar(x=x, y=z, marker=dict(color='green'), opacity=0.5), row=2, col=1, secondary_y=True)
fig5.update_yaxes(range=[50, 250], title_text='Z-label', title_font=dict(size=14), row=2, col=1, secondary_y=True)

# 레이아웃 조정 및 보여주기 (tight_layout 대응 개념은 없으며 margin으로 근사 조정)
fig5.update_layout(margin=dict(l=40, r=40, t=60, b=40))
fig5.show()


# ##########################################################
# 1. 시간 경과
#  - line plot: 카테고리별 흐름
#  - stacked bar plot: 특정 시점의 카테고리별 기여

# 2. 비교, 순위
#  - bar plot : 범주의 갯수차이가 극단적이면 업/다운 샘플링을 통해 조정 필요하다는 인사이트 발견, 도수분포표와 함께 활용

# 3. 변수간의 관계
#  - scatter plot : 두 개의 수치형 변수의 분포와 관계 파악

# 4. 데이터 분포
#  - histogram : 연속형 자료의 대한 분포 모양 확인
#  - box plot : 수치형 변수값의 분포를 파악하여 중앙값으로 데이터의 치우친 정도, 50%의 데이터들이 퍼진 정도를 파악

# 5. 전체에 대한 비율
#  - pie chart
# ##########################################################

# >>> 실습 데이터 -----

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

x = [1, 2, 3, 4]
y = [1, 4, 9, 16]
z = [19, 10, 20, 15]

df = pd.DataFrame({'x': x, 'y': y, 'z': z})
df.index = df.index.map(int)  # 데이터프레임 인덱스를 정수형 인덱스로 변경(x축 눈금라벨로 사용)

# >>> 판다스 적용 -----

# .plot() 메서드는 내부적으로 Matplotlib를 호출하여 차트를 그린다.


# =====================
# Line plot
# =====================

# x 값에 대응하는 y 값이 있어야 하며(동일 길이), 두 데이터 배열의 포인트를 선으로 연결하여 생성
# color: Plotly는 색상명('green','red' 등) 또는 hex/rgba 코드 사용
# line_dash: solid, dash, dot, dashdot
# marker symbol: circle, circle-open, triangle-up, square, diamond, cross, x

# 1개의 데이터만 전달하면 y축 데이터로 인식하고, x축은 인덱스로 자동 생성
fig6 = go.Figure(go.Scatter(y=y, mode='lines'))
fig6.show()

fig6 = go.Figure(go.Scatter(x=x, y=y, mode='lines+markers',
                            line=dict(color='green', dash='solid', width=1.5),
                            marker=dict(symbol='circle', size=5)))
fig6.show()

fig7 = px.line(df, x=df.index, y='y')
fig7.show()

# 함수식 그래프
def linear_fun(x):
    return 2 * x + 8

fig8 = go.Figure(go.Scatter(x=df.x, y=linear_fun(df.x), mode='lines', line=dict(color='green')))
fig8.show()


# =====================
# Step plot
# =====================

# line_shape: hv(post), vh(pre), hvh(mid)
fig9 = go.Figure()
fig9.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', line=dict(dash='dash', color='grey'), opacity=0.3))
fig9.add_trace(go.Scatter(x=x, y=y, mode='lines', line_shape='hv'))  # where='post'

# 판다스 스텝 그래프
# drawstyle: steps, steps-mid, steps-post
df.plot(x='x', y='y', drawstyle='steps-post', linewidth=2)


# =====================
# Bar plot
# =====================

# pattern_shape: 막대 내부 패턴 (/, \\, |, -, +, x, ., 빈 문자열)
fig11 = go.Figure(go.Bar(
    x=df.x, y=df.y,
    marker=dict(color='cyan', line=dict(color='black', width=2), pattern_shape='/'),
    opacity=0.5, width=0.5
))
fig11.update_xaxes(tickmode='array', tickvals=df.x, ticktext=[0, '갑', '을', '병'])

# 도수분포표와 함께 활용
df['x'].value_counts()

# 가로 바
fig12 = go.Figure(go.Bar(
    x=df.y, y=df.x, orientation='h',
    marker=dict(color='cyan', line=dict(color='gray', width=2))
))
fig12.update_yaxes(tickmode='array', tickvals=df.x, ticktext=[0, '갑', '을', '병'])

# 판다스 막대 그래프
df.plot(kind='bar', color=['b', 'g', 'c'], stacked=True)
df.iloc[1].plot(kind='barh', color=['b', 'g', 'c'])


# =====================
# Scatter plot
# =====================

# opacity : 점의 투명도(0~1사이의 숫자)
# marker.line : 점 테두리 지정
fig15 = go.Figure(go.Scatter(x=df.x, y=df.y, mode='markers',
                             marker=dict(size=20, color='red', line=dict(color='black', width=1)),
                             opacity=0.5))
fig15.show()

# 버블 차트(3변수)
fig16 = go.Figure(go.Scatter(x=df.x, y=df.y, mode='markers',
                             marker=dict(size=df.z, color='red'), opacity=0.5))
fig16.show()

# 판다스 산점도 그래프
df.plot(kind='scatter', x='x', y='y', s=20, c='r', alpha=0.5)          # x, y 데이터에는 '열이름' 만 입력(df.열이름 x)
df.plot(kind='scatter', x='x', y='y', s=df.z * 100, c='r', alpha=0.5)  # size 데이터에는 'df.열이름' 으로 사용


# =====================
# Histogram
# =====================

# nbinsx: 막대의 개수를 지정. xbins로 구간 경계를 직접 지정 가능
# range_x: 데이터의 범위를 (min, max) 형태로 지정. 지정하지 않으면 자동 산정

# 기술통계를 기준으로 구간을 나눈다
df.y.describe()

# x축은 데이터구간을 표현하고 y축은 데이터 개수(빈도) 또는 밀도를 표현한다
fig19 = go.Figure(go.Histogram(x=df.y, xbins=dict(start=0, end=20, size=5),
                               histnorm='probability density', opacity=0.7))
fig19.update_traces(marker=dict(line=dict(width=1)))  # histtype='step' 대응(윤곽선만 강조)
fig19.show()

fig20 = go.Figure(go.Histogram(x=df.y, xbins=dict(start=0, end=20, size=5), opacity=0.5))
fig20.show()

# 이벤트 발생 지점을 배열로 반환 : Plotly는 히스토그램 계산 결과를 직접 반환하지 않으므로 numpy로 별도 계산
import numpy as np
counts, bin_edges = np.histogram(df.y, bins=4)
print(counts, bin_edges)

# 판다스 히스토그램
df.y.plot(kind='hist', bins=3, density=True, alpha=0.5, histtype='step', color='blue', figsize=(10, 5))
df.y.plot(kind='hist', bins=3, density=False, alpha=0.5, histtype='stepfilled', color='blue', figsize=(10, 5))


# =====================
# Box plot
# =====================

fig23 = go.Figure(go.Box(y=df.y))
fig23.show()

# 판다스 박스 그래프
df.y.plot(kind='box', vert=False)


# =====================
# Pie chart
# =====================

df1 = pd.DataFrame({'count': [4, 2, 1]}, index=['apple', 'banana', 'mango'])

# rotation : 시작 각도, 3시 방향부터 반시계 방향으로 회전. 예시) rotation=90
# pull      : 파이 조각이 중심에서 벗어나는 정도(explode에 대응)
# textinfo  : 각 섹션의 비율을 텍스트 형태로 표시. 예시) textinfo='percent'
# (그림자 효과는 Plotly에 직접적인 대응 옵션이 없음)
# hole      : 도넛 형태(0~1)
fig25 = go.Figure(go.Pie(
    labels=['apple', 'banana', 'mango'], values=df1['count'],
    rotation=90, pull=[0, 0.2, 0.1], textinfo='percent',
    hole=0.5, marker=dict(line=dict(color='black', width=2))
))
fig25.show()

# 판다스 파이 차트
df1['count'].plot(kind='pie',
                  startangle=90,
                  explode=[0, 0.2, 0.1],
                  autopct='%.1f%%',
                  colors=['c', 'r', 'g'],
                  labels=['apple', 'banana', 'mango'],
                  shadow=True,
                  wedgeprops={'width': 0.5, 'edgecolor': 'k', 'linewidth': 2}
                  )


# =====================
# Seaborn -> Plotly Express
# =====================

# plotly는 matplotlib 기반이 아닌 독립 렌더링 엔진이며
# pandas 데이터프레임을 직접 인자로 받아 x, y, color, facet 등을 자동 세팅

import plotly.express as px
import seaborn as sns

# >>> relplot : 관계형(relational) 그래프 -----

# 팁 dataset의 변수 간의 관계
tips = px.data.tips()  # seaborn dataset 대신 plotly express 내장 데이터셋 사용
fig27 = px.scatter(
    tips, x='total_bill', y='tip',
    facet_col='time', color='smoker', symbol='smoker', size='size',
)
fig27.show()

# 한 변수가 시간 측정을 나타내는 관계 : plotly express 내장 dots 데이터셋이 없어 임의 데이터 필요(개념적 대응만 표기)
dots = sns.load_dataset('dots')
fig28 = px.line(
    dots, x='time', y='firing_rate',
    facet_col='align', color='choice', line_dash='choice',
)
fig28.show()

# >>> distplot : 분포형(distributions) 그래프 -----

titanic = sns.load_dataset('titanic')
titanic.fare.describe()

# 히스토그램, 커널밀도그래프 : Plotly에는 kdeplot 대응 함수가 없어 ff.create_distplot으로 근사
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

fig29 = make_subplots(rows=1, cols=3)
fig29.add_trace(go.Histogram(x=titanic['fare']), row=1, col=1)
dist_fig = ff.create_distplot([titanic['fare'].dropna()], ['fare'])
for trace in dist_fig.data:
    fig29.add_trace(trace, row=1, col=2)
kde_fig = ff.create_distplot([titanic['fare'].dropna()], ['fare'], show_hist=False, show_rug=False)
for trace in kde_fig.data:
    fig29.add_trace(trace, row=1, col=3)
fig29.show()

# >>> catplot : 카테고리형(categorical) 그래프 -----

titanic = sns.load_dataset('titanic')
fig30 = px.strip(titanic, x='class', y='age', color='sex')
fig30.show()

# >>> 다차원 데이터 -----

iris = px.data.iris()

# 다차원 실수형 데이터 -----
fig31 = px.scatter_matrix(iris)
fig31.show()

# 카테고리형 데이터가 섞여 있는 경우 -----
# color 인수에 카테고리 변수 이름을 지정하여 카테고리 값에 따라 색상을 다르게 할 수 있다
fig32 = px.scatter_matrix(iris, dimensions=iris.columns[:4], color='species',
                          symbol='species', symbol_sequence=['circle', 'square', 'diamond'])
fig32.show()

# >>> 2차원 카테고리 데이터 -----
# 2개의 범주형 변수를 x, y축으로 하여 데이터를 매트릭스로 분류한 피벗테이블을 이용
# titanic 데이터 필요(예시 개념 표기)
# df_pivot = titanic.pivot_table(index='sex', columns='class', aggfunc='size')
# fig33 = px.imshow(df_pivot, text_auto='.0f', color_continuous_scale='Reds', aspect='auto')

# >>> 스타일 테마 -----
# Plotly 대응 템플릿: plotly_white, plotly_dark, simple_white, ggplot2, seaborn 등
pio.templates.default = 'seaborn'

# 테마 삭제(기본값으로 되돌리기)
pio.templates.default = 'plotly'
