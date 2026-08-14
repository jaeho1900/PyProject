import pandas as pd

# 1. 데이터프레임 생성 (예: 특수문자와 쉼표가 섞인 적요 데이터)
data = {
    "거래ID": [101, 102],
    "금액": [15000, 23000],
    "적요": ["교통비, 택시(심야)", '도서 구입 "데이터 분석"\n(배송비 포함)'],
}
df = pd.DataFrame(data)

# 2. Parquet 파일로 저장
df.to_parquet("transactions.parquet", index=False)

# 3. 전체 데이터 불러오기
output_parquet = (
    r"C:\Users\Administrator\Desktop\오피스_연구소_작업데이터_통합.parquet"
)

df_loaded = pd.read_parquet(output_parquet)

# 4. [속도 최적화] 특정 컬럼만 골라서 초고속으로 불러오기
df_subset = pd.read_parquet("transactions.parquet", columns=["거래ID", "금액"])




# -------------------------------------------------------------
import pandas as pd

# 1. 파일 경로 설정 (Windows 경로 역슬래시 에러 방지를 위해 r을 붙임)
file_path = r"C:\Users\Administrator\Desktop\오피스, 연구소 엣지 작업데이터_260811.xlsx"

# 2. 모든 시트를 딕셔너리 형태로 한 번에 읽어오기
#    engine='calamine'을 설치하여 사용하면 읽는 속도가 훨씬 빨라집니다.
all_sheets = pd.read_excel(file_path, sheet_name=None, engine="calamine")

# 3. '개요' 시트를 제외한 나머지 시트들의 DataFrame 리스트 생성
dfs = []
for sheet_name, df in all_sheets.items():
    # '개요' 시트 제외 (시트 이름 앞뒤 공백 방지를 위해 .strip() 적용)
    if sheet_name.strip() != "개요":
        dfs.append(df)

# 4. 하나의 데이터프레임으로 수직 병합 (첫 행의 동일한 컬럼 기준으로 결합)
combined_df = pd.concat(dfs, ignore_index=True)

# 5. 결과 확인
print("병합 완료!")
print(f"- 병합된 전체 데이터 크기: {combined_df.shape[0]}행 x {combined_df.shape[1]}열")
print(combined_df.head())

# 6. [권장] 이후 빠른 작업 및 적요란 깨짐 방지를 위해 Parquet 파일로 저장
output_parquet = (
    r"C:\Users\Administrator\Desktop\오피스_연구소_작업데이터_통합.parquet"
)
combined_df.to_parquet(output_parquet, index=False)
print(f"- 통합 Parquet 파일 저장 완료: {output_parquet}")

