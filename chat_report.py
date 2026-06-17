import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# ==========================================
# 1. 초기화 및 기본 프레임 설정 (16:9 와이드)
# ==========================================
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

blank_slide_layout = prs.slide_layouts[6]

# 디자인 상수 정의 (LG 톤앤매너 및 지침 반영)
COLOR_BG = RGBColor(0xF5, 0xF1, 0xEB)       # 베이지 배경
COLOR_PRIMARY = RGBColor(0xA5, 0x00, 0x34)  # LG 딥 버건디
COLOR_PREMIUM = RGBColor(0x7A, 0x00, 0x24)  # 프리미엄 버건디
COLOR_LITE = RGBColor(0xC7, 0x70, 0x85)     # 라이트 버건디
COLOR_DARK = RGBColor(0x1A, 0x1A, 0x1A)     # 메인 텍스트
COLOR_MUTED = RGBColor(0x66, 0x66, 0x66)    # 서브 텍스트
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)    # 흰색 요소
COLOR_BORDER = RGBColor(0xD6, 0xC9, 0xB8)   # 테두리 브라운 그레이

# [지침 1] 서체 설정 수정 ('LG Smart' 일괄 적용)
FONT_NAME = "LG Smart"

def set_shape_transparent_border(shape):
    """도형 테두리 투명화 헬퍼 함수"""
    shape.line.fill.background()

def add_common_background(slide, section_num, section_title, page_num_str):
    """[지침 2] 좌우 1인치 여백을 반영한 공통 헤더/푸터 생성 함수"""
    # 1. 전체 배경색
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    set_shape_transparent_border(bg)

    # 2. 헤더 영역 (좌측 1.0인치 여백 적용)
    header_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.5), Inches(9.5), Inches(0.8))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_tag = tf.paragraphs[0]
    p_tag.text = section_num
    p_tag.font.name = FONT_NAME
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = COLOR_PRIMARY
    p_tag.space_after = Pt(2)

    p_title = tf.add_paragraph()
    p_title.text = section_title
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(18)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_DARK

    # 우측 상단 미니 로고 (우측 1.0인치 여백 안쪽 배치 : 13.333 - 1.0 - 2.0 = 10.333)
    logo_box = slide.shapes.add_textbox(Inches(10.333), Inches(0.5), Inches(2.0), Inches(0.5))
    ltf = logo_box.text_frame
    ltf.word_wrap = True
    p_logo = ltf.paragraphs[0]
    p_logo.alignment = PP_ALIGN.RIGHT
    p_logo.text = "LG PLANNING OFFICE"
    p_logo.font.name = FONT_NAME
    p_logo.font.size = Pt(9)
    p_logo.font.bold = True
    p_logo.font.color.rgb = COLOR_DARK

    # 헤더 장식선
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.3), Inches(11.333), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_PRIMARY
    set_shape_transparent_border(line)

    # 3. 푸터 영역 (좌우 1.0인치 타겟팅 배치)
    footer_box = slide.shapes.add_textbox(Inches(1.0), Inches(7.0), Inches(11.333), Inches(0.3))
    ftf = footer_box.text_frame
    ftf.word_wrap = True
    ftf.margin_left = ftf.margin_top = ftf.margin_right = ftf.margin_bottom = 0
    p_foot = ftf.paragraphs[0]
    p_foot.text = f"LG 기획실 · 사업추진 전략 보고서                                                                                                         PAGE {page_num_str}"
    p_foot.font.name = FONT_NAME
    p_foot.font.size = Pt(8.5)
    p_foot.font.color.rgb = COLOR_MUTED

def add_key_message(slide, text, current_top):
    """[지침 2] 상자 간 세로 좌표가 겹치지 않도록 Top 값을 기준으로 순차 배치"""
    # Key Message 컨테이너 (좌우 1인치 여백 준수)
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), current_top, Inches(11.333), Inches(0.6))
    box.fill.solid()
    box.fill.fore_color.rgb = COLOR_WHITE
    box.line.color.rgb = COLOR_BORDER
    box.line.width = Pt(0.5)

    edge = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), current_top, Inches(0.08), Inches(0.6))
    edge.fill.solid()
    edge.fill.fore_color.rgb = COLOR_PRIMARY
    set_shape_transparent_border(edge)

    tb = slide.shapes.add_textbox(Inches(1.2), current_top + Inches(0.05), Inches(11.0), Inches(0.5))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]

    run_label = p.add_run()
    run_label.text = "KEY MESSAGE  "
    run_label.font.name = FONT_NAME
    run_label.font.size = Pt(10)
    run_label.font.bold = True
    run_label.font.color.rgb = COLOR_PRIMARY

    run_main = p.add_run()
    run_main.text = text
    run_main.font.name = FONT_NAME
    run_main.font.size = Pt(10)
    run_main.font.color.rgb = COLOR_DARK

    return current_top + Inches(0.6) + Inches(0.3)  # 높이 및 마진 합산 후 다음 탑 좌표 반환

# ==========================================
# 2. PAGE 1: 표지 슬라이드 (COVER)
# ==========================================
slide1 = prs.slides.add_slide(blank_slide_layout)

cover_bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
cover_bg.fill.solid()
cover_bg.fill.fore_color.rgb = COLOR_BG
set_shape_transparent_border(cover_bg)

# 메타 정보 (좌측 1.0인치 여백 확보)
meta_box = slide1.shapes.add_textbox(Inches(1.0), Inches(0.6), Inches(11.333), Inches(0.5))
mtf = meta_box.text_frame
mtf.word_wrap = True
p_meta = mtf.paragraphs[0]
p_meta.text = "2026 | KOR · CONFIDENTIAL                                                                            "
p_meta.font.name = FONT_NAME
p_meta.font.size = Pt(11)
p_meta.font.color.rgb = COLOR_MUTED

run_logo_mark = p_meta.add_run()
run_logo_mark.text = "LG "
run_logo_mark.font.name = FONT_NAME
run_logo_mark.font.bold = True
run_logo_mark.font.color.rgb = COLOR_PRIMARY

run_logo_txt = p_meta.add_run()
run_logo_txt.text = "Life's Good"
run_logo_txt.font.name = FONT_NAME
run_logo_txt.font.color.rgb = COLOR_DARK

cover_line1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.1), Inches(11.333), Inches(0.03))
cover_line1.fill.solid()
cover_line1.fill.fore_color.rgb = COLOR_PRIMARY
set_shape_transparent_border(cover_line1)

# 중앙 타이틀 영역 (Top 상호 간섭 없음)
title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(2.4), Inches(10.933), Inches(2.8))
ttf = title_box.text_frame
ttf.word_wrap = True

p_eyebrow = ttf.paragraphs[0]
p_eyebrow.text = "PLANNING OFFICE REPORT"
p_eyebrow.font.name = FONT_NAME
p_eyebrow.font.size = Pt(12)
p_eyebrow.font.bold = True
p_eyebrow.font.color.rgb = COLOR_PRIMARY
p_eyebrow.space_after = Pt(14)

p_main_title = ttf.add_paragraph()
p_main_title.text = "사업추진 전략 보고서"
p_main_title.font.name = FONT_NAME
p_main_title.font.size = Pt(44)
p_main_title.font.bold = True
p_main_title.font.color.rgb = COLOR_DARK
p_main_title.space_after = Pt(14)

# 서브타이틀 바 및 박스 (Top 간섭 없이 안전 배치)
sub_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(4.5), Inches(0.08), Inches(0.7))
sub_bar.fill.solid()
sub_bar.fill.fore_color.rgb = COLOR_PRIMARY
set_shape_transparent_border(sub_bar)

sub_box = slide1.shapes.add_textbox(Inches(1.4), Inches(4.45), Inches(10.5), Inches(0.8))
stf = sub_box.text_frame
stf.word_wrap = True
p_sub1 = stf.paragraphs[0]
p_sub1.text = "상품 카테고리별 차별화를 통한 수익성 제고 방안"
p_sub1.font.name = FONT_NAME
p_sub1.font.size = Pt(16)
p_sub1.font.bold = True
p_sub1.font.color.rgb = COLOR_DARK

p_sub2 = stf.add_paragraph()
p_sub2.text = "Premium · Standard · Lite 3-Tier 맞춤형 운영모델 구축"
p_sub2.font.name = FONT_NAME
p_sub2.font.size = Pt(13)
p_sub2.font.color.rgb = COLOR_MUTED

cover_line2 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(6.1), Inches(11.333), Inches(0.01))
cover_line2.fill.solid()
cover_line2.fill.fore_color.rgb = COLOR_BORDER
set_shape_transparent_border(cover_line2)

bottom_box = slide1.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.333), Inches(0.8))
btf = bottom_box.text_frame
btf.word_wrap = True
p_bottom = btf.paragraphs[0]
p_bottom.text = "PREPARED BY\n"
p_bottom.font.name = FONT_NAME
p_bottom.font.size = Pt(9)
p_bottom.font.color.rgb = COLOR_MUTED

run_org = p_bottom.add_run()
run_org.text = "LG 기획실 (Planning Office)                                                                                                         "
run_org.font.name = FONT_NAME
run_org.font.size = Pt(12)
run_org.font.bold = True
run_org.font.color.rgb = COLOR_DARK

run_date = p_bottom.add_run()
run_date.text = "2026.06\n"
run_date.font.name = FONT_NAME
run_date.font.size = Pt(24)
run_date.font.bold = True
run_date.font.color.rgb = COLOR_PRIMARY

run_date_lbl = p_bottom.add_run()
run_date_lbl.text = "                                                                                                                                                                          Issue Date"
run_date_lbl.font.name = FONT_NAME
run_date_lbl.font.size = Pt(8)
run_date_lbl.font.color.rgb = COLOR_MUTED

# ==========================================
# 3. PAGE 2: SECTION I (사업 추진 배경 및 전략 방향)
# ==========================================
slide2 = prs.slides.add_slide(blank_slide_layout)
add_common_background(slide2, "SECTION I", "사업 추진 배경 및 전략 방향", "1 / 2")

# [지침 2] 순차 레이아웃 좌표 추적
current_top = Inches(1.5)
current_top = add_key_message(slide2, "고객 니즈의 양극화와 시장 경쟁 심화에 대응하기 위하여, 단일 서비스 모델에서 탈피한 Premium·Standard·Lite 3-tier 맞춤형 운영모델을 구축하여 티어별 차별화된 가치 제공을 통한 수익성 제고를 도모하고자 함.", current_top)

# 양대 칼럼 레이아웃 (좌측 1인치 여백 확보 및 너비 조절)
left_x = Inches(1.0)
content_width = Inches(5.4)
right_x = Inches(6.9)  # 1.0 + 5.4 + 0.5(간격) = 6.9 (우측 여백 1.033인치 확보 자동 계산)

# --- 좌측 텍스트 상자 배치 (여백 확보 및 자동 줄바꿈) ---
left_col_box = slide2.shapes.add_textbox(left_x, current_top, content_width, Inches(4.3))
ltf = left_col_box.text_frame
ltf.word_wrap = True
ltf.margin_left = ltf.margin_top = ltf.margin_right = ltf.margin_bottom = 0

# 1. 추진 배경
p = ltf.paragraphs[0]
p.text = "■ 1. 추진 배경"
p.font.name = FONT_NAME
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p.space_after = Pt(4)

bullets_bg = [
    "• 고객 니즈 양극화 심화: 기업형과 일반 소비자의 요구 격차 확대",
    "   - 고부가가치 수요: 지주사·LG전자·IDC 맞춤 운영 및 SLA 품질 보장 필요",
    "   - 볼륨 시장 경쟁 심화: 경쟁사 저가 공세로 인한 원가 압박 가속화",
    "• 운영 효율성 한계 도달: One-Size-Fits-All 모델 자원 왜곡 발생",
    "   - 수익 기여도가 높은 핵심 고객 대상 집중 투자 구조 부족",
    "   - 1군 핵심 고객의 이탈률 상승 추세 지속 (전년 대비 +2.3%p)"
]
for b in bullets_bg:
    p = ltf.add_paragraph()
    p.text = b
    p.font.name = FONT_NAME
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_DARK
    p.space_after = Pt(2)

p.space_after = Pt(12)

# 2. 전략 방향
p = ltf.add_paragraph()
p.text = "■ 2. 전략 방향"
p.font.name = FONT_NAME
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = COLOR_PRIMARY
p.space_after = Pt(4)

bullets_strat = [
    "• 3-Tier 차별화 체계 구축: 고객 가치 및 수익 기반 최적 자원 분배",
    "   - Premium(고수익·전문 영역), Standard(리텐션), Lite(인지도 확장)",
    "• MECE 기반 역량 배분: 인원·품질·솔루션 역량 진단 및 차등 투입"
]
for b in bullets_strat:
    p = ltf.add_paragraph()
    p.text = b
    p.font.name = FONT_NAME
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_DARK
    p.space_after = Pt(2)

# --- 우측 시각화 피라미드 상자 배치 (동일 세로 좌표층 형성) ---
right_bg = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, current_top, content_width, Inches(4.3))
right_bg.fill.solid()
right_bg.fill.fore_color.rgb = COLOR_WHITE
right_bg.line.color.rgb = COLOR_BORDER
right_bg.line.width = Pt(0.5)

# 피라미드 내부 타이틀
rt_box = slide2.shapes.add_textbox(right_x, current_top + Inches(0.15), content_width, Inches(0.4))
rt_tf = rt_box.text_frame
rt_tf.word_wrap = True
rt_p = rt_tf.paragraphs[0]
rt_p.alignment = PP_ALIGN.CENTER
rt_p.text = "상품 카테고리별 운영모델 차별화 구조"
rt_p.font.name = FONT_NAME
rt_p.font.size = Pt(11)
rt_p.font.bold = True
rt_p.font.color.rgb = COLOR_DARK

# 피라미드 구성 요소 레이어링
p_width_base = Inches(5.0)
p_center_x = right_x + (content_width / 2)

# Premium
p1 = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, p_center_x - Inches(1.5), current_top + Inches(0.7), Inches(3.0), Inches(0.8))
p1.fill.solid(); p1.fill.fore_color.rgb = COLOR_PREMIUM; set_shape_transparent_border(p1)
p1_tf = p1.text_frame; p1_tf.word_wrap = True
p1_p = p1_tf.paragraphs[0]; p1_p.alignment = PP_ALIGN.CENTER; p1_p.text = "PREMIUM (고수익·전문)\n지주사·LG전자·IDC 맞춤 운영"; p1_p.font.name = FONT_NAME; p1_p.font.size = Pt(9); p1_p.font.color.rgb = COLOR_WHITE; p1_p.font.bold = True

# Standard
p2 = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, p_center_x - Inches(2.0), current_top + Inches(1.6), Inches(4.0), Inches(0.8))
p2.fill.solid(); p2.fill.fore_color.rgb = COLOR_PRIMARY; set_shape_transparent_border(p2)
p2_tf = p2.text_frame; p2_tf.word_wrap = True
p2_p = p2_tf.paragraphs[0]; p2_p.alignment = PP_ALIGN.CENTER; p2_p.text = "STANDARD (수익·리텐션 강화)\n1군 볼륨 및 주력시장 기술기반 운영"; p2_p.font.name = FONT_NAME; p2_p.font.size = Pt(9); p2_p.font.color.rgb = COLOR_WHITE; p2_p.font.bold = True

# Lite
p3 = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, p_center_x - Inches(2.4), current_top + Inches(2.5), Inches(4.8), Inches(0.8))
p3.fill.solid(); p3.fill.fore_color.rgb = COLOR_LITE; set_shape_transparent_border(p3)
p3_tf = p3.text_frame; p3_tf.word_wrap = True
p3_p = p3_tf.paragraphs[0]; p3_p.alignment = PP_ALIGN.CENTER; p3_p.text = "LITE (위험관리·인지도 확장)\n2군 신규 볼륨 및 레드오션 시장수준 운영"; p3_p.font.name = FONT_NAME; p3_p.font.size = Pt(9); p3_p.font.color.rgb = COLOR_WHITE; p3_p.font.bold = True

# 설명 하단 글
caption_box = slide2.shapes.add_textbox(right_x, current_top + Inches(3.5), content_width, Inches(0.6))
ctf = caption_box.text_frame
ctf.word_wrap = True
cp = ctf.paragraphs[0]
cp.alignment = PP_ALIGN.CENTER
cp.text = "▲ 상위 티어일수록 높은 수익성·전문 역량 요구\n▼ 하위 티어일수록 시장 접근성·확장성 중시"
cp.font.name = FONT_NAME
cp.font.size = Pt(8.5)
cp.font.color.rgb = COLOR_MUTED

# ==========================================
# 4. PAGE 3: SECTION II (티어별 추진 전략 및 기대효과)
# ==========================================
slide3 = prs.slides.add_slide(blank_slide_layout)
add_common_background(slide3, "SECTION II", "티어별 추진 전략 및 기대효과", "2 / 2")

current_top_s3 = Inches(1.5)
current_top_s3 = add_key_message(slide3, "3-Tier 체계의 핵심은 차별화된 자원 배분과 운영모델 적용을 통하여 Premium은 고수익 창출, Standard는 리텐션 제고, Lite는 시장 확장을 동시 달성하는 것이며, 전사 수익성을 구조적으로 제고하고자 함.", current_top_s3)

# --- 상단부: 비교 분석 표 (Table 배치) ---
rows, cols = 4, 4
table_width = Inches(11.333) # 13.333 - 1.0(좌) - 1.0(우)
table_height = Inches(2.0)
table_shape = slide3.shapes.add_table(rows, cols, Inches(1.0), current_top_s3, table_width, table_height)
table = table_shape.table

# 테이블 내부 컬럼 폭 정교화 분배
table.columns[0].width = Inches(1.5)
table.columns[1].width = Inches(3.277)
table.columns[2].width = Inches(3.277)
table.columns[3].width = Inches(3.277)

headers = ["구분", "PREMIUM (프리미엄)", "STANDARD (스탠다드)", "LITE (라이트)"]
row_labels = ["제품 대상", "필요 역량", "F/U 과제"]
table_data = [
    ["지주사·LG전자·IDC\n(맞춤 운영)", "1군 볼륨 및 리텐션 대상\n(기술기반 운영)", "2군 신규 볼륨\n(시장수준 운영)"],
    ["버틀러 & 전문기술인 확보\n(인원 5 · 품질 5 · 솔루션 0)", "솔루션 & 프로세스 차별화\n(인원 4 · 품질 4 · 솔루션 4)", "서비스 & 품질관리 이원화\n(인원 1 · 품질 2 · 솔루션 3)"],
    ["• IDC 사업화 전략 수립\n• IDC 표준운영프로세스 수립", "• 솔루션 R&D / 현장 Pilot\n• 품질/개량체계 / 리텐션 적용", "• 서비스 유형화 / 가격 기준 수립\n• 품질 이원화 / 사업장 검증"]
]

# 표 헤더 셀 스타일 적용
for c in range(cols):
    cell = table.cell(0, c)
    cell.text = headers[c]
    p = cell.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.font.name = FONT_NAME
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    if c == 0: cell.fill.solid(); cell.fill.fore_color.rgb = COLOR_DARK
    elif c == 1: cell.fill.solid(); cell.fill.fore_color.rgb = COLOR_PREMIUM
    elif c == 2: cell.fill.solid(); cell.fill.fore_color.rgb = COLOR_PRIMARY
    elif c == 3: cell.fill.solid(); cell.fill.fore_color.rgb = COLOR_LITE

# 데이터 입력 및 자동 줄바꿈 설정
for r in range(3):
    cell_lbl = table.cell(r+1, 0)
    cell_lbl.text = row_labels[r]
    cell_lbl.fill.solid()
    cell_lbl.fill.fore_color.rgb = RGBColor(0xEE, 0xE6, 0xDC)
    p_lbl = cell_lbl.text_frame.paragraphs[0]
    p_lbl.alignment = PP_ALIGN.CENTER
    p_lbl.font.name = FONT_NAME
    p_lbl.font.size = Pt(9)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = COLOR_DARK

    for c in range(3):
        cell_data = table.cell(r+1, c+1)
        cell_data.text = table_data[r][c]
        cell_data.fill.solid()
        cell_data.fill.fore_color.rgb = COLOR_WHITE
        for p in cell_data.text_frame.paragraphs:
            p.font.name = FONT_NAME
            p.font.size = Pt(8.5)
            p.font.color.rgb = COLOR_DARK

# [지침 2] 테이블 높이와 패딩을 감안하여 카드 세로 시작 좌표를 안전하게 이동
card_y_pos = current_top_s3 + table_height + Inches(0.4)

# --- 하단부: 티어별 전략 카드 (3 Columns 레이아웃) ---
card_width = Inches(3.577) # (11.333 전체 가용 너비 - 0.6 간격합산) / 3
card_height = Inches(2.1)
card_gap = Inches(0.3)

card_info = [
    {"title": "PREMIUM 전략", "color": COLOR_PREMIUM, "bullets": [
        "• IDC 사업화 전략 수립으로 시장 선점",
        "• 표준운영프로세스 구축으로 서비스 표준화",
        "• 버틀러형 전담 인력 배치로 SLA 보장",
        "• 전문기술인 확보로 고부가 솔루션 제공"
    ]},
    {"title": "STANDARD 전략", "color": COLOR_PRIMARY, "bullets": [
        "• 솔루션 R&D 투자로 차별화 기술력 확보",
        "• 현장 Pilot 검증을 통한 신뢰성 입증",
        "• 품질/개량체계 수립으로 운영 고도화",
        "• 리텐션 프로그램 적용으로 고객 이탈 방지"
    ]},
    {"title": "LITE 전략", "color": COLOR_LITE, "bullets": [
        "• 서비스 유형화로 신규 시장 모델 정립",
        "• 품질 기준 이원화 조치로 가성비 극대화",
        "• 명확한 가격 기준 수립으로 경쟁력 확보",
        "• 사업장 검증 기반 진입 리스크 사전 관리"
    ]}
]

for i, info in enumerate(card_info):
    card_x_pos = Inches(1.0) + i * (card_width + card_gap)

    # 카드 컨테이너 상자
    card_body = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x_pos, card_y_pos, card_width, card_height)
    card_body.fill.solid(); card_body.fill.fore_color.rgb = COLOR_WHITE
    card_body.line.color.rgb = COLOR_BORDER; card_body.line.width = Pt(0.5)

    # 상단 에지 라인
    card_top_line = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, card_x_pos, card_y_pos, card_width, Inches(0.06))
    card_top_line.fill.solid(); card_top_line.fill.fore_color.rgb = info["color"]
    set_shape_transparent_border(card_top_line)

    # 내부 텍스트 프레임 (지침 반영)
    card_box = slide3.shapes.add_textbox(card_x_pos + Inches(0.15), card_y_pos + Inches(0.15), card_width - Inches(0.3), card_height - Inches(0.3))
    ctf = card_box.text_frame
    ctf.word_wrap = True
    ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0

    # 타이틀
    p_title = ctf.paragraphs[0]
    p_title.text = info["title"]
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(11)
    p_title.font.bold = True
    p_title.font.color.rgb = info["color"]
    p_title.space_after = Pt(6)

    # 상세 내용 블릿
    for bullet_text in info["bullets"]:
        p_b = ctf.add_paragraph()
        p_b.text = bullet_text
        p_b.font.name = FONT_NAME
        p_b.font.size = Pt(8.5)
        p_b.font.color.rgb = COLOR_DARK
        p_b.space_after = Pt(2)

# ==========================================
# 5. 파일 저장 및 완료
# ==========================================
output_filename = "C:/Users/Administrator/Desktop/LG_사업추진전략보고서_수정3.pptx"
prs.save(output_filename)
print(f"성공: '{output_filename}' 파일이 성공적으로 생성되었습니다.")
