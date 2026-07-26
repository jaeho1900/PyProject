# 296 예외처리
# 문자열 PER (Price to Earning Ratio) 값을 실수로 변환할 때 에러가 발생합니다. 예외처리를 통해 에러가 발생하는 PER은 0으로 출력하세요.

# per = ["10.31", "", "8.00"]

# for i in per:
#     print(float(i))

import pandas as pd

df = pd.read_csv("d:/매수종목2.txt", dtype="str", sep='\t', header=None)

dic1 = dict(zip(df[0], df[1]))
print(dic1)

dic2 = {}
for i in range(len(df)):
    dic2[df.iloc[i,0]] = df.iloc[i,1]
print(dic2)
