# 주어진 문자열이 회문이면 True, 회문이 아니면 False를 반환하라.
# 입력: madam, 출력: True
# 입력: tomato, 출력: False

# 코파일러 끄기
a = input("문장을 입력하세요: ")

k= len(a)//2

if a[:k] == a[::-1][:k]:
    print("True")
else:
    print("False")

