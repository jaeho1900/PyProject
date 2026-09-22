# -*- coding: utf-8 -*-
"""
운영센터 '작업관리' 분석 스크립트 - Tkinter GUI 버전

기존 분석 스크립트를 멀티스레딩을 지원하는 데스크톱 애플리케이션으로 변환합니다.
- threading과 queue를 사용하여 GUI 멈춤 현상 방지
- scrolledtext, progressbar로 실시간 진행 상황 피드백
- Treeview와 pywebview를 사용하여 결과 데이터 및 인터랙티브 차트 표시
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import queue
from datetime import datetime
from pathlib import Path
import sys
import re

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import webview

# --- 원본 스크립트의 분석 함수들 ---
# (수정 없이 그대로 사용하거나, 로그/진행률 보고를 위해 약간 수정)
VALID_STATUSES = ['작업완료', '지연완료']
SAFETY_5 = ['소화', '감지', '발신기', '수신기', '방화', '피난', '가스', '누수', '차단기', '변압기', '발전기', 'UPS', '배터리', '비상']
SAFETY_4 = ['전기', '분전반', 'MCC', '모터컨트롤', '냉동기', '보일러', '냉각탑', '공기조화기', '승강기', '엘리베이터', '펌프']
OPERATION_5 = ['MAIN', '차단기', '변압기', '발전기', 'UPS', '배터리', '수신기', '소화펌프', '냉동기', '냉각탑', '공기조화기', '보일러']
OPERATION_4 = ['SUB', '분전반', 'MCC', '모터컨트롤', '방화', '소화', '감지', '발신기', '가스']

SAFETY_5_REGEX = '|'.join(map(re.escape, SAFETY_5))
SAFETY_4_REGEX = '|'.join(map(re.escape, SAFETY_4))
OPERATION_5_REGEX = '|'.join(map(re.escape, OPERATION_5))
OPERATION_4_REGEX = '|'.join(map(re.escape, OPERATION_4))

def vector_score(series, pattern_5, pattern_4):
    s_str = series.fillna('').astype(str).str.upper()
    cond5 = s_str.str.contains(pattern_5, regex=True, case=False)
    cond4 = s_str.str.contains(pattern_4, regex=True, case=False)
    return np.select([cond5, cond4], [5, 4], default=2)

def percentile_score(series):
    return series.rank(method='average', pct=True) * 100

def get_priority_table(data):
    df = data.dropna(subset=['표준설비', '총작업시간(분)_E']).copy()
    for col in ['표준설비', '설비분류LV1', '작업상태', '법정관리']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    df['총작업시간(분)_E'] = pd.to_numeric(df['총작업시간(분)_E'], errors='coerce')
    df = df.dropna(subset=['총작업시간(분)_E'])
    r = df.groupby(['설비분류LV1', '표준설비'], observed=True).agg(
        작업건수=('표준설비', 'size'), 총작업시간_분_E=('총작업시간(분)_E', 'sum'),
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
    r['안전영향도'] = vector_score(r['표준설비'], SAFETY_5_REGEX, SAFETY_4_REGEX)
    r['운영중단영향도'] = vector_score(r['표준설비'], OPERATION_5_REGEX, OPERATION_4_REGEX)
    r['법정·규제영향도'] = np.select(
        [r['법정관리표시율'].ge(.8), r['법정관리표시율'].ge(.5), r['법정관리표시율'].gt(0)],
        [5, 4, 3], # 조건이 3개이므로, 선택 목록에도 [5, 4, 3] 세 개의 값을 전달합니다.
        default=2
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
    if len(priority) <= top_n:
        selected = priority.copy()
        selected['_selected_reason'] = '전체평가순위 TOP50'
        selected['보정후순위'] = np.arange(1, len(selected) + 1)
        return selected
    selected_indices = list(range(top_n))
    selected_reasons = {i: '전체평가순위 TOP50' for i in range(top_n)}
    class_series = priority[class_col]
    for class_name in class_series.dropna().unique():
        current_in_top = [idx for idx in selected_indices if class_series.iloc[idx] == class_name]
        if len(current_in_top) >= minimum: continue

        need = minimum - len(current_in_top)
        candidate_indices = [idx for idx in range(top_n, len(priority)) if class_series.iloc[idx] == class_name][:need]

        for cand_idx in candidate_indices:
            current_counts = class_series.iloc[selected_indices].value_counts()
            removable_candidates = [idx for idx in reversed(selected_indices) if current_counts.get(class_series.iloc[idx], 0) > minimum]

            if not removable_candidates:
                print('최소 분류 수를 보장하면서 정확한 TOP50을 만들 수 없습니다.')
                break

            remove_idx = removable_candidates[0]

            selected_indices.remove(remove_idx)
            selected_indices.append(cand_idx)
            selected_reasons[cand_idx] = f'{class_name} 최소 {minimum}개 보정'

    selected_indices.sort()
    selected = priority.iloc[selected_indices].copy()
    selected['_selected_reason'] = [selected_reasons[i] for i in selected_indices]
    selected['보정후순위'] = np.arange(1, len(selected) + 1)
    return selected

# --- 백그라운드 스레드에서 실행될 메인 분석 함수 ---
def run_full_analysis(folder_path_str, data_queue):
    try:
        folder_path = Path(folder_path_str)
        data_queue.put(("log", f"분석 시작: {folder_path}"))
        data_queue.put(("progress", 5))

        excel_files = [f for f in folder_path.iterdir() if f.suffix.lower() in [".xlsx", ".xls"] and not f.name.startswith("~$")]
        if not excel_files:
            data_queue.put(("error", "선택한 폴더에 유효한 Excel 파일이 없습니다."))
            return

        dataframes = []
        total_files = len(excel_files)
        for i, file_path in enumerate(excel_files):
            data_queue.put(("log", f"파일 읽는 중 ({i+1}/{total_files}): {file_path.name}"))
            try:
                sheets = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, df in sheets.items():
                    if df.empty: continue
                    df.columns = df.columns.astype(str).str.replace(r"\s+", "", regex=True)
                    if "표준설비" not in df.columns:
                        data_queue.put(("error", f"오류: {file_path.name}에 '표준설비' 열 없음"))
                        return
                    df["원본파일명"] = file_path.name
                    df["시트명"] = str(sheet_name)
                    dataframes.append(df)
            except Exception as e:
                data_queue.put(("error", f"파일 읽기 실패: {file_path.name} | {e}"))
                return
            data_queue.put(("progress", 5 + int(45 * (i + 1) / total_files)))

        if not dataframes:
            data_queue.put(("error", "통합할 유효 데이터가 없습니다."))
            return

        data_queue.put(("log", "데이터 통합 및 전처리 중..."))
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = combined_df[(combined_df['서비스LV1'] == '시설') & (combined_df['총작업시간(분)'].notna())].copy()
        work_time = pd.to_numeric(combined_df['작업시간(분)'], errors='coerce').fillna(0)
        total_time = pd.to_numeric(combined_df['총작업시간(분)'], errors='coerce').fillna(0)
        step1_calc = np.select(
            [work_time <= 480, (work_time > 480) & (work_time <= 1440), work_time > 1440],
            [work_time, 480, work_time - ((work_time // 1440) * 960)], default=0
        )
        multiplier = np.where(work_time > 0, total_time // work_time, 0)
        combined_df['총작업시간(분)_E'] = multiplier * step1_calc
        data_queue.put(("progress", 50))

        # --- 분석 1: 우선순위 평가 ---
        data_queue.put(("log", "분석 1: 우선순위 평가 수행 중..."))
        priority = get_priority_table(combined_df)
        top50 = select_top50_with_minimum_by_class(priority, top_n=50, minimum=2)
        group_summary = top50.groupby('설비분류LV1', dropna=False, observed=True).agg(
            포함설비수=('표준설비', 'nunique'), 작업건수=('작업건수', 'sum'),
            총작업시간_분_E=('총작업시간_분_E', 'sum'), 평균종합점수=('종합우선순위점수', 'mean'),
        ).reset_index().sort_values('평균종합점수', ascending=False)
        data_queue.put(("result", ("TOP 50", top50)))
        data_queue.put(("result", ("분류별 요약", group_summary)))
        data_queue.put(("progress", 70))

        # --- 시각화 1 ---
        plot_df = group_summary.sort_values(by="포함설비수", ascending=False).copy()
        plot_df["평균종합점수_라벨"] = plot_df["평균종합점수"].map(lambda x: f"{x:.2f}")
        fig1 = px.bar(plot_df, x="포함설비수", y="설비분류LV1", orientation="h", text="포함설비수", color="평균종합점수_라벨", title="표준설비 TOP50 - 설비분류별")
        data_queue.put(("plot", ("분류별 TOP 50", fig1)))

        # --- 시각화 2 ---
        plot2_sorted = top50.head(50).assign(설비중요도점수=lambda x: x["설비중요도점수"].astype(float)).sort_values("보정후순위", ascending=False)
        fig2 = px.bar(plot2_sorted, x="종합우선순위점수", y="표준설비", orientation="h", color="설비중요도점수", text="종합우선순위점수", color_continuous_scale="Blues", title="표준설비 TOP50")
        fig2.update_layout(height=700)
        data_queue.put(("plot", ("표준설비 TOP 50", fig2)))
        data_queue.put(("progress", 90))

        # --- 파일 저장 (선택적) ---
        data_queue.put(("log", "결과 파일 저장 중..."))
        priority.to_csv(folder_path / '전체표준설비_평가순위.csv', index=False, encoding='utf-8-sig')
        top50.to_csv(folder_path / '표준설비_TOP50_분류보정.csv', index=False, encoding='utf-8-sig')
        data_queue.put(("log", "CSV 파일 저장 완료."))

        data_queue.put(("progress", 100))
        data_queue.put(("done", "모든 분석이 성공적으로 완료되었습니다."))

    except Exception as e:
        data_queue.put(("error", f"분석 중 심각한 오류 발생: {e}"))

# --- Tkinter 애플리케이션 클래스 ---
class AnalysisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("운영센터 작업관리 분석")
        self.geometry("1200x800")

        self.data_queue = queue.Queue()
        self.plot_frames = {}
        self.tree_views = {}

        self.create_widgets()
        self.process_queue()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = ttk.LabelFrame(main_frame, text="작업 컨트롤", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        self.folder_path_var = tk.StringVar(value="분석할 폴더를 선택하세요.")
        ttk.Label(control_frame, textvariable=self.folder_path_var, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(control_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        self.start_button = ttk.Button(control_frame, text="분석 시작", command=self.start_analysis, state=tk.DISABLED)
        self.start_button.pack(side=tk.LEFT, padx=5)

        status_frame = ttk.LabelFrame(main_frame, text="진행 상태", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, expand=True, pady=(0, 5))
        self.log_widget = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=8, state=tk.DISABLED)
        self.log_widget.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)
            self.start_button.config(state=tk.NORMAL)
            self.log_message(f"폴더 선택됨: {folder_selected}")

    def start_analysis(self):
        folder_path = self.folder_path_var.get()
        if not Path(folder_path).is_dir():
            self.log_message("오류: 유효한 폴더가 아닙니다.", "error")
            return

        self.start_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.log_widget.config(state=tk.NORMAL); self.log_widget.delete(1.0, tk.END); self.log_widget.config(state=tk.DISABLED)

        # 기존 탭 제거
        for i in reversed(range(self.notebook.index('end'))):
            self.notebook.forget(i)
        self.plot_frames.clear()
        self.tree_views.clear()

        self.log_message(f"분석을 시작합니다...")
        threading.Thread(target=run_full_analysis, args=(folder_path, self.data_queue), daemon=True).start()

    def process_queue(self):
        try:
            while True:
                msg_type, data = self.data_queue.get_nowait()
                if msg_type == "log": self.log_message(data)
                elif msg_type == "progress": self.progress_bar['value'] = data
                elif msg_type == "result": self.display_result_table(*data)
                elif msg_type == "plot": self.display_plot(*data)
                elif msg_type == "done":
                    self.log_message(data, "success")
                    self.start_button.config(state=tk.NORMAL)
                elif msg_type == "error":
                    self.log_message(data, "error")
                    self.start_button.config(state=tk.NORMAL)
        except queue.Empty:
            self.after(100, self.process_queue)

    def log_message(self, message, level="info"):
        self.log_widget.config(state=tk.NORMAL)
        self.log_widget.insert(tk.END, f"[{level.upper()}] {message}\n")
        self.log_widget.see(tk.END)
        self.log_widget.config(state=tk.DISABLED)

    def display_result_table(self, title, df):
        if title in self.tree_views:
            frame = self.tree_views[title].master
        else:
            frame = ttk.Frame(self.notebook, padding="5")
            self.notebook.add(frame, text=title)
            tree = ttk.Treeview(frame, show="headings")
            vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            vsb.pack(side='right', fill='y')
            hsb.pack(side='bottom', fill='x')
            tree.pack(fill='both', expand=True)
            self.tree_views[title] = tree

        tree = self.tree_views[title]
        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        for index, row in df.iterrows():
            tree.insert("", "end", values=[str(v) for v in row])
        self.log_message(f"결과 테이블 '{title}' 표시 완료.")

    def display_plot(self, title, fig):
        if title in self.plot_frames:
            frame = self.plot_frames[title]
            for widget in frame.winfo_children():
                widget.destroy()
        else:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=title)
            self.plot_frames[title] = frame

        html_content = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
        webview.create_window(title, html=html_content, parent=frame.winfo_id())
        self.log_message(f"인터랙티브 그래프 '{title}' 표시 완료.")

if __name__ == "__main__":
    app = AnalysisApp()
    app.mainloop()
