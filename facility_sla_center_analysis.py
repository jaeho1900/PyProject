"""
시설관리 SLA 근거자료용 분석 코드
- pandas / numpy / plotly 중심
- 운영센터별 분석: center = '트윈타워'
- 총작업건수·총작업시간 자체 비교가 아니라 센터 내부 비율 및 이행률 중심
- 현재 파일에는 요청일시 컬럼이 없으므로 '요청→착수 시간'은 실제 요청일시가 추가될 때 계산
"""

from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# 0. 설정
# ============================================================
DATA_PATH =Path(r'C:\Users\Administrator\Desktop\home\Integrated_data.parquet')
OUTPUT_DIR = DATA_PATH.parent / 'facility_sla_analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 분석 대상 운영센터: 필요할 때 이 변수만 바꾸면 됨
center = '트윈타워'

# 서비스LV2 색상 고정: 모든 차트에서 동일하게 사용
SERVICE_COLORS = {
    '점검': '#1F77B4',
    '운전': '#FF7F0E',
    '보수': '#2CA02C',
    '검침': '#D62728',
    '시설순찰': '#9467BD',
    '진단[Patrol]': '#8C564B',
    '예방정비': '#E377C2',
    '법정검사/신고': '#17BECF',
}

STATUS_COMPLETED = '작업완료'
STATUS_DELAYED = '지연완료'
VALID_STATUSES = [STATUS_COMPLETED, STATUS_DELAYED]


def safe_divide(numerator, denominator):
    """문자열·object·스칼라·0 나눗셈을 안전하게 처리하는 비율 계산 함수."""
    num = pd.to_numeric(numerator, errors='coerce')

    # 분모가 Series인 경우
    if isinstance(denominator, (pd.Series, pd.Index)):
        den = pd.to_numeric(
            denominator,
            errors='coerce'
        ).astype('float64')

        den = den.mask(den.eq(0))

        return num.astype('float64').div(den)

    # 분모가 numpy.float64, int, float 등 단일 숫자인 경우
    den = pd.to_numeric(
        denominator,
        errors='coerce'
    )

    if pd.isna(den) or den == 0:
        return pd.Series(
            np.nan,
            index=num.index,
            dtype='float64'
        )

    return num.astype('float64') / float(den)

# ============================================================
# 1. 데이터 적재·공통 정제
# ============================================================
df = pd.read_parquet(DATA_PATH, engine='pyarrow', dtype_backend='pyarrow')
df = df.copy()
df['_row_id'] = np.arange(len(df))

for col in ['운영센터', '분류', '서비스LV2', '표준설비', '법정관리',
            '작업상태', '발생유형']:
    if col in df.columns:
        df[col] = df[col].astype('string').str.strip()

for col in ['완료예정일자', '완료일자', '작업시작일시', '작업완료일시']:
    if col in df.columns:
        df[f'{col}_dt'] = pd.to_datetime(df[col], errors='coerce')

# 현재 데이터 구조상 요청일시 후보 컬럼은 존재하지 않음.
# 향후 원천자료에 요청일시 컬럼이 추가되면 아래 목록에 컬럼명을 추가하면 됨.
REQUEST_DATETIME_CANDIDATES = [
    '요청일시', '접수일시', 'VOC접수일시', '민원접수일시',
    '요청일자', '접수일자', 'VOC접수일자'
]

def resolve_request_datetime(data):
    """요청일시 후보를 찾아 datetime Series로 반환한다."""
    for col in REQUEST_DATETIME_CANDIDATES:
        if col in data.columns:
            return pd.to_datetime(data[col], errors='coerce'), col
    return pd.Series(pd.NaT, index=data.index, dtype='datetime64[ns]'), None


def check_center(center_name):
    centers = sorted(df['운영센터'].dropna().unique().tolist())
    if center_name not in centers:
        raise ValueError(f"'{center_name}'은(는) 운영센터 목록에 없습니다. 가능 값: {centers}")

check_center(center)

# ============================================================
# 2. 중요 표준설비 20개 선정 및 선정 이유
# ============================================================
# 선정 기준:
# ① 전기·소방·비상전원·공조 등 건물 운영 중단 및 안전사고와 직결
# ② 법정·안전관리 또는 재난대응과의 연계성
# ③ 실제 데이터에 존재하는 표준설비명 사용
# ④ SLA 평가에서 발주처가 확인 가능한 작업대상
IMPORTANT_EQUIPMENT_REASONS = {
    'MAIN기중차단기(ACB)': '수전·주배전 계통의 과전류 및 사고 차단과 직결되는 핵심 전기설비',
    'SUB기중차단기(ACB)': '구역별 배전 보호와 정전·전기안전 리스크 관리에 중요한 설비',
    'MAIN진공차단기(VCB)': '고압 수전·배전 계통의 사고전류 차단과 전원 안정성에 핵심',
    'SUB진공차단기(VCB)': '고압 배전 구간의 보호·분리 및 정전 예방에 중요한 설비',
    '변압기(TR_몰드)': '전압 변환 및 건물 전력공급의 핵심 설비로 장애 시 운영 영향이 큼',
    '분전반(전등/전열)': '조명·콘센트 계통의 말단 전원공급과 과부하 관리에 중요',
    '분전반(동력)': '펌프·팬·공조 등 동력설비 운전 전원을 담당하는 핵심 분전설비',
    '모터컨트롤센터(MCC_판넬)': '펌프·팬 등 주요 모터설비의 제어·보호 및 운전 안정성에 중요',
    '발전기(디젤 수냉식)': '정전 시 비상전원을 공급하여 핵심 시설의 연속운영을 지원',
    '자동절체스위치(ATS)': '상용전원과 비상전원 간 자동 절체로 정전 대응의 신뢰성을 좌우',
    '무정전전원공급장치(UPS)': '전산·통신·제어 등 순간정전 민감 부하의 연속전원을 보장',
    'UPS&배터리 시스템': '비상전원 유지시간과 UPS 성능을 좌우하는 저장전원 설비',
    '소화기': '초기 화재 대응의 기본 설비로 배치·유효기간·상태점검이 중요',
    '옥내소화전(발신기일체형)': '건물 내부 화재 대응과 경보·소화 활동에 동시에 연계되는 설비',
    '방화문': '화재·연기 확산 방지를 위한 방화구획 유지에 핵심',
    '방화셔터': '화재 시 개구부를 차단하여 연소 확대를 방지하는 방화설비',
    'R형 수신기': '화재신호 수신·표시·감시의 중심으로 소방 대응 판단에 중요',
    '감지기(열/연)': '화재를 조기에 감지하여 수신기 및 경보체계로 전달하는 핵심 설비',
    '공기조화기': '실내 온·습도·공기질 및 연구·업무환경 유지에 직접적인 영향을 줌',
    '냉각탑': '냉방 열원계통의 핵심으로 여름철 냉방 안정성과 설비 효율에 영향',
}
IMPORTANT_EQUIPMENT = list(IMPORTANT_EQUIPMENT_REASONS.keys())

important_equipment_master = pd.DataFrame({
    '표준설비': IMPORTANT_EQUIPMENT,
    '선정이유': [IMPORTANT_EQUIPMENT_REASONS[x] for x in IMPORTANT_EQUIPMENT],
    '선정순번': np.arange(1, len(IMPORTANT_EQUIPMENT) + 1),
})
important_equipment_master.to_csv(
    OUTPUT_DIR / '01_중요표준설비_20개_선정근거.csv', index=False, encoding='utf-8-sig'
)

# 법정·안전설비: 선정된 20개 가운데 소방·전기안전·비상전원과 직접 연결되는 대상
LEGAL_SAFETY_EQUIPMENT_REASONS = {
    'MAIN기중차단기(ACB)': '수배전설비 보호 및 전기안전 관리 대상',
    'SUB기중차단기(ACB)': '배전설비 보호 및 전기안전 관리 대상',
    'MAIN진공차단기(VCB)': '고압 전기설비 보호와 정전·사고 예방 대상',
    'SUB진공차단기(VCB)': '고압 배전설비 보호와 전기안전 관리 대상',
    '변압기(TR_몰드)': '수변전설비의 절연·열화·전기안전 관리 대상',
    '발전기(디젤 수냉식)': '비상전원 및 정전 대응을 위한 안전 핵심설비',
    '자동절체스위치(ATS)': '비상전원 절체 및 비상운전 신뢰성에 직결',
    '무정전전원공급장치(UPS)': '비상·무정전 전원 공급을 위한 핵심설비',
    'UPS&배터리 시스템': '비상전원 저장·공급 및 전원 장애 대응 대상',
    '소화기': '소방시설의 초기 화재 대응 설비',
    '옥내소화전(발신기일체형)': '소화·발신 기능이 결합된 소방시설',
    '방화문': '방화구획 및 연소 확대 방지를 위한 소방안전 설비',
    '방화셔터': '방화구획 및 화재 확산 방지를 위한 소방안전 설비',
    'R형 수신기': '자동화재탐지 및 경보 수신의 핵심설비',
    '감지기(열/연)': '자동화재탐지의 감지부로 조기경보에 핵심',
}
LEGAL_SAFETY_EQUIPMENT = list(LEGAL_SAFETY_EQUIPMENT_REASONS.keys())

legal_safety_master = pd.DataFrame({
    '표준설비': LEGAL_SAFETY_EQUIPMENT,
    '선정이유': [LEGAL_SAFETY_EQUIPMENT_REASONS[x] for x in LEGAL_SAFETY_EQUIPMENT],
})
legal_safety_master.to_csv(
    OUTPUT_DIR / '02_법정안전설비_선정근거.csv', index=False, encoding='utf-8-sig'
)

# ============================================================
# 3. 이행률 공통 함수
# ============================================================
def make_execution_rate_table(data, equipment_list, group_cols=None):
    """
    이행률 정의
    - 등록건수: 해당 표준설비에 등록된 전체 작업건수
    - 완료건수: 작업상태가 작업완료 또는 지연완료인 건수
    - 기한내완료건수: 작업상태가 작업완료인 건수
    - 이행률: 완료건수 / 등록건수
    - 기한내이행률: 작업완료건수 / 등록건수

    현재 데이터의 작업상태가 '작업완료', '지연완료'로 구성되어 있으므로
    이행률과 기한내이행률을 분리해 제시한다.
    """
    x = data[data['표준설비'].isin(equipment_list)].copy()
    if group_cols is None:
        group_cols = ['표준설비']

    result = (
        x.groupby(group_cols, dropna=False, observed=True)
         .agg(
             등록건수=('_row_id', 'size'),
             완료건수=('작업상태', lambda s: s.isin(VALID_STATUSES).sum()),
             기한내완료건수=('작업상태', lambda s: (s == STATUS_COMPLETED).sum()),
             지연완료건수=('작업상태', lambda s: (s == STATUS_DELAYED).sum()),
             상태미확인건수=('작업상태', lambda s: (~s.isin(VALID_STATUSES)).sum()),
         )
         .reset_index()
    )
    # groupby 결과가 object/string dtype이 되는 경우를 대비해 숫자형으로 강제 변환
    for col in ['등록건수', '완료건수', '기한내완료건수', '지연완료건수', '상태미확인건수']:
        result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0)

    result['이행률'] = safe_divide(result['완료건수'], result['등록건수'])
    result['기한내이행률'] = safe_divide(result['기한내완료건수'], result['등록건수'])
    result['지연률'] = safe_divide(result['지연완료건수'], result['등록건수'])
    return result

# ============================================================
# 4. 운영센터별 표준설비 이행률
# ============================================================
def important_equipment_execution(center_name=None):
    """중요 표준설비 20개별 이행률. center_name=None이면 전체 센터."""
    x = df if center_name is None else df[df['운영센터'].eq(center_name)]
    result = make_execution_rate_table(x, IMPORTANT_EQUIPMENT)
    result = important_equipment_master.merge(result, on='표준설비', how='left')
    result['운영센터'] = center_name if center_name is not None else '전체'
    return result

important_rate_by_center = important_equipment_execution(center)
important_rate_by_center.to_csv(
    OUTPUT_DIR / f'03_중요표준설비_이행률_{center}.csv', index=False, encoding='utf-8-sig'
)

# 모든 운영센터를 비교하고 싶을 때: 센터별로 별도 산출
all_center_rows = []
for c in sorted(df['운영센터'].dropna().unique()):
    r = important_equipment_execution(c)
    all_center_rows.append(r)
important_rate_all_centers = pd.concat(all_center_rows, ignore_index=True)
important_rate_all_centers.to_csv(
    OUTPUT_DIR / '04_중요표준설비_센터별_이행률.csv', index=False, encoding='utf-8-sig'
)

# 중요설비 이행률 차트: 센터 변수에 따라 제목·파일명 변경
plot_rate = important_rate_by_center.dropna(subset=['등록건수']).copy()
plot_rate['기한내이행률(%)'] = plot_rate['기한내이행률'] * 100
plot_rate = plot_rate.sort_values('기한내이행률(%)', ascending=True)
fig = px.bar(
    plot_rate,
    x='기한내이행률(%)', y='표준설비', orientation='h',
    text='기한내이행률(%)',
    title=f'{center} 중요 표준설비별 기한내 이행률',
    labels={'기한내이행률(%)': '기한내 이행률(%)', '표준설비': '표준설비'},
    color='기한내이행률(%)', color_continuous_scale='Blues'
)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(template='plotly_white', height=760, coloraxis_showscale=False)
fig.write_html(OUTPUT_DIR / f'05_중요표준설비_기한내이행률_{center}.html', include_plotlyjs='cdn')

# ============================================================
# 5. 법정·안전설비 이행률
# ============================================================
def legal_safety_execution(center_name=None):
    x = df if center_name is None else df[df['운영센터'].eq(center_name)]
    result = make_execution_rate_table(x, LEGAL_SAFETY_EQUIPMENT)
    result = legal_safety_master.merge(result, on='표준설비', how='left')
    result['운영센터'] = center_name if center_name is not None else '전체'
    # 실제 원자료의 법정관리 플래그도 함께 집계
    legal_flag = (
        x[x['표준설비'].isin(LEGAL_SAFETY_EQUIPMENT)]
        .groupby('표준설비', observed=True)['법정관리']
        .apply(lambda s: (s == '법정').sum())
        .rename('법정관리표시건수')
        .reset_index()
    )
    result = result.merge(legal_flag, on='표준설비', how='left')
    result['법정관리표시건수'] = result['법정관리표시건수'].fillna(0).astype(int)
    return result

legal_rate_by_center = legal_safety_execution(center)
legal_rate_by_center.to_csv(
    OUTPUT_DIR / f'06_법정안전설비_이행률_{center}.csv', index=False, encoding='utf-8-sig'
)

plot_legal = legal_rate_by_center.dropna(subset=['등록건수']).copy()
plot_legal['기한내이행률(%)'] = plot_legal['기한내이행률'] * 100
plot_legal = plot_legal.sort_values('기한내이행률(%)', ascending=True)
fig = px.bar(
    plot_legal,
    x='기한내이행률(%)', y='표준설비', orientation='h',
    text='기한내이행률(%)',
    title=f'{center} 법정·안전설비별 기한내 이행률',
    labels={'기한내이행률(%)': '기한내 이행률(%)', '표준설비': '법정·안전설비'},
    color='기한내이행률(%)', color_continuous_scale='Reds'
)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(template='plotly_white', height=650, coloraxis_showscale=False)
fig.write_html(OUTPUT_DIR / f'07_법정안전설비_기한내이행률_{center}.html', include_plotlyjs='cdn')

# ============================================================
# 6. 법정검사·신고 이행률
# ============================================================
def statutory_inspection_execution(center_name=None):
    """
    서비스LV2 == '법정검사/신고'를 법정검사·신고 업무로 정의한다.
    - 전체 이행률: 완료 또는 지연완료 / 등록건수
    - 기한내 이행률: 작업완료 / 등록건수
    - 지연률: 지연완료 / 등록건수
    - 법정관리 표시율: 법정관리 표기 / 등록건수
    표준설비별 결과도 함께 제공한다.
    """
    x = df if center_name is None else df[df['운영센터'].eq(center_name)]
    x = x[x['서비스LV2'].eq('법정검사/신고')].copy()

    overall = pd.DataFrame([{
        '운영센터': center_name if center_name is not None else '전체',
        '등록건수': len(x),
        '완료건수': x['작업상태'].isin(VALID_STATUSES).sum(),
        '기한내완료건수': (x['작업상태'] == STATUS_COMPLETED).sum(),
        '지연완료건수': (x['작업상태'] == STATUS_DELAYED).sum(),
        '법정관리표시건수': (x['법정관리'] == '법정').sum(),
    }])
    for col in ['등록건수', '완료건수', '기한내완료건수', '지연완료건수', '법정관리표시건수']:
        overall[col] = pd.to_numeric(overall[col], errors='coerce').fillna(0)
    overall['이행률'] = safe_divide(overall['완료건수'], overall['등록건수'])
    overall['기한내이행률'] = safe_divide(overall['기한내완료건수'], overall['등록건수'])
    overall['지연률'] = safe_divide(overall['지연완료건수'], overall['등록건수'])
    overall['법정관리표시율'] = safe_divide(overall['법정관리표시건수'], overall['등록건수'])

    equipment_values = x['표준설비'].dropna().unique().tolist()
    by_equipment = make_execution_rate_table(x, equipment_values)
    by_equipment['법정관리표시건수'] = (
        x.groupby('표준설비', dropna=False, observed=True)['법정관리']
         .apply(lambda s: (s == '법정').sum())
         .reindex(by_equipment['표준설비']).fillna(0).to_numpy()
    ).astype(int)
    by_equipment['법정관리표시율'] = safe_divide(
        by_equipment['법정관리표시건수'], by_equipment['등록건수']
    )
    return overall, by_equipment

statutory_overall, statutory_by_equipment = statutory_inspection_execution(center)
statutory_overall.to_csv(
    OUTPUT_DIR / f'08_법정검사신고_전체이행률_{center}.csv', index=False, encoding='utf-8-sig'
)
statutory_by_equipment.to_csv(
    OUTPUT_DIR / f'09_법정검사신고_표준설비별이행률_{center}.csv', index=False, encoding='utf-8-sig'
)

# ============================================================
# 7. 보수 및 불편신고 처리율
# ============================================================
def repair_voc_processing(center_name=None):
    """
    보수 및 불편신고 분석.
    요청 건수 정의:
    - 보수 전체
    - 그중 VOC 및 요청 유형(VOC, 작업자요청, 센터직원요청, 현장대리인요청, 센터장요청)

    시간 정의:
    - 요청→착수: 실제 요청일시 컬럼이 있을 때만 산출
    - 착수→완료: 작업시작일시와 작업완료일시 차이
    - 지연률: 작업상태가 지연완료인 건수 / 분석대상 건수
    """
    x = df if center_name is None else df[df['운영센터'].eq(center_name)]
    x = x[x['서비스LV2'].eq('보수')].copy()
    x['요청일시_dt'], request_col = resolve_request_datetime(x)

    request_types = ['VOC', '작업자요청', '센터직원요청', '현장대리인요청', '센터장요청', 'RMS(원격감시)']
    x['요청여부'] = x['발생유형'].isin(request_types)
    x['불편신고여부'] = x['발생유형'].eq('VOC')

    # 시간 계산: 음수/이상값은 NaN 처리
    x['요청_to_착수_분'] = (x['작업시작일시_dt'] - x['요청일시_dt']).dt.total_seconds() / 60
    x['착수_to_완료_분'] = (x['작업완료일시_dt'] - x['작업시작일시_dt']).dt.total_seconds() / 60
    x.loc[x['요청_to_착수_분'] < 0, '요청_to_착수_분'] = np.nan
    x.loc[x['착수_to_완료_분'] < 0, '착수_to_완료_분'] = np.nan
    x.loc[x['착수_to_완료_분'] > 30 * 24 * 60, '착수_to_완료_분'] = np.nan

    def summarize(g, label):
        n = len(g)
        request_to_start = g['요청_to_착수_분'].dropna()
        start_to_end = g['착수_to_완료_분'].dropna()
        return {
            '운영센터': center_name if center_name is not None else '전체',
            '구분': label,
            '요청건수': n,
            '작업완료건수': (g['작업상태'].isin(VALID_STATUSES)).sum(),
            '기한내완료건수': (g['작업상태'] == STATUS_COMPLETED).sum(),
            '지연완료건수': (g['작업상태'] == STATUS_DELAYED).sum(),
            '지연률': (g['작업상태'] == STATUS_DELAYED).mean() if n else np.nan,
            '요청→착수_측정건수': request_to_start.size,
            '요청→착수_평균분': request_to_start.mean() if len(request_to_start) else np.nan,
            '요청→착수_중앙값분': request_to_start.median() if len(request_to_start) else np.nan,
            '착수→완료_측정건수': start_to_end.size,
            '착수→완료_평균분': start_to_end.mean() if len(start_to_end) else np.nan,
            '착수→완료_중앙값분': start_to_end.median() if len(start_to_end) else np.nan,
            '요청일시_사용컬럼': request_col if request_col else '없음',
        }

    rows = [summarize(x, '보수 전체')]
    for request_type in request_types:
        rows.append(summarize(x[x['발생유형'].eq(request_type)], request_type))
    rows.append(summarize(x[x['요청여부']], '불편·요청성 보수 합계'))
    rows.append(summarize(x[x['불편신고여부']], 'VOC 보수'))

    summary = pd.DataFrame(rows)
    by_type = (
        x.groupby('발생유형', dropna=False, observed=True)
         .agg(
             요청건수=('_row_id', 'size'),
             지연완료건수=('작업상태', lambda s: (s == STATUS_DELAYED).sum()),
             작업완료건수=('작업상태', lambda s: s.isin(VALID_STATUSES).sum()),
             요청_to_착수_측정건수=('요청_to_착수_분', 'count'),
             요청_to_착수_평균분=('요청_to_착수_분', 'mean'),
             요청_to_착수_중앙값분=('요청_to_착수_분', 'median'),
             착수_to_완료_측정건수=('착수_to_완료_분', 'count'),
             착수_to_완료_평균분=('착수_to_완료_분', 'mean'),
             착수_to_완료_중앙값분=('착수_to_완료_분', 'median'),
         ).reset_index()
    )
    by_type['지연률'] = safe_divide(
        by_type['지연완료건수'], by_type['요청건수']
    )
    return x, summary, by_type, request_col

repair_detail, repair_summary, repair_by_type, request_datetime_col = repair_voc_processing(center)
repair_summary.to_csv(
    OUTPUT_DIR / f'10_보수불편신고_처리율_요약_{center}.csv', index=False, encoding='utf-8-sig'
)
repair_by_type.to_csv(
    OUTPUT_DIR / f'11_보수불편신고_발생유형별_{center}.csv', index=False, encoding='utf-8-sig'
)

if request_datetime_col is None:
    warnings.warn(
        '현재 원자료에 요청일시/접수일시 컬럼이 없어 요청→착수 시간은 산출되지 않습니다. '
        '요청일시를 추가한 뒤 REQUEST_DATETIME_CANDIDATES에 컬럼명을 등록하세요.',
        UserWarning
    )

# 보수 발생유형별 요청 건수·지연률 차트
plot_req = repair_by_type.sort_values('요청건수', ascending=True).copy()
fig = make_subplots(rows=1, cols=2, subplot_titles=('요청 건수', '지연률'))
fig.add_trace(
    go.Bar(y=plot_req['발생유형'], x=plot_req['요청건수'], orientation='h', marker_color='#4C78A8', name='요청건수'),
    row=1, col=1
)
fig.add_trace(
    go.Bar(y=plot_req['발생유형'], x=plot_req['지연률'] * 100, orientation='h', marker_color='#E45756', name='지연률(%)'),
    row=1, col=2
)
fig.update_xaxes(title_text='건수', row=1, col=1)
fig.update_xaxes(title_text='지연률(%)', ticksuffix='%', row=1, col=2)
fig.update_layout(
    title=f'{center} 보수업무의 요청 유형별 처리 현황',
    template='plotly_white', height=520, showlegend=False
)
fig.write_html(OUTPUT_DIR / f'12_보수불편신고_요청건수_지연률_{center}.html', include_plotlyjs='cdn')

# 보수 서비스LV2 고정색상 차트: 다른 분석 차트와 비교 가능하도록 색상 고정
service_share = (
    df[df['운영센터'].eq(center)]
      .groupby('서비스LV2', observed=True)
      .size()
      .rename('작업건수')
      .reset_index()
)
service_share['센터내비율(%)'] = safe_divide(
    service_share['작업건수'], service_share['작업건수'].sum()
) * 100
service_share = service_share.sort_values('센터내비율(%)', ascending=True)
fig = px.bar(
    service_share, x='센터내비율(%)', y='서비스LV2', orientation='h',
    color='서비스LV2', color_discrete_map=SERVICE_COLORS,
    title=f'{center} 서비스LV2 센터 내부 작업비율',
    labels={'센터내비율(%)': '운영센터 내부 작업비율(%)', '서비스LV2': '서비스LV2'},
    text='센터내비율(%)'
)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(template='plotly_white', height=520, legend_title_text='서비스LV2')
fig.write_html(OUTPUT_DIR / f'13_서비스LV2_센터내비율_{center}.html', include_plotlyjs='cdn')

# ============================================================
# 8. 콘솔 출력: 보고서 작성 시 확인할 핵심 표
# ============================================================
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 220)
print(f'분석 운영센터: {center}')
print('\n[중요 표준설비별 이행률]')
print(important_rate_by_center[['표준설비', '등록건수', '기한내완료건수', '지연완료건수', '기한내이행률', '지연률']].to_string(index=False))
print('\n[법정·안전설비별 이행률]')
print(legal_rate_by_center[['표준설비', '등록건수', '법정관리표시건수', '기한내이행률', '지연률']].to_string(index=False))
print('\n[법정검사·신고 전체 이행률]')
print(statutory_overall.to_string(index=False))
print('\n[보수·불편신고 처리율]')
print(repair_summary.to_string(index=False))
print(f'\n요청일시 사용 컬럼: {request_datetime_col}')
print(f'결과 저장 위치: {OUTPUT_DIR}')
