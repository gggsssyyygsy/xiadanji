import csv
import glob

'''Razer Lancehead Tournament Gaming Mouse
trackings_string = \
    '1ZY8F7290328178108, 1ZY8F8730328245718, 1ZY8F8860328194535, 1ZV986510370424794, 1Z97279W0329732503, 1Z972WE10318637552, 1Z300WX10318694887, 1Z971V2A0329688928, 1Z3Y66E90318645092, 1Z971E1E0325103214, 1Z971ER50370419356, 1Z300WR70318652890, 1Z300WV70318672623, 1Z971E1R0370440484, 1Z300WW20318657087, 1Z300F670370397397, 1Z971E150370445521, 1ZWA03460370397143, 1Z300W0R0318695983, 1Z300WF40318717729, 1ZY8R0660329793703, 1Z300F990370449842, 1Z971R970370439398, 1Z300F430370500461, 1Z300F520370427275, 1Z971VA10370488390, 1Z971T6T0370458814, 1Z971VA40370427584, 1Z97279R0370412683, 1Z300F780370446438, 1Z9714VW0370446702, 1Z9714WV0370379849, 1Z300F9W0370447899, 1ZY8R1110318635595, 1Z9723Y60318663463, 1Z9723X40318697235, 1Z3001E20329724899, 1Z9723X80318715396, 232908120005257, 1Z972WE80318769282, 1Z972F7R0329809852, 1Z972WF40318686547, 1Z3Y65X50370484301, 1ZY8F9070328269253, 1Z972F600325120851, 1ZWA10760370454574, 1ZV987090370473354, 1Z972WE50318751402, 232384020001863, 1Z300FV40325133531, 1Z300FV50325117673, 094534320000536, 1Z3Y53340325093317, 1Z300FX60325159973, 1Z3Y56130325082890, 1Z971VV10325140866, 1Z9719VE0325069577, 1Z3Y65970318663799, 1Z3Y66E40318680446, 094418220001346, 094419020001826, 1Z9728W00370475723, 1ZY8F8440329834125, 1ZY8R0060329827575, 1ZV9812X0370465003, 1Z300F900370465877, 1Z300WR60318764913, 1Z300F320370531618, 1Z971A7Y0370470315, 1ZY8R0410325183710, 1Z300F420370518016, 1ZY8R0720328296053, 1ZY8R0300328288659, 1Z97279E0329832964, 1Z97231R0325142547, 232393120000690, 1Z970Y700328415343, 1Z300WF30318916828, 1Z300F820370696786, 1Z3Y6510YN30086356, 1ZY8F7370329956330, 1ZY8F9030330032368, 1ZV981E70370662953, 1Z971E4V0370717792, 1Z300F950370717292, 1Z3Y52F50325331994, 1ZY8F8920330000861, 1ZY8F9010330138507, 1ZY8F8830330035985, 1Z971TT30370723813, 1ZY8F8010328585049, 1ZY8R0740319073780, 1Z300WX90318995154, 1Z972WF60319111714, 1Z300F450370746292, 1Z300F490370809421, 1Z97278V0325289342, 1ZY8F9750330202683, 1ZV980150370754604, 1ZY8R0860330176358, 1ZY8F7420330208073, 1ZY8F8180330074289, 1ZY8R0570330117770, 1Z300F460370830957, 1Z9714R40325509652, 1Z300F570370792504, 1ZY8F8430330243683, 1Z97231Y0325509773, 1ZWA12490370841783, 1ZV977880370944466'
'''
trackings_string = \
    '1ZY8F6710318801937, 1ZY8F6920325251729, 1ZY8F6920325251756, 1Z97279X0329931359, 1Z3001EV0329982984, 1Z3001E60330050633, 1Z3Y56880328532534, 1Z3004R70328666204, 1Z3004V40328581048, 1Z3Y57150328993476, 1ZY8F6770325887027, 1Z30041X0329093118, 1ZY8F7600325878058, 1Z97Y2050325959583, 1ZY8F7230326182028'

def tracking_spliter():
    trackings = []
    for file in glob.glob('mytrackings.csv'):
        with open(file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in spamreader:
                for item in row:
                    item=item.replace('\xc2', '')
                    item=item.replace('\xa0', '')
                    split_items = item.split(';')
                    for split_item in split_items:
                        trackings.append(split_item.strip())
    my_trackings = set(trackings)
    return my_trackings

def check_sl33(my_trackings):
    item_counter = {}
    remove_trackings = set()
    for file in glob.glob('SL*.csv'):
        with open(file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            date = ''
            for row in spamreader:
                if row[0]:
                    date = row[0]
                if row[1]:
                    tracking = row[1].strip()
                upc = row[2]
                item = row[3]
                qty = row[4]
                if not qty:
                    continue
                for my_tracking in my_trackings:
                    if my_tracking in tracking or tracking in my_tracking or tracking == my_tracking:
                        if item in item_counter:
                            item_counter[item] += int(qty)
                        else:
                            item_counter[item] = int(qty)
                        remove_trackings.add(my_tracking)
                        continue
    my_trackings -= remove_trackings
    print item_counter
    print 'remaining trackings:', my_trackings

def check_all_orders():
    upc_counter = {}
    item_counter = {}
    weird_counter = []
    for file in glob.glob('*.csv'):
        with open(file, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            date = ''
            for row in spamreader:
                if row[0].strip() == 'date':
                    continue
                if row[0]:
                    date = row[0]
                if row[1]:
                    tracking = row[1].strip()
                upc = row[2]
                item = row[3]
                if not item:
                    continue
                try:
                    qty = int(row[4])
                except:
                    weird_counter.append((date, upc, item, qty))
                if upc in upc_counter:
                    upc_counter[upc]['qty'] += qty
                    upc_counter[upc]['item'].add(item)
                else:
                    upc_counter[upc] = {}
                    upc_counter[upc]['qty'] = qty
                    upc_counter[upc]['item'] = set([item])
                if item in item_counter:
                    item_counter[item] += qty
                else:
                    item_counter[item] = qty
    #print upc_counter
    print 'UPC COUNTER!!!'
    for upc in upc_counter:
        print upc, upc_counter[upc]['item'], upc_counter[upc]['qty'], '\n'
    #print item_counter
    print 'ITEM COUNTER!!!'
    for item in item_counter:
        print item, item_counter[item], '\n'
    #print weird_counter
    print 'WEIRD COUNTER!!!'
    for weird in weird_counter:
        print weird

if __name__ == '__main__':
    #check_all_orders()
    #exit()
    my_trackings = tracking_spliter()
    check_sl33(my_trackings)
