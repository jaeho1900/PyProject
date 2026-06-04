import random

class Account:
    account_count = 0
    def __init__ (self, name, balance):
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

    @classmethod
    def get_account_num(cls):
        print(cls.account_count)

    def deposit(self, income):
        if income >= 1:
            self.balance += income

    def withdraw(self, outcome):
        if outcome > self.balance:
            self.balance -= outcome
            print(f"{outcome} 출금되었습니다. 잔액은 {self.balance}입니다")
        else:
            print("잔액이 부족합니다")

    def display_info(self):
        print(f"은행이름: {self.bank}")
        print(f"예금주: {self.name}")
        print(f"계좌번호: {self.num}")
        print(f"잔액: {self.balance:,}원")

    def interest(self):
        self.balance = self.balance * 1.01

k = Account("tomy", 9990)
k.name
k.balance
Account.account_count
k.get_account_num()
k.deposit(100000)
k.balance
k.withdraw(150000)
k.display_info()
