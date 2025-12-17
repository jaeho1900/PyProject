import requests
btc = requests.get("https://api.bithumb.com/public/ticker/").json()['data']

variant_price = int(btc['max_price']) - int(btc['min_price'])
standard = int(btc['opening_price']) + variant_price

if standard > int(btc['max_price']):
    print("상승장")
else:
    print("하락장")
