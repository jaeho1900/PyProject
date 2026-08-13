# 코드1
h = [168,170,168,173,168, 168]

kdic = []
for i in range(len(h)):
    kdic.append((i, h[i]))

lo = []
for i, j in kdic:
    if j == 168:
        lo.append(i)
print(lo)


#코드2
h = [168,170,168,173,168, 168]
h1 = h
k = 0
L = list()
L1 = list()
n = 168
for i in range(h1.count(n)):
    idx = h1.index(n)
    k += idx
    L.append(k)
    k += 1
    h1 = h1[idx+1:]
print(L)
