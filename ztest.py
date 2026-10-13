# 정렬되지 않은 양의 정수로 이루어진 배열 A가 있다. 연속된 원소를 더한 값이 제시된 값 S와 같은 부분 배열을 찾아라. (인덱스 기준은 1이다.)
# 입력: arr = [1, 2, 3, 7, 5], s = 12, 출력: [2, 4]
    # 인덱스 2부터 4까지의 합: 2 + 3 + 7 = 12
# 입력: arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], s = 15, 출력: [1, 5]

arr = [1, 2, 3, 7, 5]
s = 12

s_t = 0
l_t = 0

# 1 2 3 7
# 2 3 7

total = 0
for i in range(len(arr)):
    for j in range(i, len(arr)):
        if total < s:
            total += arr[j]
            print("total<s:", total, i, j)
        else:
            print("loop1", total, i, j)
            break
    total = 0
    if total == s:
        print("loop2", total, i, j)
        break
print(i+1, j+1)
