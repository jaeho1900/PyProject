def convert_int(string):
    return int(string.replace(',',''))

convert_int("1,234,567")

import datetime

now = datetime.datetime.now()
print(now.timedelta(day))


import datetime

now = datetime.datetime.now()

print(now.strftime("%H:%M:%S"))



print(datetime.datetime.strptime("2020-05-04", "%Y-%m-%d"))

