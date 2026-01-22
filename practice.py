apart = [ [101, 102], [201, 202], [301, 302] ]

m = []
n = []
for i in range(len(apart),0,-1):
    m = apart[i-1]
    for j in range(len(m),0,-1):
        n = m[j-1]
        print(n, "호")

for row in apart[::-1]:
    for col in row[::-1]:
        print(col, "호")
