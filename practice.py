class Stock:
    def __init__(self, name, code, per, pbr, rate):
        self.name = name
        self.code = code
        self.per = per
        self.pbr = pbr
        self.rate = float(rate)



삼성 = Stock("삼성전자", "005930")
삼성.get_name()
삼성.get_code()
삼성.name
