# 0과 1로 이루어진 배열이 있다. 배열 자체를 오름차순으로 정렬하라.

# 입력: [1, 0, 1, 1, 1, 1, 1, 0, 0, 0], 출력: [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
# 입력: [1, 1], 출력: [1, 1]

a = [1, 0, 1, 1, 1, 1, 1, 0, 1, 0]

b = []
for i in range(len(a)):
    if a[0] == 1:
        b.append(a.pop(0))
    else:
        b.insert(0, a.pop(0))
print(b)


left, right = 0, len(a) - 1
while left < right:
    if a[left] == 0:
        left += 1
    elif a[right] == 1:
        right -= 1
    else:
        a[left], a[right] = a[right], a[left]
        left += 1
        right -= 1
