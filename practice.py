import random

class Account:
    account_count = 0
    def __init__ (self, name, balance):
        self.input_count = 0
        self.name = name
        self.balance = balance
        self.bank = "sc은행"
        num1 = random.randint(0, 999)
        num2 = random.randint(0, 99)
        num3 = random.randint(0, 999999)
        num1 = str(num1).zfill(3)
        num2 = str(num2).zfill(2)
        num3 = str(num3).zfill(6)
        self.num = num1 + '-' + num2 + '-' + num3
        Account.account_count +=1
        self.deposit_book = [balance]
        self.withdraw_book = []

    @classmethod
    def get_account_num(cls):
        print(cls.account_count)

    def deposit(self, income):
        if income >= 1:
            self.deposit_book.append(income)
            print(f"{income:,}원 입금되었습니다.")
            self.balance += income
            self.input_count += 1
            if self.input_count % 5 == 0:
                self.deposit_book.append(self.balance * 0.01)
                print(f"{self.input_count}회차 이자 {self.balance * 0.01:,}원이 입금되었습니다")
                self.balance += self.balance * 0.01
                print(f"잔액은 {self.balance:,}입니다")

    def withdraw(self, outcome):
        if outcome <= self.balance:
            self.withdraw_book.append(outcome)
            self.balance -= outcome
            print(f"{outcome:,}원 출금되었습니다. 잔액은 {self.balance:,}원 입니다")
        else:
            print("잔액이 부족합니다")

    def display_info(self):
        print(f"은행이름: {self.bank}")
        print(f"예금주: {self.name}")
        print(f"계좌번호: {self.num}")
        print(f"잔액: {self.balance:,}원")

    def deposit_history(self):
        for i in self.deposit_book:
            print(f"{i:,}원", end = "\n")
        print(f"잔액은 {self.balance:,}원 입니다")

    def withdraw_history(self):
        for i in self.withdraw_book:
            print(f"{i:,}원", end = "\n")
        print(f"잔액은 {self.balance:,}원 입니다")

# 입금과 출금 내역이 기록되도록 코드를 업데이트 하세요.
# 입금 내역과 출금 내역을 출력하는 deposit_history와 withdraw_history 메서드를 추가하세요.

k = Account("tomy", 10000000)
j = Account("kim", 2000000)
m = Account("sir", 800000)

k.deposit(10000)
k.deposit(20000)
k.deposit(30000)
k.deposit(40000)
k.deposit(50000)
k.deposit(60000)
k.deposit_history()

k.withdraw(89990)
k.withdraw_history()

k.balance
