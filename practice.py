import random
class Account():
    def __init__ (bank_name, accounter_name, account_num, balance):
        self.bank_name = "sc은행"
        self.accounter_name = accounter_name  # 3-2-6 랜덤
        self.account_num = account_num
        self.balance = balance
       random.randrange(100,1000)
       random.randrange(10,100)
       random.randrange(100000,1000000)


print(f"str(random.randrange(100,1000))-str(random.randrange(10,100))-str(random.randrange(100000,1000000))")
