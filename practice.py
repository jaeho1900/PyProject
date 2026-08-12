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


for i, j in enumerate(h):
    print(i ,j)
    if j == n:
        L1.append(i)

