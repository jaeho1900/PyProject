import requests
btc = requests.get("https://api.bithumb.com/public/ticker/").json()['data']

head_num = num1.replace("-","")

Multipli = "234567892345"

k,j = 0,0
for i in zip(head_num, Multipli):
    k = int(i[0]) * int(i[1])
    j = j+k
t = 11 - (j % 11)

if int(num1[-1]) == t:
    print("유효한 번호")
else:
    print("유효하지 않은 번호")




print(j)



for i in head_num:


if head_num <9:
    print("서울 입니다")
else:
    print("서울이 아닙니다.")





max_num = ''






if head_num < 3:
    max_num = "강북구"
elif head_num < 6:
    max_num = "도봉구"
else:
    max_num = "노원구"

print(max_num)



