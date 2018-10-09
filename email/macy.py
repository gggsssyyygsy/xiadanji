from gmail.gmaillib import account, message
from email.header import decode_header
from gmail.helper import loadConfig
from bs4 import BeautifulSoup

username, password = loadConfig("gmail/config.csv")

items = [
        'Apple Watch Series 3 (GPS), 38mm Gold Aluminum Case with Pink Sand Sport Band',
        'Apple Watch Series 3 (GPS), 38mm Space Gray Aluminum Case with Black Sport Band',
        'Apple Watch Series 3 (GPS), 38mm Space Gray Aluminum Case with Gray Sport Band',
        'Apple Watch Series 3 (GPS), 38mm Silver Aluminum Case with Fog Sport Band',
        'Apple Watch Series 3 (GPS,) 42mm Space Gray Aluminum Case with Black Sport Band',
        'Apple Watch Series 3 (GPS), 42mm Gold Aluminum Case with Pink Sand Sport Band',
        'Apple Watch Series 3 (GPS), 42mm Silver Aluminum Case with Fog Sport Band',
        'Apple Watch Series 3 (GPS), 42mm Space Gray Aluminum Case with Gray Sport Band',
        'Apple Watch Nike+ (GPS), 38mm Silver Aluminum Case with Pure Platinum/Black Nike Sport Band',
        'Apple Watch Nike+ GPS, 38mm Space Gray Aluminum Case with Anthracite/Black Nike Sport Band',
         ]

shipping_subject_keywords = ['your order 147','has shipped']
confirmation_subject_keywords = ['thanks for your order 147', '']
tracking_split_word = 'Tracking #:</span>'
qty_split_word = 'Qty:</span>'
order_number_length = 10

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
        subject = subject.lower()
        if shipping_subject_keywords[0] in subject and shipping_subject_keywords[1] in subject:
            order_number = subject.split('your order ')[1][:order_number_length]
            #initialize order counter
            content = email.body.split('Waiting to ship')[0]
            #print email.body 
            #exit()
            #get tracking
            trackings = []
            parts = content.split(tracking_split_word)
            for i in range(1, len(parts)):
                parsed_html = BeautifulSoup(parts[i], 'html.parser')
                tracking = parsed_html.a.text

                # not important in other code.
                if tracking == 'multiple tracking URLs':
                    tracking = 'multiple_{}'.format(order_number)

                trackings.append(tracking)
            #get item and qty
            parts = content.split(qty_split_word)
            for i in range(0, len(parts) - 1):
                parsed_html = BeautifulSoup(parts[i+1], 'html.parser')
                for item in items:
                    if item in parts[i]:
                        tracking = str(trackings[i])
                        qty = int(parsed_html.span.text)
                        if (tracking,qty) in item_counter[item]['trackings']:
                            continue
                        item_counter[item]['qty'] += qty
                        item_counter[item]['trackings'].append((tracking,qty))
                        #print tracking, qty
                        if order_number not in order_counter:
                            order_counter[order_number] = {}
                        if item in order_counter[order_number]:
                            order_counter[order_number][item]['qty'] += qty
                            order_counter[order_number][item]['trackings'].append((tracking,qty))
                        else:
                            order_counter[order_number][item] = {}
                            order_counter[order_number][item]['qty'] = qty
                            order_counter[order_number][item]['trackings']=[(tracking,qty)]
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
        subject = subject.lower()
        print confirmation_subject_keywords[0], confirmation_subject_keywords[1], subject
        if confirmation_subject_keywords[0] in subject and confirmation_subject_keywords[1] in subject:
            order_number = subject.split('Thanks for your order ')[1][:order_number_length]
            print order_number
            if order_number in canceled_orders:
                continue
            #initialize order counter
            if order_number not in order_counter:
                order_counter[order_number] = {}
            content = email.body
            print content
            #get item and qty
            parts = content.split(qty_split_word)
            for i in range(0, len(parts) - 1):
                print 11111111
                parsed_html = BeautifulSoup(parts[i+1], 'html.parser')
                for item in items:
                    print 2222222
                    if item in parts[i]:
                        qty = int(parsed_html.span.text)
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
        subject = subject.lower() 
    if "your macy's order" in subject and 'was canceled' in subject:
            order_number = subject.split("your macy's order")[1][:order_number_length]
            canceled_orders.append(order_number)
    return canceled_orders

if __name__ == '__main__':
    error_orders = []
    g_account = None
    g_account = account(username[0], password[0])
    emails = g_account.inbox(start=0, amount=2000, date='08/26/2018')
    #shipped_item_counter, shipped_order_counter = get_trackings(emails)
    canceled_orders = get_canceled_orders(emails)
    item_counter, order_counter = get_order_confirmations(emails, canceled_orders)
    
    for item in items:
        print item
        print 'qty: ', item_counter[item]['qty']
        print 'shipped qty: ', shipped_item_counter[item]['qty']
        for tracking in shipped_item_counter[item]['trackings']:
            print tracking[0], tracking[1]

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
