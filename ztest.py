# 주어진 문자열이 회문이면 True, 회문이 아니면 False를 반환하라.
# 입력: madam, 출력: True
# 입력: tomato, 출력: False

a = input("문장을 입력하세요: ")

if a == a[::-1]:
    print("True")
else:
    print("False")

