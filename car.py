class 차:
    def __init__(self, 바퀴, 가격):
        self.바퀴 = 바퀴
        self.가격 = 가격

class 자전차(차):
    def __init__(self, 바퀴, 가격, 구동계):
        차.__init__(self, 바퀴, 가격)
        # super().__init__(바퀴, 가격)
        self.구동계 = 구동계

class 자동차(차):
    def 정보(self):
        print(f'바퀴수 {self.바퀴}')
        print(f'가격 {self.가격}')

car = 차(2, 1000)
car.바퀴
car.가격

bicycle = 자전차(2, 100)
bicycle.가격

bicycle = 자전차(2, 100, "시마노")
bicycle.구동계

car = 자동차(4, 1000)
car.정보()
