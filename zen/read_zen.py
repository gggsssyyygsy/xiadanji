

file = open('zen.txt', 'r').read()
#print file.read()

l1 = file.split("<td class='value'>\n$")[1:]
l2 = file.split("<h3>")[1:]
l3 = file.split("<h4>PIN: ")[1:]
for i in range(0, len(l1)):
    value = l1[i][:6]
    code = l2[i][:15]
    pin = l3[i][:8]
    #bb
    #code = l2[i][:16]
    #pin = l3[i][:4]
    print code + ', ' + pin + ', ' + value
