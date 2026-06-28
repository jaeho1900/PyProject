class 차:
    def __init__(self, tier_num, price):
        self.바퀴 = tier_num
        self.가격 = price

car = 차(2, 1000)
car.바퀴
car.가격

# 차 클래스를 상속받은 자전차 클래스를 정의하세요.
class 자전차(차):
    pass

# 다음 코드가 동작하도록 자전차 클래스를 정의하세요. 단 자전차 클래스는 차 클래스를 상속받습니다.
bicycle = 자전차(2, 100)
bicycle.가격
100
