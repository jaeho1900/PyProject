import os
import pandas as pd
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# ---------------------------------------------------------
# 0. 경로 설정
# ---------------------------------------------------------
BASE_DIR = r"C:\Users\Administrator\Desktop"
EXCEL_PATH = os.path.join(BASE_DIR, "설비관리.xlsx")
DOCX_TEMP_PATH = os.path.join(BASE_DIR, "temp.docx")
DOCX_OUTPUT_PATH = os.path.join(BASE_DIR, "설비관리.docx")


# ---------------------------------------------------------
# 1. 엑셀 데이터 로드 및 정렬 (데이터 많은 순)
# ---------------------------------------------------------
df = pd.read_excel(EXCEL_PATH)

# 데이터 개수가 많은 순서대로 내림차순 정렬 규칙 적용
df['LV1_count'] = df.groupby('설비LV1')['설비LV1'].transform('count')
df['LV2_count'] = df.groupby(['설비LV1', '표준설비'])['표준설비'].transform('count')

df_sorted = df.sort_values(
    by=['LV1_count', '설비LV1', 'LV2_count', '표준설비'],
    ascending=[False, True, False, True]
).reset_index(drop=True)

data_rows = df_sorted[['설비LV1', '표준설비', '서비스LV2', '작업명', '주기']].values.tolist()


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
        for table in doc.tables:
            if table._element.getparent() == doc._body._element:
                # 위치상 헤더 단락 다음에 위치한 표를 타겟팅
                target_table = table
                break
        break

# 만약 단락 위치 기반 탐색이 불가능한 경우 문서 내 첫 번째 표 사용
if target_table is None and len(doc.tables) > 0:
    target_table = doc.tables[0]

if target_table is None:
    raise ValueError("문서에서 대상 표를 찾을 수 없습니다.")


# ---------------------------------------------------------
# 4. 기존 표의 양식을 유지하며 2번째 행(Index 1)부터 내용 채우기
# ---------------------------------------------------------
# 기존 표에 필요 데이터 수만큼 행 확장
current_rows = len(target_table.rows)
needed_rows = len(data_rows) + 1  # 헤더(1행) + 데이터 행 수

# 부족한 행만큼 기존 표의 하단에 새 행 추가
while len(target_table.rows) < needed_rows:
    target_table.add_row()

# 데이터 채우기 (2번째 행인 Index 1부터 작성)
for idx, row_data in enumerate(data_rows, start=1):
    row_cells = target_table.rows[idx].cells

    format_cell(row_cells[0], row_data[0])  # 설비LV1
    format_cell(row_cells[1], row_data[1])  # 표준설비
    format_cell(row_cells[2], row_data[2])  # 서비스LV2
    format_cell(row_cells[3], row_data[3], align=WD_ALIGN_PARAGRAPH.LEFT)  # 작업명 (좌측 정렬)
    format_cell(row_cells[4], row_data[4])  # 주기


# ---------------------------------------------------------
# 5. 동일 값 수직 셀 병합 및 텍스트 하나만 유지 처리
# ---------------------------------------------------------
# 1열 (설비LV1) 병합 처리
start_r = 1
total_data_len = len(data_rows)

for r in range(2, total_data_len + 1):
    if target_table.cell(r, 0).text.strip() != target_table.cell(start_r, 0).text.strip():
        if r - 1 > start_r:
            safe_merge_and_clean(target_table, 0, start_r, r - 1)
        start_r = r
if total_data_len > start_r:
    safe_merge_and_clean(target_table, 0, start_r, total_data_len)

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
