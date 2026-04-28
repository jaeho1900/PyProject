import random

class Account:
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

k = Account("tomy", 9990)
k.name
k.balance
k.bank
k.num



