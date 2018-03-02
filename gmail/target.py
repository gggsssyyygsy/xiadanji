from gmaillib import account, message
from email.header import decode_header

username, password = loadConfig("config.csv")

keywords = ['qty:', 'Tracking #']
'''
         'Pokken Tournament Nintendo Wii U',
         'Super Mario Maker Nintendo Wii U',
         'New Super Mario Bros U + New Super Luigi U Nintendo Wii U',
         'Razer Lancehead Tournament Gaming Mouse',
         'Pokemon X Nintendo 3DS',
         'Pokemon Y Nintendo 3DS',
         'Nintendo Switch Super Mario Odyssey Edition',
         'Nintendo&#174; 2DS - Scarlet Red with New Super Mario Bros. 2Game Pre-Installed',
         'Nintendo&#174; 2DS Bundle with Mario Kart 7 - Electric Blue',
         'Ring Stick Up Cam Outdoor Security Camera - Black',
         'Nintendo&#174; Switch&#153; with Neon Blue and Neon Red Joy-Con&#153;',
         'Amazon Kindle Paperwhite, Wi-Fi, Special Offers - Black',
         'PlayStation&#174; 4 1TB Console',
         'Amazon Fire TV Stick with Alexa Voice Remote',
         'Google Chromecast'
         'Epson WorkForce WF-3640 Wireless All-in-One Printer',
         'PlayStation 4 Pro Destiny 2 Limited Edition Bundle',
         "Xbox One S 1TB Assassin's Creed Origins Bonus Bundle",
         'PlayStation&#174; 4 1TB Console',
         'Acer Chromebook 15, Celeron N3060, 15.6" HD, 2GB LPDDR3, 16GB Storage, CB3-532-C3F7',
'''
items = [
         'Amazon Fire TV Stick with Alexa Voice Remote',
         ]

def get_trackings(emails):
    order_counter = {} #{order# : {item: {qty:0, trackings:[]}}
    item_counter = {} #{item# : {qty:0, trackings:[]}}
    #initialize item counter
    for item in items:
        item_counter[item] = {'qty' : 0, 'trackings' : []}
    for email in emails:
        subject = email.subject
        if not subject:
            continue
        if 'Good news! Your order #' in subject or 'Good news! Items have shipped from your order #' in subject:
            if 'Good news! Your order #' in subject:
                order_number = subject.split('Good news! Your order #')[1][:13]
            else:
                order_number = subject.split('Good news! Items have shipped from your order #')[1][:13]
            #initialize order counter
            content = str(email.parsed_email)
            #get tracking
            trackings = content.split('Tracking # ')
            for i in range(1, len(trackings)):
                tracking = trackings[i][:30].strip().split(' ')[0]
            #get item and qty
            parts = content.split('qty: ')
            for i in range(0, len(parts) - 1):
                for item in items:
                    if item in parts[i]:
                        try:
                            qty = int(parts[i + 1][0] + parts[i + 1][1])
                        except:
                            qty = int(parts[i + 1][0])
                        if tracking in item_counter[item]['trackings']:
                            continue
                        item_counter[item]['qty'] += qty
                        item_counter[item]['trackings'].append(tracking)
                        print tracking, qty
                        if order_number not in order_counter:
                            order_counter[order_number] = {}
                        if item in order_counter[order_number]:
                            order_counter[order_number][item]['qty'] += qty
                            order_counter[order_number][item]['trackings'].append(tracking)
                        else:
                            order_counter[order_number][item] = {}
                            order_counter[order_number][item]['qty'] = qty
                            order_counter[order_number][item]['trackings']=[tracking]
                        break
        else:
            continue

    return item_counter, order_counter

#get confirmations and calculate total amout
def get_order_confirmations(emails, canceled_orders = []):
    order_counter = {} #{order# : {item: {qty:0, trackings:[]}}
    item_counter = {} #{item# : {qty:0, trackings:[]}}
    #initialize item counter
    for item in items:
        item_counter[item] = {'qty' : 0}
    for email in emails:
        subject = email.subject
        if not subject:
            continue
        if "Thanks for shopping Target! Here" in subject:
            try:
                order_number = subject.split('s your order #: ')[1][:13]
            except:
                order_number = subject.split('s your order #')[1][:13]
            if order_number in canceled_orders:
                continue
            #initialize order counter
            if order_number not in order_counter:
                order_counter[order_number] = {}
            content = str(email.parsed_email)
            #get item and qty
            parts = content.split('qty: ')
            for i in range(0, len(parts) - 1):
                for item in items:
                    if item in parts[i]:
                        try:
                            qty = int(parts[i + 1][0] + parts[i + 1][1])
                        except:
                            qty = int(parts[i + 1][0])
                        item_counter[item]['qty'] += qty
                        if item in order_counter[order_number]:
                            order_counter[order_number][item]['qty'] += qty
                        else:
                            order_counter[order_number][item] = {}
                            order_counter[order_number][item]['qty'] = qty
                        break
        else:
            continue
    return item_counter, order_counter

def get_canceled_orders(emails):
    canceled_orders = []
    for email in emails:
        subject = email.subject
        if not subject:
            continue
        if "Sorry, we had to cancel." in subject:
            content = str(email.parsed_email)
            order_number = content.split('</a>. There was a technical issue that prevented us from fulfilling your order.')[0][-13:]
            canceled_orders.append(order_number)
    return canceled_orders

if __name__ == '__main__':
    error_orders = []
    g_account = None
    g_account = account(username, password)
    emails = g_account.inbox(start=0, amount=1000, date='11/15/2017')
    shipped_item_counter, shipped_order_counter = get_trackings(emails)
    canceled_orders = get_canceled_orders(emails)
    item_counter, order_counter = get_order_confirmations(emails, canceled_orders)

    for item in items:
        print item
        print 'qty: ', item_counter[item]['qty']
        print 'shipped qty: ', shipped_item_counter[item]['qty']
        print shipped_item_counter[item]['trackings']

    for order_number in shipped_order_counter:
        if order_number not in order_counter:
            error_orders.append(order_number)
            continue
        for item in shipped_order_counter[order_number]:
            shipped_qty = shipped_order_counter[order_number][item]['qty']
            order_counter[order_number][item]['qty'] -= shipped_qty

    for order_number in order_counter:
        flag = True
        for item in order_counter[order_number]:
            if order_counter[order_number][item]['qty'] != 0:
                if flag:
                    print '-------split line------\n'
                    print 'Order number:', order_number
                    flag = False
                print item
                print 'qty: ', order_counter[order_number][item]['qty']
                print '\n'

    print 'These Orders Have Problems, check manually!!!', error_orders
    print 'These Orders got canceled, check manually!!!', canceled_orders
