class Human:
    def __init__(self, name, age, sex):
        self.name = name
        self.age = age
        self.sex = sex
    def __del__(self):
        print("나의 죽음을 알리지마라")
    def who(self):
        print("이름:", self.name, "나이:", self.age, "성별:", self.sex)
    def setInfo(self, name, age, sex):
        self.name = name
        self.age = age
        self.sex = sex

areum = Human("조아름", 25, "여자")
areum.who()
del areum
