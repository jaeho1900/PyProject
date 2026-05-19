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

k = Account("tomy", 9990)
j = Account("jam", 9990)
k.name
j.name
Account.account_count
k.get_account_num()
j.get_account_num()
k.deposit(100000)
k.balance
