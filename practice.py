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

    @classmethod
    def get_account_num(cls):
        print(cls.account_count)

    def deposit(self, income):
        if income >= 1:
            self.balance += income
            self.input_count += 1
            if self.input_count % 5 == 0:
                self.balance = self.balance * 1.01

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

# Account 클래스로부터 3개 이상 인스턴스를 생성하고 생성된 인스턴스를 리스트에 저장해보세요.

k = Account("tomy", 10000)
j = Account("kim", 20000)
m = Account("sir", 80000)

k.balance
j.balance
m.balance

customers = [k, j, m]



customers[2].balance



Account.get_account_num()


j.deposit(1000)
j.input_count

Account.account_count
