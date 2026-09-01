"""
중요설비 표본 개수 적정성 검토

방법
1. Integrated_data.xlsx의 분류별(연구소/오피스) 전체 표준설비 수 확인
2. 전체 표준설비의 약 20%를 후보군으로 산정
3. 최소 20개, 최대 50개 범위로 보정
4. 설비분류LV1별 최소 2개 포함을 고려한 추천 개수 산출
5. 20/30/40/50/70개 민감도 분석 및 Plotly 시각화
"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px

# ============================================================
# 0. 설정
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
# 1. 데이터 적재·정제
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
# 2. 분류별 전체 표준설비 수 및 추천 후보군 수
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
# 3. 설비분류LV1별 대표성 확인
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

# ============================================================
# 4. 민감도 분석
# ============================================================
def sensitivity_table(data, class_name):
    x = data[data[CLASS_COL].eq(class_name)].copy()
    total_equipment = x[EQUIPMENT_COL].nunique()

    rows = []
    for candidate_size in SENSITIVITY_SIZES:
        actual_size = min(candidate_size, total_equipment)
        rows.append({
            CLASS_COL: class_name,
            '후보군수': candidate_size,
            '실제가능후보군수': actual_size,
            '전체표준설비수': total_equipment,
            '전체대비비율(%)': actual_size / total_equipment * 100
            if total_equipment else np.nan,
            '설비분류LV1수': x[LV1_COL].nunique(dropna=True),
        })
    return pd.DataFrame(rows)

sensitivity_df = pd.concat(
    [sensitivity_table(base, class_name) for class_name in CLASS_LIST],
    ignore_index=True
)

# ============================================================
# 5. 저장
# ============================================================
recommendation_df.to_csv(
    OUTPUT_DIR / '중요설비_후보군_추천개수.csv',
    index=False,
    encoding='utf-8-sig'
)

lv1_df.to_csv(
    OUTPUT_DIR / '분류별_설비분류LV1_대표성_확인.csv',
    index=False,
    encoding='utf-8-sig'
)

sensitivity_df.to_csv(
    OUTPUT_DIR / '중요설비_후보군_민감도분석.csv',
    index=False,
    encoding='utf-8-sig'
)

# ============================================================
# 6. Plotly 시각화
# ============================================================
plot_rec = recommendation_df[recommendation_df[CLASS_COL].isin(CLASS_LIST)].copy()
fig = px.bar(
    plot_rec,
    x=CLASS_COL,
    y=['전체표준설비수', '최종추천후보수'],
    barmode='group',
    text_auto=True,
    title='분류별 전체 표준설비 수와 추천 중요설비 후보군 수',
    labels={'value': '설비 수', 'variable': '구분', CLASS_COL: '분류'},
    color_discrete_map={
        '전체표준설비수': '#B8C4CE',
        '최종추천후보수': '#1F77B4'
    }
)
fig.update_layout(template='plotly_white', height=500)
fig.write_html(
    OUTPUT_DIR / '분류별_중요설비_후보군_추천개수.html',
    include_plotlyjs='cdn'
)

fig2 = px.line(
    sensitivity_df,
    x='후보군수',
    y='전체대비비율(%)',
    color=CLASS_COL,
    markers=True,
    title='후보군 규모별 전체 표준설비 대비 비율',
    labels={'후보군수': '후보군 수', '전체대비비율(%)': '전체 대비 비율(%)', CLASS_COL: '분류'}
)
fig2.update_layout(template='plotly_white', height=500)
fig2.update_yaxes(ticksuffix='%')
fig2.write_html(
    OUTPUT_DIR / '중요설비_후보군_민감도분석.html',
    include_plotlyjs='cdn'
)

# ============================================================
# 7. 출력
# ============================================================
pd.set_option('display.max_columns', 30)
pd.set_option('display.width', 180)
print('\n[중요설비 후보군 추천 결과]')
print(recommendation_df.to_string(index=False))
print('\n[설비분류LV1 대표성 확인]')
print(lv1_df.to_string(index=False))
print(f'\n결과 저장 위치: {OUTPUT_DIR}')
