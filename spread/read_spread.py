file = open('spread.txt', 'r').read()
#print file.read()
date = '01/27/2018'
l1 = file.split(date)[1:]
l2 = file.split("Card Number :")[1:]
l3 = file.split("Pin :")[1:]
for i in range(0, len(l2)):
    value = l1[i].strip()[:7].strip()
    code = l2[i].strip()[:16].strip()
    pin = l3[i].strip()[:8].strip()
    print code + ', ' + pin + ', ' + value

