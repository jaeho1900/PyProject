# 294 파일 읽기
# 바탕화면에 생성한 '매수종목1.txt' 파일을 읽은 후 종목코드를 리스트에 저장해보세요.

# 295 파일 읽기
# 바탕화면에 생성한 '매수종목2.txt' 파일을 읽은 후 종목코드와 종목명을 딕셔너리로 저장해보세요. 종목명을 key로 종목명을 value로 저장합니다.

import pandas as pd
data = ['005930', '005380', '035420']
df = pd.DataFrame(data)
df.to_csv("C:/Users/Administrator/Desktop/매수종목1.txt", sep='\t', index=False, header=False)

data2 = [['005930', '삼성전자'], ['005380', '현대차'], ['035420', 'NAVER']]
df2 = pd.DataFrame(data2)
df2.to_csv("C:/Users/Administrator/Desktop/매수종목2.txt", sep='\t', index=False, header=False)

data3 = [['삼성전자','005930','15.79'], ['NAVER','035420','55.82']]
df3 = pd.DataFrame(data3, columns=["종목명", "종목코드", "PER"])
df3.to_csv("C:/Users/Administrator/Desktop/매수종목.csv", index=False, encoding="cp949")

