# 다음 코드가 동작하도록 차 클래스를 정의하세요.

# >> car = 차(2, 1000)
# >> car.바퀴
# 2
# >> car.가격
# 1000

class 차:
    def __init__ (self, tier_num, price):
        self.바퀴 = tier_num
        self.가격 = price

