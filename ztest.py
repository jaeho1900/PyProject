# 정렬되지 않은 양의 정수로 이루어진 배열 A가 있다. 연속된 원소를 더한 값이 제시된 값 S와 같은 부분 배열을 찾아라. (인덱스 기준은 1이다.)
# 입력: arr = [1, 2, 3, 7, 5], s = 12, 출력: [2, 4]
    # 인덱스 2부터 4까지의 합: 2 + 3 + 7 = 12
# 입력: arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], s = 15, 출력: [1, 5]


arr = [1, 2, 3, 7, 5]
s = 12
st = 0
la = 0
total = 0
total2 = 0

for i in range(len(arr)):
    if sum(arr[i:len(arr)]) == s:
        print(len(arr)-i)


for i in range(st, len(arr)):
    total += arr[i]
    if total == s:
        print(total)
        break
    elif total > s:
        st += 1
        for i in range(st, len(arr)):
            total2 += arr[i]
            if total2 == s:
                print(total2)
                break
            elif total2 > s:
                st += 1
                break
            else:
                continue
        break
    else:
        continue
print(st, total, total2)


