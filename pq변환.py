import pandas as pd

excel_path = (
    r"C:\Users\Administrator\Desktop\오피스, 연구소 엣지 작업데이터_260811.xlsx"
)
output_parquet_path = (
    r"C:\Users\Administrator\Desktop\오피스_연구소_엣지_작업데이터_통합.parquet"
)

all_sheets = pd.read_excel(excel_path, sheet_name=None, engine="calamine")

df_list = []
for sheet_name, df in all_sheets.items():
    if not df.empty:
        df.insert(0, "운영센터명", sheet_name)
        df_list.append(df)

combined_df = pd.concat(df_list, ignore_index=True)
combined_df.columns = combined_df.columns.str.replace("\n", "")
combined_df.to_parquet(output_parquet_path, engine="pyarrow", index=False)

print(f"총 {len(df_list)}개 시트 병합 완료!")
print(f"전체 데이터 행 수: {len(combined_df)}")
print(f"저장 경로: {output_parquet_path}")
