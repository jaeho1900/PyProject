# -*- coding: utf-8 -*-
"""
운영센터 '작업관리' 분석 및 시각화 - Streamlit GUI 버전

기존 분석 스크립트를 Streamlit을 사용하여 대화형 웹 애플리케이션으로 변환합니다.
- 웹 기반 파일 업로드, 동적 파라미터 설정
- 인터랙티브 Plotly 차트 렌더링 및 결과 데이터 다운로드 기능
- st.cache_data를 이용한 성능 최적화
- st.session_state를 이용한 설정 관리 및 유지
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re
import json
import os

# --- 웹페이지 기본 설정 ---
st.set_page_config(
    page_title="운영센터 작업관리 분석 대시보드",
    page_icon="📊",
    layout="wide",
)

# --- 설정 관리 ---
CONFIG_FILE = "config.json"

def load_settings():
    """설정 파일을 로드합니다. 파일이 없으면 기본값을 반환합니다."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    # 기본값
    return {
        "VALID_STATUSES": ['작업완료', '지연완료'],
        "SAFETY_5": ['소화', '감지', '발신기', '수신기', '방화', '피난', '가스', '누수', '차단기', '변압기', '발전기', 'UPS', '배터리', '비상'],
        "SAFETY_4": ['전기', '분전반', 'MCC', '모터컨트롤', '냉동기', '보일러', '냉각탑', '공기조화기', '승강기', '엘리베이터', '펌프'],
        "OPERATION_5": ['MAIN', '차단기', '변압기', '발전기', 'UPS', '배터리', '수신기', '소화펌프', '냉동기', '냉각탑', '공기조화기', '보일러'],
        "OPERATION_4": ['SUB', '분전반', 'MCC', '모터컨트롤', '방화', '소화', '감지', '발신기', '가스']
    }

# st.session_state에 설정이 없으면 초기화
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

# --- 데이터 분석 함수 (설정을 인자로 받도록 수정) ---
@st.cache_data
def load_and_preprocess_data(uploaded_files):
    # (이하 원본과 동일, 생략)
    pass

def vector_score(series, pattern_5, pattern_4):
    # (이하 원본과 동일, 생략)
    pass

def get_priority_table(data, settings):
    """분석 함수가 st.session_state의 설정을 사용하도록 수정"""
    # 설정에서 키워드 목록과 정규식 패턴 가져오기
    VALID_STATUSES = settings['VALID_STATUSES']
    SAFETY_5_REGEX = '|'.join(map(re.escape, settings['SAFETY_5']))
    SAFETY_4_REGEX = '|'.join(map(re.escape, settings['SAFETY_4']))
    OPERATION_5_REGEX = '|'.join(map(re.escape, settings['OPERATION_5']))
    OPERATION_4_REGEX = '|'.join(map(re.escape, settings['OPERATION_4']))

    # ... (원본 get_priority_table 로직) ...
    # r['안전영향도'] = vector_score(...) 부분에서 위의 정규식 변수 사용
    # ... (나머지 로직은 원본과 거의 동일) ...
    # 이 부분은 설명을 위해 개념적으로 축약, 실제 구현 시 원본 코드의 해당 변수들을 settings에서 가져오도록 수정해야 함
    pass

# (select_top_with_minimum_by_class, create_download_button 등 나머지 함수는 원본과 동일)

# --- Streamlit UI 구성 ---
st.title("📊 운영센터 작업관리 분석 대시보드")
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 분석 설정")
    st.info("분석에 사용될 키워드 목록은 'Settings' 페이지에서 수정할 수 있습니다.")
    uploaded_files = st.file_uploader(
        "분석할 작업관리 엑셀 파일을 업로드하세요.",
        type=["xlsx", "xls"],
        accept_multiple_files=True
    )
    top_n = st.number_input("TOP N 순위", min_value=5, max_value=200, value=50, step=10)
    minimum = st.number_input("분류별 최소 보정 개수", min_value=1, max_value=10, value=2, step=1)

    run_button = st.button("🚀 분석 실행")

# 메인 로직
if run_button and uploaded_files:
    with st.spinner('파일을 읽고 데이터를 전처리하는 중입니다...'):
        combined_df = load_and_preprocess_data(uploaded_files)

    if combined_df is not None and not combined_df.empty:
        st.success(f"✅ 파일 로딩 및 전처리 완료! 총 {len(combined_df):,}건의 데이터가 처리되었습니다.")

        with st.spinner('데이터 분석 및 시각화를 진행 중입니다...'):
            # 분석 함수에 현재 설정(st.session_state.settings) 전달
            priority_df = get_priority_table(combined_df, st.session_state.settings)
            # ... (이하 분석 및 시각화 로직) ...
            pass
# ... (이하 UI 로직) ...
