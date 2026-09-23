import os
import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# ---------------------------------------------------------
# 0. 경로 설정
# ---------------------------------------------------------
# 현재 사용자의 바탕화면 경로 자동 탐색 (필요 시 직접 경로 지정 가능)
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
EXCEL_PATH = os.path.join(BASE_DIR, "설비관리.xlsx")
DOCX_TEMP_PATH = os.path.join(BASE_DIR, "temp.docx")
DOCX_OUTPUT_PATH = os.path.join(BASE_DIR, "설비관리.docx")


# ---------------------------------------------------------
# 1. 엑셀 데이터 로드 및 정렬 (데이터 많은 순)
# ---------------------------------------------------------
df = pd.read_excel(EXCEL_PATH)

# 결측치(NaN) 기본 공백 처리
target_cols = ['설비LV1', '표준설비', '서비스LV2', '작업명', '주기']
for col in target_cols:
    if col not in df.columns:
        df[col] = ""
    else:
        df[col] = df[col].fillna("")

# 데이터 개수가 많은 순서대로 내림차순 정렬 규칙 적용
df['LV1_count'] = df.groupby('설비LV1')['설비LV1'].transform('count')
df['LV2_count'] = df.groupby(['설비LV1', '표준설비'])['표준설비'].transform('count')

df_sorted = df.sort_values(
    by=['LV1_count', '설비LV1', 'LV2_count', '표준설비'],
    ascending=[False, True, False, True]
).reset_index(drop=True)

data_rows = df_sorted[['설비LV1', '표준설비', '서비스LV2', '작업명', '주기']].values.tolist()
data_rows = df_sorted[target_cols].values.tolist()


# ---------------------------------------------------------
# 2. 서식 및 병합 관련 함수
# ---------------------------------------------------------
def format_cell(cell, text, bold=False, font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER):
    """셀 텍스트 입력 및 정렬, 폰트 서식 설정 (기존 테두리/배경 양식 유지)"""
    cell.text = str(text) if text is not None else ""
    p = cell.paragraphs[0]
    p.alignment = align
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    for run in p.runs:
        run.font.name = '맑은 고딕'
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = RGBColor(0, 0, 0)


def safe_merge_and_clean(table, col_idx, start_row, end_row):
    """
    지정한 열의 start_row부터 end_row까지 병합하고,
    병합된 셀의 내용이 중복되지 않고 '하나의 값만' 깔끔하게 유지되도록 처리합니다.
    """
    first_cell_text = table.cell(start_row, col_idx).text.strip()
    target_cell = table.cell(start_row, col_idx)

    for r in range(start_row + 1, end_row + 1):
        target_cell.merge(table.cell(r, col_idx))

    # 병합 후 중복 합성된 텍스트를 최초 단일 텍스트로 복원 및 정렬
    format_cell(target_cell, first_cell_text, bold=False, font_size=9, align=WD_ALIGN_PARAGRAPH.CENTER)


def get_merge_ranges(data, key_func):
    """
    원본 데이터 기준으로 연속된 동일 키 값을 가진 구간 [(start_row, end_row), ...] 계산
    (헤더가 1행이므로 데이터 index에 +1을 더해 표의 행 index로 반환)
    """
    ranges = []
    if not data:
        return ranges

    start = 0
    for i in range(1, len(data)):
        if key_func(data[i]) != key_func(data[start]):
            if (i - 1) > start:
                ranges.append((start + 1, (i - 1) + 1))
            start = i
    if (len(data) - 1) > start:
        ranges.append((start + 1, (len(data) - 1) + 1))
    return ranges


# ---------------------------------------------------------
# 3. Word 문서 불러오기 및 기존 표 탐색
# ---------------------------------------------------------
doc = Document(DOCX_TEMP_PATH)

target_heading = "1.1) 주요 설비 관리 업무"
target_table = None

# '1.1) 주요 설비 관리 업무' 단락 바로 다음에 위치한 표 찾기
for i, p in enumerate(doc.paragraphs):
    if target_heading in p.text:
        # 해당 단락 이후의 첫 번째 표 탐색
# '1.1) 주요 설비 관리 업무' 단락 바로 다음에 위치한 표 찾기 (XML 본문 순서 탐색)
found_heading = False
for child in doc._body._element:
    if child.tag.endswith('p'):
        text = "".join(child.itertext())
        if target_heading in text:
            found_heading = True
    elif child.tag.endswith('tbl') and found_heading:
        for table in doc.tables:
            if table._element.getparent() == doc._body._element:
                # 위치상 헤더 단락 다음에 위치한 표를 타겟팅
            if table._element == child:
                target_table = table
                break
        break
        if target_table:
            break

# 만약 단락 위치 기반 탐색이 불가능한 경우 문서 내 첫 번째 표 사용
# 위치 기반 탐색이 불가능한 경우 문서 내 첫 번째 표 fallback
if target_table is None and len(doc.tables) > 0:
    target_table = doc.tables[0]

if target_table is None:
    raise ValueError("문서에서 대상 표를 찾을 수 없습니다.")


# ---------------------------------------------------------
# 4. 기존 표의 양식을 유지하며 2번째 행(Index 1)부터 내용 채우기
# 4. 기존 표의 행 수 조정 및 데이터 채우기 (2번째 행부터)
# ---------------------------------------------------------
# 기존 표에 필요 데이터 수만큼 행 확장
current_rows = len(target_table.rows)
needed_rows = len(data_rows) + 1  # 헤더(1행) + 데이터 행 수

# 부족한 행만큼 기존 표의 하단에 새 행 추가
# 1) 부족한 행 추가
while len(target_table.rows) < needed_rows:
    target_table.add_row()

# 데이터 채우기 (2번째 행인 Index 1부터 작성)
# 2) 기존 템플릿 표의 불필요한 초과 행 삭제
while len(target_table.rows) > needed_rows:
    tr = target_table.rows[-1]._tr
    target_table._tbl.remove(tr)

# 3) 데이터 채우기 (헤더 다음인 1번 인덱스부터 작성)
for idx, row_data in enumerate(data_rows, start=1):
    row_cells = target_table.rows[idx].cells

    format_cell(row_cells[0], row_data[0])  # 설비LV1
    format_cell(row_cells[1], row_data[1])  # 표준설비
    format_cell(row_cells[2], row_data[2])  # 서비스LV2
    format_cell(row_cells[3], row_data[3], align=WD_ALIGN_PARAGRAPH.LEFT)  # 작업명 (좌측 정렬)
    format_cell(row_cells[4], row_data[4])  # 주기


# ---------------------------------------------------------
# 5. 동일 값 수직 셀 병합 및 텍스트 하나만 유지 처리
# 5. 동일 값 수직 셀 병합 (원본 데이터 기반으로 안전하게 처리)
# ---------------------------------------------------------
# 1열 (설비LV1) 병합 처리
start_r = 1
total_data_len = len(data_rows)
# 1열 (설비LV1) 병합 구간 계산 및 병합
lv1_merge_ranges = get_merge_ranges(data_rows, key_func=lambda x: str(x[0]).strip())
for start_r, end_r in lv1_merge_ranges:
    safe_merge_and_clean(target_table, 0, start_r, end_r)

for r in range(2, total_data_len + 1):
    if target_table.cell(r, 0).text.strip() != target_table.cell(start_r, 0).text.strip():
        if r - 1 > start_r:
            safe_merge_and_clean(target_table, 0, start_r, r - 1)
        start_r = r
if total_data_len > start_r:
    safe_merge_and_clean(target_table, 0, start_r, total_data_len)
# 2열 (표준설비) 병합 구간 계산 및 병합 (설비LV1과 표준설비가 모두 일치할 때 병합)
lv2_merge_ranges = get_merge_ranges(data_rows, key_func=lambda x: (str(x[0]).strip(), str(x[1]).strip()))
for start_r, end_r in lv2_merge_ranges:
    safe_merge_and_clean(target_table, 1, start_r, end_r)

# 2열 (표준설비) 병합 처리 (1열과 2열이 모두 동일할 때 병합)
start_r = 1
for r in range(2, total_data_len + 1):
    curr_lv1 = target_table.cell(r, 0).text.strip()
    prev_lv1 = target_table.cell(start_r, 0).text.strip()
    curr_lv2 = target_table.cell(r, 1).text.strip()
    prev_lv2 = target_table.cell(start_r, 1).text.strip()

    if (curr_lv2 != prev_lv2) or (curr_lv1 != prev_lv1):
        if r - 1 > start_r:
            safe_merge_and_clean(target_table, 1, start_r, r - 1)
        start_r = r
if total_data_len > start_r:
    safe_merge_and_clean(target_table, 1, start_r, total_data_len)


# ---------------------------------------------------------
# 6. 최종 파일 저장
# ---------------------------------------------------------
doc.save(DOCX_OUTPUT_PATH)
print(f"작업이 완료되었습니다. 결과 파일: {DOCX_OUTPUT_PATH}")
