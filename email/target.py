from gmail.gmaillib import account, message
from email.header import decode_header
from gmail.helper import loadConfig


username, password = loadConfig("gmail/config.csv")

keywords = ['qty:', 'Tracking #']
items = [
         'Amazon Fire TV with 4K Ultra HD and Alexa Voice Remote',
         'Fire HD 8 with Alexa (8&quot; HD Display) Black - 16GB',
         'Amazon Fire TV Stick with Alexa Voice Remote',
         'Fire 7 with Alexa (7&quot; Display Tablet) Black - 8GB',
         "Harry's Men's Razor Blade Refills - 4ct",
         "Harry's Men's Razor Blade Refills - 8ct",
         "Harry's Men's Shave Cream - 3.4oz",
         "Harry's Shaving Set - 4pk",
         ]

shipping_subject_keywords = ['Target!!!!!!!']

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
        if shipping_subject_keywords[0] in subject:
            '''
            if 'Good news! Your order #' in subject:
                order_number = subject.split('Good news! Your order #')[1][:13]
            else:
                order_number = subject.split('Good news! Items have shipped from your order #')[1][:13]
            '''
            order_number = 1
            #initialize order counter
            content = email.body
            print content
            #get tracking
            trackings = content.split('Tracking # ')
            for i in range(1, len(trackings)):
                tracking = trackings[i][:18].strip().split(' ')[0]
                #get item and qty
                parts = trackings[i].split('qty: ')
                for j in range(0, len(parts) - 1):
                    for item in items:
                        if item in parts[j]:
                            try:
                                qty = int(parts[j + 1][0])
                            except:
                                qty = int(parts[j + 1][0])
                            if (tracking,qty) in item_counter[item]['trackings']:
                                continue
                            item_counter[item]['qty'] += qty
                            item_counter[item]['trackings'].append((tracking,qty))
                            print tracking, qty
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
    g_account = account(username[0], password[0])
    emails = g_account.inbox(start=0, amount=20, date='09/05/2018')
    shipped_item_counter, shipped_order_counter = get_trackings(emails)
    #canceled_orders = get_canceled_orders(emails)
    #item_counter, order_counter = get_order_confirmations(emails, canceled_orders)

    for item in items:
        print item
        #print 'qty: ', item_counter[item]['qty']
        print 'shipped qty: ', shipped_item_counter[item]['qty']
        for tracking in shipped_item_counter[item]['trackings']:
            print tracking[0], tracking[1]
    
    for order_number in shipped_order_counter:
        #if order_number not in order_counter:
        #    error_orders.append(order_number)
        #    continue
        for item in shipped_order_counter[order_number]:
            shipped_qty = shipped_order_counter[order_number][item]['qty']
            #order_counter[order_number][item]['qty'] -= shipped_qty

    '''
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
    '''
