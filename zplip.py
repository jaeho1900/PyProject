# ======================
# parquet 파일에서 컬럼을 추가하는 파이썬 코드
# ======================

# -----------
# 1. Polars 활용 (대용량 데이터 권장)
# 메모리 사용량이 적고 연산 속도가 가장 빠릅니다.

import polars as pl

# 1. Parquet 파일 읽기
df = pl.read_parquet("input.parquet")

# 2. 새로운 컬럼 추가 (예: 기존 컬럼 가공 또는 고정값)
df = df.with_columns(
    (pl.col("price") * pl.col("quantity")).alias("total_amount"),
    pl.lit("KRW").alias("currency"),
)

# 3. 저장 (압축 알고리즘 지정 가능: snappy, zstd 등)
df.write_parquet("output.parquet", compression="zstd")

# -----------
# 2. PyArrow 활용 (가장 가벼운 표준 라이브러리)
# DataFrame 변환 없이 Arrow Table 상태에서 직접 컬럼을 조작하여 오버헤드를 최소화합니다.

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

# 1. Table 읽기
table = pq.read_table("input.parquet")

# 2. 새 컬럼 데이터 생성 (배열 연산 또는 고정값)
total_amount = pc.multiply(table["price"], table["quantity"])
status_array = pa.array(["Active"] * table.num_rows)

# 3. 컬럼 추가 (append_column)
table = table.append_column("total_amount", total_amount)
table = table.append_column("status", status_array)

# 4. 저장
pq.write_table(table, "output.parquet", compression="snappy")

# -----------
# 3. Pandas 활용 (일반적인 방식)
# 100만 건 수준의 데이터에서 간단하게 처리할 때 사용합니다.

import pandas as pd

# 1. Parquet 파일 읽기
df = pd.read_parquet("input.parquet")

# 2. 컬럼 추가
df["total_amount"] = df["price"] * df["quantity"]
df["created_year"] = 2026

# 3. 저장
df.to_parquet("output.parquet", engine="pyarrow", compression="snappy")
