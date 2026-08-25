# =====================
# EDA (Exploratory Dada Analysis)
# =====================

#  [4가지 주제]
#  1. 저항성의 강조: 이상치 등 부분적 변동에 대한 민감성 확인
#  2. 잔차계산: 관찰 값들이 주 경향에서 벗어난 정도 파악
#  3. 자료변수의 재표현: 변수를 적당한 척도롤 바꾸는 것
#  4. 그래프를 통한 현시성: 분석 결과를 이해하기 쉽게 시각화하는 것


# =====================
# 단일 그래프 그리기
# =====================

x = [1, 2, 3, 4]
y = [100000, 400000, 900000, 1600000]

# >>> 한글 폰트 사용 -----

import matplotlib.pyplot as plt
import platform

if platform.system() == 'Windows': #윈도우
        plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin': #맥
        plt.rc('font', family='AppleGothic')
elif platform.system() == 'Linux': #리눅스 (구글 콜랩)
        plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False # 유니코드에서 음수 부호설정

# 한글 폰트 윈도우ver
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# >>> 사이즈 -----

plt.figure(figsize=(14, 5), dpi=80)  # 가로x세로 인치

# >>> 범례 -----

plt.plot(x, y, label='그래프1')
plt.legend()

plt.legend(loc='best')
# loc 옵션 : best(0), upper right(1), upper left(2),
#            lower left(3), lower right(4), right(5), center left(6), center right(7),
#            lower center(8), , upper center(9), center(10)

# >>> 타이틀 -----

plt.title('Title', fontsize=17, color='black', loc='center')

# >>> 축 레이블 -----

plt.xlabel('X label(원)', fontsize=15, color='black')
plt.ylabel('Y label(명)', fontsize=15, color='black')

# >>> 축 범위 -----

plt.xlim(0.0, 5.0)
plt.ylim(min(y), max(y)+1)

plt.axis([0, 6, 0, 20])     # xmin, xmax, ymin, ymax

# >>> 눈금 -----

# 눈금 값 및 눈금 값 서식
plt.xticks(ticks = [1, 1.5, 3, 3.5], labels = ['갑', '점오', 'Three', '정'], rotation=30, ha='left', color='r')

# 눈금 값 서식(천단위) : 현재 눈금 값을 가져와서, 값을 fixed 한 후, 포멧팅
# gca()는 get current axese의 약어
current_values = plt.gca().get_yticks()
plt.gca().set_yticks(current_values)
plt.gca().set_yticklabels(['{:,.0f}'.format(x) for x in current_values])

# 눈금 값 서식 및 눈금 서식
plt.tick_params(axis='y', labelsize=10, labelcolor='green', rotation=-25, color='r',
                direction='in', length=3, width=5, pad=6)
# axis       x, y, both
# direction  눈금 위치(안/밖/걸침 in, out, inout)
# length     눈금 길이
# width      눈금 너비
# pad        눈금과 글자 간격

# >>> 그리드 -----

plt.grid(axis='y', color='gray', alpha=0.5, linestyle='--')  # both, x, y

plt.grid(False)

# >>> 주석 표시 -----

# 화살표
plt.annotate('',
             xy=(0.2, 0.1),       # 화살표의 머리 부분
             xytext=(0.6, 0.8),   # 화살표의 꼬리 부분
             xycoords='data',     # data(좌표와 같이 이동), figure fraction(좌표 위치 고수)
             arrowprops=dict(arrowstyle='->', color='skyblue', lw=5))
# 텍스트
plt.annotate('주석입력',           # 텍스트 입력
             xy=(0.3, 0.6),       # 텍스트 위치 기준점
             rotation=60,         # 텍스트 기울기
             va='center',         # 텍스트 상하 정렬
             ha='left',           # 텍스트 좌우 정렬
             fontsize='12')

# >>> 수직,수평선 그리기 -----

# 수평선 : hlines(y기준값, x시작값, x끝값), 점과 점 연결
plt.hlines(4, 1, 1.6, colors='red', linewidth=3)

# 수평선 : axhline(y기준값, x시작비율값, x끝비율값) , ※ 축비율(0~100%)
plt.axhline(1.5, 0.1, 0.7, color='gray', linestyle='--', linewidth='1')

# 수직선 : vlines(x기준값, y시작값, y끝값), 점과 점 연결
plt.vlines(1, 1, 4, colors='pink', linewidth=3)

# 수직선 : axvline(x기준값, y시작비율값, y끝비율값) , ※ 축비율(0~100%)
plt.axvline(1.5, 0.2, 1.8, color='green', linestyle=':', linewidth='2')

# >>> 그래프 영역 채우기 -----

x = [1, 3, 5, 7, 9]
y1 = [1, 2, 4, 6, 8]
y2 = [1, 3, 7, 10, 12]
plt.plot(x, y1)
plt.plot(x, y2)

# Y축의 0값 부터 4개의 점을 잇는 영역 : (x[2], 0), (x[2], y1[2]), (x[3], y1[3]), (x[3], 0)
plt.fill_between(x[2:4], y1[2:4], alpha=0.5)

# X측의 0값 부터 4개의 점을 잇는 영역 : (0, y2[2]), (0, y2[3]), (x[3], y2[3]), (x[2], y2[2])
plt.fill_betweenx(y2[2:4], x[2:4], color='pink', alpha=0.5)

# 두 그래프 사이의 영역 채우기
plt.fill_between(x[1:3], y1[1:3], y2[1:3], color='b', alpha=0.5)

# 임의의 영역 채우기 : 시계 방향
plt.fill([7, 7, 9, 9], [5, 12, 10.5, 6.5], color='y', alpha=0.5)

# >>> 그래프 랜더링 -----

plt.show()

# >>> 그래프 저장 -----

# PNG, PDF, SVG, JPG 등 저장
plt.savefig('figure.png', dpi=300)

# 투명 배경 저장
plt.savefig('figure_transparent.png', transparent=True)

# >>> 자동 스타일 -----

# 자동 스타일 종류
plt.style.available

# classic: Matplotlib의 초기 스타일
# ggplot: R의 ggplot 패키지에서 영감을 받은 스타일
# seaborn: Seaborn 라이브러리에서 영감을 받은 스타일
# bmh: Bayesian Methods for Hackers 책에서 사용된 스타일
# dark_background: 어두운 배경에 적합한 스타일
# grayscale: 회색조 스타일
# fivethirtyeight: 뉴스 사이트 FiveThirtyEight.com에서 영감을 받은 스타일

# 자동 스타일 적용은 모든 그래프에 적용됨
plt.style.use('ggplot')

# 기본 스타일로 되돌리기
plt.style.use('default')

# 임시 스타일 적용 : with문 블럭에서만
with plt.style.context('ggplot'):
    plt.plot([1, 2, 3], [1, 2, 3])
    plt.show()


# =====================
# 다중 그래프 그리기
# =====================

# >>> 하나의 좌표평면에 다중 그래프 그리기 -----

x1 = range(1, 10)
x2 = range(1, 8)
x3 = range(3, 12)
y1 = [2, 3, 4, 5, 6, 7, 8, 9, 10]
y2 = [10, 9, 8, 7, 6, 5, 4]
y3 = [5, 5, 5, 5, 5, 5, 5, 5, 5]

# 하나의 좌표평면에 다중 그래프 그리기
plt.plot(x1, y1, label='그래프 1')
plt.plot(x2, y2, label='그래프 2')
plt.plot(x3, y3, label='그래프 3')

# 범례 표시
plt.legend()

# 그래프 제목 및 축 라벨 추가
plt.title('제목: 다중 선 그래프 그리기')
plt.xlabel('X축')
plt.ylabel('Y축')

# 그래프 보여주기
plt.show()

# >>> 하나의 창에 각각의 좌표평면을 가지는 서브 플롯 그리기 -----

# subplot(nrows, ncols, index)는 각각 행, 열, 서브플롯의 위치를 나타내며, 인덱스는 1부터 시작하여
# 행을 따라 왼쪽에서 오른쪽으로, 다시 위에서 아래로 증가
# subplot(2, 3, 4)는 2행 3열의 그리드에서 4번째 위치(두 번째 행의 첫 번째 열)의 서브플롯을 의미

import matplotlib.pyplot as plt

x = [1, 2, 3, 4]
y = [1, 4, 9, 16]
z = [109, 190, 200, 150]

# 그림틀 객체 생성
plt.figure(figsize=(6, 4))

# 첫 번째 서브플롯 -----
plt.subplot(221)
plt.plot(x, y)
plt.xlabel('x축', size=10)
plt.ylabel('y축', size=10)
plt.ylim(min(y), max(y))
plt.xticks(ticks = [-1, 0, 1, 4, 5], labels = ['-1', '0', '갑', '을', '병'], rotation=30)
plt.tick_params(axis='x', labelsize=10, labelcolor='b')  # 눈금 서식
plt.title('서브플롯 1')

# 두 번째 서브플롯 : 겹쳐서 그리기 -----
plt.subplot(222)
plt.plot([12, 15, 19], 'o', label='line')
plt.bar([2, 4, 6], [12, 15, 11], label='bar')
plt.legend()
plt.title('서브플롯 2')

# 세 번째 서브플롯 : 트윈 축(x축 공유) 그리기 -----
plt.subplot(223)
plt.plot(x, y, color='blue')
plt.twinx()
plt.bar(x, z, color='green', alpha=0.5)
plt.ylim(50, 250)
plt.ylabel('Z-label', fontsize='14')
plt.title('서브플롯 3')

# 레이아웃 조정 및 보여주기
plt.tight_layout()
plt.show()


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

import matplotlib.pyplot as plt
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
# color: b, g, r, c(cyan), m(magenta), y, k(black), w
# linestyles: -, --, -., :
# marker: ., o, ^, s, D, d, +, x
plt.plot(y)                                                  # 1개의 데이터만 전달하면 y축 데이터로 인식하고, x축 데이터는 자동 생성
plt.plot(x, y, color='g', linestyle='-', marker='o', linewidth=1.5, markersize=5)

df.plot(kind='line')
plt.show()

# 함수식 그래프
def linear_fun(x):
    return 2 * x + 8

plt.plot(df.x, linear_fun(df.x), color='g')
plt.plot(df.x, linear_fun(df.x), color='g')


# =====================
# Step plot
# =====================

# where: pre, mid, post
plt.plot(x, y, 'o--', color='grey', alpha=0.3)
plt.step(x, y, where='post')

# 판다스 스텝 그래프
# drawstyle: steps, steps-mid, steps-post
df.plot(x='x', y='y', drawstyle='steps-post', linewidth=2)


# =====================
# Bar plot
# =====================

# hatch: 막대 내부에 패턴 /, \, |, -, +, x, o, O, .
plt.bar(df.x, df.y, color='c', edgecolor='k', linewidth=2, linestyle='--',
        hatch='//', alpha=0.5, width=0.5, tick_label=[0, '갑', '을', '병'])

# 도수분포표와 함께 활용
df['x'].value_counts()

# 가로 바
plt.barh(df.x, df.y, height=-0.6, align='edge', color='c', edgecolor='gray', linewidth=2,
         tick_label=[0, '갑', '을', '병'])

# 판다스 막대 그래프
df.plot(kind='bar', color=['b', 'g', 'c'], stacked=True)
df.iloc[1].plot(kind='barh', color=['b', 'g', 'c'])


# =====================
# Scatter plot
# =====================

# alpha : 점의 투명도(0~1사이의 숫자)
# edgecolor : 점 테두리의 색
plt.scatter(x=df.x, y=df.y, s=20, c='r', alpha=0.5, edgecolor='black')

# 버블 차트(3변수)
plt.scatter(x=df.x, y=df.y, s=df.z * 100, c='r', alpha=0.5)

# 판다스 산점도 그래프
df.plot(kind='scatter', x='x', y='y', s=20, c='r', alpha=0.5)          # x, y 데이터에는 '열이름' 만 입력(df.열이름 x)
df.plot(kind='scatter', x='x', y='y', s=df.z * 100, c='r', alpha=0.5)  # size 데이터에는 'df.열이름' 으로 사용


# =====================
# Histogram
# =====================

# bins: 막대의 개수를 지정하거나, 막대 경계를 나타내는 시퀀스를 전달. 예시) bins=20
# range: 데이터의 범위를 (min, max) 형태로 지정. 지정하지 않으면 데이터의 최솟값과 최댓값이 기준. 예시) range=(-3, 3)

# 기술통계를 기준으로 구간을 나눈다
df.y.describe()

# x축은 데이터구간을 표현하고 y축은 데이터 개수(빈도)를 표현한다
plt.hist(df.y, bins=range(0, 21, 5), density=True, alpha=0.7, histtype='step')  # 0부터 20까지 5단위로 4구간 설정
plt.hist(df.y, bins=range(0, 21, 5), density=False, alpha=0.5, histtype='stepfilled')

# 이벤트 발생 지점을 배열로 반환
bins = plt.hist(df.y, bins=4)
print(bins)

# 판다스 히스토그램
df.y.plot(kind='hist', bins=3, density=True, alpha=0.5, histtype='step', color='blue', figsize=(10, 5))
df.y.plot(kind='hist', bins=3, density=False, alpha=0.5, histtype='stepfilled', color='blue', figsize=(10, 5))


# =====================
# Box plot
# =====================

plt.boxplot(df.y)

# 판다스 박스 그래프
df.y.plot(kind='box', vert=False)


# =====================
# Pie chart
# =====================

df1 = pd.DataFrame({'count':[4, 2, 1] }, index=['apple', 'banana', 'mango'])

# startangle : 시작 각도, 3시 방향부터 반시계 방향으로 회전. 예시) startangle=90
# explode    : 파이 조각이 중심에서 벗어나는 정도
# autopct    : 각 섹션의 비율을 텍스트 형태로 표시하는 방법을 지정합니다. 예를 들어, '%1.1f%%'는 소수점 아래 한 자리까지 표시합니다. 예시) autopct='%1.1f%%'
# shadow     : 파이 차트에 그림자를 추가하여 3D 효과를 줄 수 있습니다. 예시) shadow=True
# wedgeprops : 도넛 형태
plt.pie(df1['count'], labels=['apple', 'banana', 'mango'],
        startangle=90, explode=[0, 0.2, 0.1], autopct='%.1f%%', shadow=True,
        wedgeprops={'width': 0.5, 'edgecolor': 'k', 'linewidth': 2})

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
# Seaborn
# =====================

# matplotlib 기반으로 구축되었으며
# pandas 데이터프레임과 통합되어 xtick, ytick, xlabel, ylabel, legend 등 자동 세팅

import matplotlib.pyplot as plt
import seaborn as sns

# >>> relplot : 관계형(relational) 그래프 -----

# 팁 dataset의 5개 변수 간의 관계
tips = sns.load_dataset('tips')
sns.relplot(
    # x=tips['total_bill'], y=tips['tip'],
    data=tips, x='total_bill', y='tip',
    col='time', hue='smoker', style='smoker', size='size',
)

# 한 변수가 시간 측정을 나타내는 관계
dots = sns.load_dataset('dots')
sns.relplot(
    data=dots, x='time', y='firing_rate',
    kind='line', col='align',
    hue='choice', size='coherence', style='choice',
    facet_kws=dict(sharex=False),
)

# >>> distplot : 분포형(distributions) 그래프 -----

titanic = sns.load_dataset('titanic')
titanic.fare.describe()

fig = plt.figure(figsize=(15, 5))
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)

# 히스토그램, 커널밀도그래프
sns.histplot(data=titanic, x='fare', element='step', ax=ax1)
sns.histplot(titanic['fare'], kde=True, stat='density', element='step', ax=ax2)
sns.kdeplot(data=titanic, x='fare', ax=ax3)

# >>> catplot : 카테고리형(categorical) 그래프 -----

titanic = sns.load_dataset('titanic')
sns.swarmplot(data=titanic, x='class', y='age', hue='sex')

# >>> 다차원 데이터 -----

iris = sns.load_dataset('iris')

# 다차원 실수형 데이터 -----
sns.pairplot(iris)

# 카테고리형 데이터가 섞여 있는 경우 -----
# hue 인수에 카테고리 변수 이름을 지정하여 카테고리 값에 따라 색상을 다르게 할 수 있다
sns.pairplot(iris, hue='species', markers=['o', 's', 'D'])

# 2차원 카테고리 데이터 -----
# 2개의 범주형 변수를 x, y축으로 하여 데이터를 매트릭스로 분류한 피벗테이블을 이용
df_pivot = titanic.pivot_table(index='sex', columns='class', aggfunc='size')
sns.heatmap(df_pivot, annot=True, fmt='.0f', cmap='Reds', linewidth=.5, cbar=False)

# >>> 스타일 테마 : darkgrid, whitegrid, dark, white, ticks -----

sns.set_style('darkgrid')

# 테마 삭제
plt.style.use('default')


# =====================
# ydata_profiling
# =====================

import seaborn as sns

titanic = sns.load_dataset('titanic')
df = titanic.loc[:, ['age', 'fare', 'class', 'who', 'embark_town', 'alive']]

# ​conda install ydata-profiling
# ​conda install ipywidgets
from ydata_profiling import ProfileReport

# 프로파일링 실행
ProfileReport(df, title="Profiling Report")

# 데이터가 큰 경우는 html파일로 저장 후 확인 권장
profile = ProfileReport(df, title="Profiling Report")
profile.to_file('profile.html')
