def  print_5xn(a):
    if len(a)%5 == 0:
        k = len(a)//5
    else:
        k = len(a)//5+1
    for i in range(k):
        print(a[0:5])
        a = a[5:]

def print_5xn(line):
    chunk_num = int(len(line) / 5)
    for x in range(chunk_num + 1) :
        print(line[x * 5: x * 5 + 5])

def print_5xn(line):
    # 0부터 시작해서 5씩 건너뛰며 반복
    for i in range(0, len(line), 5):
        print(line[i : i + 5])

print_5xn("아이256엠078어보이유알어걸")
