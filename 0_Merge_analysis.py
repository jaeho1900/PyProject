"""
# 운영센터 '작업관리' 분석 및 시각화
"""

from datetime import datetime
from pathlib import Path
import re
import sys
import tkinter as tk
from tkinter import filedialog

import numpy as np
import pandas as pd
import plotly.express as px

# ----------------------------
# 상수 정의
# ----------------------------
VALID_STATUSES = ['작업완료', '지연완료']

SAFETY_5 = ['소화', '감지', '발신기', '수신기', '방화', '피난', '가스', '누수', '차단기', '변압기', '발전기', 'UPS', '배터리', '비상']
SAFETY_4 = ['전기', '분전반', 'MCC', '모터컨트롤', '냉동기', '보일러', '냉각탑', '공기조화기', '승강기', '엘리베이터', '펌프']
OPERATION_5 = ['MAIN', '차단기', '변압기', '발전기', 'UPS', '배터리', '수신기', '소화펌프', '냉동기', '냉각탑', '공기조화기', '보일러']
OPERATION_4 = ['SUB', '분전반', 'MCC', '모터컨트롤', '방화', '소화', '감지', '발신기', '가스']

# 정규식 패턴 사전 컴파일 (속도 최적화)
SAFETY_5_REGEX = '|'.join(map(re.escape, SAFETY_5))
SAFETY_4_REGEX = '|'.join(map(re.escape, SAFETY_4))
OPERATION_5_REGEX = '|'.join(map(re.escape, OPERATION_5))
OPERATION_4_REGEX = '|'.join(map(re.escape, OPERATION_4))


def vector_score(series, pattern_5, pattern_4):
    """Pandas 벡터화 연산을 통해 안전/운영 영향도 점수를 빠르게 계산"""
    s_str = series.fillna('').astype(str).str.upper()
    cond5 = s_str.str.contains(pattern_5, regex=True, case=False)
    cond4 = s_str.str.contains(pattern_4, regex=True, case=False)

    return np.select([cond5, cond4], [5, 4], default=2)


def percentile_score(series):
    return series.rank(method='average', pct=True) * 100


def get_priority_table(data):
    # 유효 데이터 필터링 & 타입 정리
    df = data.dropna(subset=['표준설비', '총작업시간(분)_E']).copy()

    for col in ['표준설비', '설비분류LV1', '작업상태', '법정관리']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df['총작업시간(분)_E'] = pd.to_numeric(df['총작업시간(분)_E'], errors='coerce')
    df = df.dropna(subset=['총작업시간(분)_E'])

    # 단일 groupby 기반 집계
    r = df.groupby(['설비분류LV1', '표준설비'], observed=True).agg(
        작업건수=('표준설비', 'size'),
        총작업시간_분_E=('총작업시간(분)_E', 'sum'),
        완료건수=('작업상태', lambda s: s.isin(VALID_STATUSES).sum()),
        기한내완료건수=('작업상태', lambda s: (s == '작업완료').sum()),
        지연완료건수=('작업상태', lambda s: (s == '지연완료').sum()),
        법정관리건수=('법정관리', lambda s: (s == '법정').sum()),
    ).reset_index()

    total_cnt = r['작업건수'].replace(0, np.nan)
    r['총작업시간_시간_E'] = r['총작업시간_분_E'] / 60
    r['이행률'] = r['완료건수'] / total_cnt
    r['기한내이행률'] = r['기한내완료건수'] / total_cnt
    r['지연률'] = r['지연완료건수'] / total_cnt
    r['법정관리표시율'] = r['법정관리건수'] / total_cnt

    # 정규식 기반 벡터화 점수 산출
    r['안전영향도'] = vector_score(r['표준설비'], SAFETY_5_REGEX, SAFETY_4_REGEX)
    r['운영중단영향도'] = vector_score(r['표준설비'], OPERATION_5_REGEX, OPERATION_4_REGEX)

    r['법정·규제영향도'] = np.select(
        [r['법정관리표시율'].ge(.8), r['법정관리표시율'].ge(.5), r['법정관리표시율'].gt(0)],
        [5, 4, 3], default=2
    )

    r['설비중요도점수'] = (r['안전영향도'] / 5 * 40) + (r['법정·규제영향도'] / 5 * 30) + (r['운영중단영향도'] / 5 * 30)
    r['업무부하점수'] = percentile_score(r['총작업시간_분_E'])
    r['관리빈도점수'] = percentile_score(r['작업건수'])
    r['품질성과점수'] = (0.5 * r['이행률'] * 100) + (0.5 * (1 - r['지연률']) * 100)

    r['종합우선순위점수'] = (r['설비중요도점수'] + r['업무부하점수'] + r['관리빈도점수'] + r['품질성과점수']) / 4

    r = r.sort_values(
        ['종합우선순위점수', '설비중요도점수', '총작업시간_분_E', '작업건수'],
        ascending=[False, False, False, False]
    ).reset_index(drop=True)

    r['전체평가순위'] = np.arange(1, len(r) + 1)
    return r


def select_top50_with_minimum_by_class(priority, class_col='설비분류LV1', top_n=50, minimum=2):
    """
    메모리 재할당(concat) 없이 Index 스왑 방식 알고리즘 적용
    """
    if len(priority) <= top_n:
        selected = priority.copy()
        selected['_selected_reason'] = '전체평가순위 TOP50'
        selected['보정후순위'] = np.arange(1, len(selected) + 1)
        return selected

    selected_indices = list(range(top_n))
    selected_reasons = {i: '전체평가순위 TOP50' for i in range(top_n)}

    # 분류별 선택 인덱스 추적
    class_series = priority[class_col]

    for class_name in class_series.dropna().unique():
        current_in_top = [idx for idx in selected_indices if class_series.iloc[idx] == class_name]
        if len(current_in_top) >= minimum:
            continue

        need = minimum - len(current_in_top)

        # 외부 후보군 (순위가 낮은 순서대로 탐색)
        candidate_indices = [
            idx for idx in range(top_n, len(priority))
            if class_series.iloc[idx] == class_name
        ][:need]

        for cand_idx in candidate_indices:
            # 보정 탈락 가능 후보: 선택된 인덱스 중 분류 최소 수량(minimum) 초과 보유 분류의 가장 순위 낮은 인덱스
            current_counts = class_series.iloc[selected_indices].value_counts()
            removable_candidates = [
                idx for idx in reversed(selected_indices)
                if current_counts.get(class_series.iloc[idx], 0) > minimum
            ]

            if not removable_candidates:
                raise ValueError('최소 분류 수를 보장하면서 정확한 TOP50을 만들 수 없습니다.')

            remove_idx = removable_candidates[0] # 가장 순위가 낮은 항목

            selected_indices.remove(remove_idx)
            selected_indices.append(cand_idx)
            selected_reasons[cand_idx] = f'{class_name} 최소 {minimum}개 보정'

    selected_indices.sort()
    selected = priority.iloc[selected_indices].copy()
    selected['_selected_reason'] = [selected_reasons[i] for i in selected_indices]
    selected['보정후순위'] = np.arange(1, len(selected) + 1)

    return selected


def work_play1(combined_df, folder_path):
    priority = get_priority_table(combined_df)
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

    # CSV 저장
    priority.to_csv(folder_path / '전체표준설비_평가순위.csv', index=False, encoding='utf-8-sig')
    top50.to_csv(folder_path / '표준설비_TOP50_분류보정.csv', index=False, encoding='utf-8-sig')
    group_summary.to_csv(folder_path / '표준설비_TOP50_설비분류LV1_요약.csv', index=False, encoding='utf-8-sig')

    # 시각화 1: 분류별 TOP50
    plot_df = group_summary.sort_values(by="포함설비수", ascending=False).copy()
    plot_df["평균종합점수_라벨"] = plot_df["평균종합점수"].map(lambda x: f"{x:.2f}")

    fig = px.bar(
        plot_df, x="포함설비수", y="설비분류LV1", orientation="h",
        text="포함설비수", color="평균종합점수_라벨",
        title="표준설비 TOP50 - 설비분류별",
        labels={"포함설비수": "TOP50 표준설비 수", "설비분류LV1": "설비분류", "평균종합점수_라벨": "종합점수 평균"}
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        template="plotly_white", height=500,
        yaxis=dict(autorange="reversed"),
        legend=dict(title="종합점수 평균", traceorder="normal")
    )
    fig.write_html(folder_path / '설비분류_TOP50.html', include_plotlyjs='cdn')

    # 시각화 2: TOP50 설비
    plot2_sorted = top50.head(50).assign(설비중요도점수=lambda x: x["설비중요도점수"].astype(float)).sort_values("보정후순위", ascending=False)

    fig1 = px.bar(
        plot2_sorted, x="종합우선순위점수", y="표준설비", orientation="h",
        color="설비중요도점수", text="종합우선순위점수", color_continuous_scale="Blues",
        title="표준설비 TOP50",
        labels={"종합우선순위점수": "종합 점수", "표준설비": "표준설비", "설비중요도점수": "설비 중요도 점수"},
        hover_data=["작업건수", "총작업시간_시간_E", "이행률", "지연률", "업무부하점수", "관리빈도점수"]
    )
    fig1.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig1.update_layout(
        template="plotly_white", height=700,
        coloraxis_showscale=False, xaxis=dict(range=[0, 105])
    )
    fig1.write_html(folder_path / '표준설비_TOP50.html', include_plotlyjs='cdn')


def work_play2(combined_df, folder_path):
    facility_summary = (
        combined_df.groupby(["표준설비", "서비스LV2"])["총작업시간(분)_E"]
        .agg(
            작업건수="count",
            총작업시간_분="sum",
            평균작업시간_분="mean",
            중앙작업시간_분="median",
            최대작업시간_분="max",
        )
        .reset_index()
    )

    num_cols = ["평균작업시간_분", "중앙작업시간_분", "총작업시간_분"]
    facility_summary[num_cols] = facility_summary[num_cols].round(2)
    facility_summary["설비라벨"] = facility_summary["표준설비"].astype(str) + " (" + facility_summary["서비스LV2"].astype(str) + ")"

    # 조건 필터링
    cond = (facility_summary['서비스LV2'] == '보수') | (facility_summary['표준설비'].str.contains('건물', na=False))
    facility_summary = facility_summary[~cond].reset_index(drop=True)
    facility_summary.to_csv(folder_path / '표준설비_공수패턴.csv', index=False, encoding='utf-8-sig')

    scatter_data = facility_summary[facility_summary["작업건수"] >= 20]

    fig2 = px.scatter(
        scatter_data, x="작업건수", y="평균작업시간_분", size="총작업시간_분",
        color="서비스LV2", hover_name="설비라벨", log_x=True,
        title="<b>[표준설비별 공수 패턴] 작업 빈도(건수) vs 건당 평균 소요시간</b>",
        labels={"작업건수": "작업 발생건수 (Log Scale)", "평균작업시간_분": "건당 평균 작업시간 (분)"},
        template="plotly_white", height=600
    )
    fig2.write_html(folder_path / '표준설비_공수_패턴.html', include_plotlyjs='cdn')


def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    folder_selected = filedialog.askdirectory(title="Excel 파일이 있는 폴더를 선택하세요")
    root.destroy()

    if not folder_selected:
        print("폴더가 선택되지 않았습니다.")
        return

    folder_path = Path(folder_selected)
    excel_files = [
        f for f in folder_path.iterdir()
        if f.suffix.lower() in [".xlsx", ".xls"]
        and not f.name.startswith("~$")
        and not f.name.startswith("작업완료_")
    ]

    if not excel_files:
        print("선택한 폴더에 유효한 Excel 파일이 없습니다.")
        return

    dataframes = []

    for file_path in excel_files:
        try:
            sheets = pd.read_excel(file_path, sheet_name=None)
            for sheet_name, df in sheets.items():
                if df.empty:
                    continue

                # 열 이름 전처리
                df.columns = df.columns.astype(str).str.replace(r"\s+", "", regex=True)

                if "표준설비" not in df.columns:
                    print(f"\n[오류] 파일명: {file_path.name} (시트명: {sheet_name})")
                    print("작업관리에서 분류 숨기기를 해제 후 다운로드하십시오")
                    sys.exit()

                df["원본파일명"] = file_path.name
                df["시트명"] = str(sheet_name)
                dataframes.append(df)

            print(f"읽기 완료: {file_path.name}")

        except Exception as error:
            print(f"읽기 실패: {file_path.name} | 오류: {error}")
            sys.exit()

    if not dataframes:
        print("통합할 유효 데이터가 없습니다.")
        return

    combined_df = pd.concat(dataframes, ignore_index=True)

    # 데이터 필터링
    combined_df = combined_df[
        (combined_df['서비스LV1'] == '시설') &
        (combined_df['총작업시간(분)'].notna())
    ].copy()

    # 시간 수정 로직 벡터화 연산
    work_time = pd.to_numeric(combined_df['작업시간(분)'], errors='coerce').fillna(0)
    total_time = pd.to_numeric(combined_df['총작업시간(분)'], errors='coerce').fillna(0)

    step1_calc = np.select(
        [work_time <= 480, (work_time > 480) & (work_time <= 1440), work_time > 1440],
        [work_time, 480, work_time - ((work_time // 1440) * 960)],
        default=0
    )
    multiplier = np.where(work_time > 0, total_time // work_time, 0)
    combined_df['총작업시간(분)_E'] = multiplier * step1_calc

    # 파일 저장
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"운영센터_시설작업관리_data_{now_str}.xlsx"
    output_path = folder_path / output_filename

    combined_df.to_excel(output_path, index=False)

    # 분석 및 시각화 수행
    work_play1(combined_df, folder_path)
    work_play2(combined_df, folder_path)

    print("\n" + "=" * 30)
    print("통합 완료")
    print(f"행 개수: {len(combined_df):,}")
    print(f"열 개수: {len(combined_df.columns):,}")
    print(f"저장 위치: {output_path}")
    print("=" * 30)


if __name__ == "__main__":
    main()
