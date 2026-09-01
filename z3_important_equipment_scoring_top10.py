"""
중요 표준설비 우선순위 평가
- 안전·법정·운영중단 영향도를 5점 척도로 평가
- 가중치: 안전 40%, 법정 30%, 운영중단 30%
- 점수는 법적 확정판정이 아니라 SLA 분석용 1차 평가모형
"""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px

# Windows 11: 아래 DATA_PATH를 실제 파일 위치로 수정하거나
# 이 코드와 Integrated_data.xlsx를 같은 폴더에 둔다.
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'Integrated_data.xlsx'
# 예: DATA_PATH = Path(r'C:\Users\홍길동\Downloads\Integrated_data.xlsx')
OUTPUT_DIR = BASE_DIR / 'facility_sla_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 평가 대상 20개 표준설비
# 실제 데이터에 존재하는 명칭과 일치하는지 먼저 확인한다.
EQUIPMENT_SCORE = [
    ('R형 수신기', 5, 5, 5, '화재신호 수신·표시·감시의 중심으로 건물 화재대응에 직접 영향'),
    ('감지기(열/연)', 5, 5, 5, '화재 조기감지와 경보의 시작점으로 누락·오작동 시 안전영향이 큼'),
    ('옥내소화전(발신기일체형)', 5, 5, 5, '화재 발생 시 초기 소화 및 발신 기능과 직접 연결'),
    ('소화기', 5, 5, 3, '초기 화재 대응의 기본 소방설비로 수량·배치·유효기간 관리가 중요'),
    ('방화문', 5, 5, 4, '화재·연기 확산 방지와 방화구획 유지에 직접 영향'),
    ('방화셔터', 5, 5, 4, '화재 시 개구부 차단 및 연소확대 방지에 직접 영향'),
    ('발전기(디젤 수냉식)', 5, 4, 5, '정전 시 비상전원 공급과 핵심시설 연속운영에 영향'),
    ('MAIN진공차단기(VCB)', 5, 3, 5, '고압 수전·배전계통의 사고전류 차단과 전원 안정성에 영향'),
    ('SUB진공차단기(VCB)', 4, 3, 4, '고압 배전구간 보호 및 사고구간 분리에 중요'),
    ('변압기(TR_몰드)', 4, 3, 5, '전력공급 핵심설비로 장애 발생 시 정전 및 운영중단 영향이 큼'),
    ('MAIN기중차단기(ACB)', 4, 3, 5, '주배전계통 과전류 보호와 전원 차단에 중요'),
    ('SUB기중차단기(ACB)', 4, 3, 4, '구역별 배전 보호와 전기안전 관리에 중요'),
    ('자동절체스위치(ATS)', 4, 3, 5, '상용·비상전원 자동 절체 성능에 따라 정전 대응이 좌우됨'),
    ('무정전전원공급장치(UPS)', 4, 3, 5, '전산·통신·제어 등 순간정전 민감 부하의 연속운영에 중요'),
    ('UPS&배터리 시스템', 4, 3, 5, '비상전원 유지시간과 UPS 성능을 좌우하는 저장전원 설비'),
    ('공기조화기', 3, 2, 4, '실내 온습도·공기질 및 연구·업무환경 유지에 영향'),
    ('냉각탑', 3, 2, 4, '냉방 열원계통의 핵심으로 냉방 안정성과 설비효율에 영향'),
    ('분전반(동력)', 4, 2, 4, '펌프·팬·공조 등 동력설비 운전전원 공급에 중요'),
    ('분전반(전등/전열)', 3, 2, 3, '조명·콘센트 계통 전원공급과 과부하 관리에 중요'),
    ('모터컨트롤센터(MCC_판넬)', 3, 2, 4, '주요 모터설비의 제어·보호 및 운전 안정성에 영향'),
]

score_df = pd.DataFrame(
    EQUIPMENT_SCORE,
    columns=['표준설비', '안전영향도', '법정·규제영향도', '운영중단영향도', '선정근거']
)

# 5점 척도를 100점으로 변환
WEIGHTS = {
    '안전영향도': 0.40,
    '법정·규제영향도': 0.30,
    '운영중단영향도': 0.30,
}
score_df['안전배점'] = score_df['안전영향도'] / 5 * 100 * WEIGHTS['안전영향도']
score_df['법정·규제배점'] = score_df['법정·규제영향도'] / 5 * 100 * WEIGHTS['법정·규제영향도']
score_df['운영중단배점'] = score_df['운영중단영향도'] / 5 * 100 * WEIGHTS['운영중단영향도']
score_df['종합점수'] = score_df[['안전배점', '법정·규제배점', '운영중단배점']].sum(axis=1)
score_df['우선순위'] = (
    score_df['종합점수'].rank(method='first', ascending=False).astype(int)
)
score_df = score_df.sort_values(
    ['종합점수', '안전영향도', '운영중단영향도', '법정·규제영향도'],
    ascending=[False, False, False, False]
).reset_index(drop=True)
score_df['우선순위'] = np.arange(1, len(score_df) + 1)

# TOP 10
top10_df = score_df.head(10).copy()

# 결과 저장
score_df.to_csv(OUTPUT_DIR / '중요표준설비_20개_배점결과.csv', index=False, encoding='utf-8-sig')
top10_df.to_csv(OUTPUT_DIR / '중요표준설비_TOP10.csv', index=False, encoding='utf-8-sig')

# Plotly 시각화
plot_df = top10_df.sort_values('종합점수', ascending=True)
fig = px.bar(
    plot_df,
    x='종합점수',
    y='표준설비',
    orientation='h',
    text='종합점수',
    color='종합점수',
    color_continuous_scale='Blues',
    title='안전·법정·운영중단 영향도 기준 중요 표준설비 TOP10',
    labels={'종합점수': '종합점수(100점)', '표준설비': '표준설비'},
    hover_data=['안전영향도', '법정·규제영향도', '운영중단영향도']
)
fig.update_traces(texttemplate='%{text:.1f}점', textposition='outside')
fig.update_layout(template='plotly_white', height=600, coloraxis_showscale=False)
fig.write_html(OUTPUT_DIR / '중요표준설비_TOP10.html', include_plotlyjs='cdn')

print('\n[중요 표준설비 TOP10]')
print(top10_df[
    ['우선순위', '표준설비', '안전영향도', '법정·규제영향도', '운영중단영향도', '종합점수']
].to_string(index=False))
print(f'\n결과 저장 위치: {OUTPUT_DIR}')
