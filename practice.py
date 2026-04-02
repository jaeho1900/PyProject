class Stock:
    def __init__(self, name, code, per, pbr, 배당수익률):
        self.name = name
        self.code = code
        self.per = per
        self.pbr = pbr
        self.배당수익률 = 배당수익률

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code


삼성 = Stock("삼성전자", "005930", 15.79, 1.33, 2.83)
현대 = Stock("현대차","005380",	8.70, 0.35, 4.27)
LG = Stock("LG전자","066570",	317.34,	0.69,	1.37)

for i in [삼성, 현대, LG]:
    print(i.code, i.per)
