class MenuClass:
    def __init__(self):
       self.menu = ['','Americano', 'Latte', 'Espresso', 'Mocha', '식혜', '수정과']
       self.price = [0,1500, 2000, 1700, 2500, 2000, 1900]
       self.bill = [0, 10000, 5000, 1000]
       self.total = 0

    #############################
    # 메뉴 보이기
    def menu_print(self):
        i = 1
        while i< len(self.menu):
            print(i, self.menu[i], self.price[i])
            #print("%d. %-10s %5d"% (i, menu[i], price[i]))
            i = i+1
    #############################

    #############################
    # 음료  선택
    def menu_select(self):
        n = int(input("음료를 선택하세요 : "))
        price_sum = self.price[n]
        print(self.menu[n], self.price[n],'원 ', '합계 ', price_sum, '원')

        # 음료 추가

        while n != 0:
            print()
            n = int(input("계속 주문은 음료 번호를, 지불은 0을 누르세요 : "))
            if n > 0 and n < len(self.menu):
                price_sum = price_sum + self.price[n]
                print(self.menu[n], self.price[n],'원 ', '합계 ', price_sum, '원')
            else :
                if n == 0 :
                    print("주문이 완료되었습니다.")
                else :
                    print("없는 메뉴입니다.")
        self.total += price_sum
        return price_sum
    ##############################

    ##############################
    # 지불
    def menu_pay(self, total_price):
        # 지불 방법 출력
        for i in range (1, len(self.bill)):
            print( i,'.',self.bill[i],'원',end='   ')
        print()

        # 지불
        pay = 0
        while pay < total_price:
            n = int(input("지불 금액을 입력하세요 : "))
            if n>0 and n<len(self.bill):
                pay = pay + self.bill[n]
                print('총 지불액 :', pay,'원')
            else :
                print('다시 선택하세요.')

        print('거스름 ', pay-total_price, '원')
    ###############################

#인스턴스 생성
menu1 = MenuClass()
#일일 정산용
calc = 0
while(calc != 99):
    menu1.menu_print()
    total_price = menu1.menu_select()
    menu1.menu_pay(total_price)
    calc = int(input("일일 정산은 99, 새로운 주문은 1을 누르세요."))
print("오늘의 판매액은 ", menu1.total, "원 입니다.")

