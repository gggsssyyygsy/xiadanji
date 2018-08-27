from gmaillib import account, message
from email.header import decode_header
from bs4 import BeautifulSoup
import re
import requests

username, password = loadConfig("config.csv")

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
'''
items = [
    'Amazon Fire TV Stick with Alexa Voice Remote',
    'Google Chromecast'
]

zips = ['19701', '19713', '19720', '03060', '95616']

def get_trackings(emails):
    order_counter = {}  # {zip: {order# : {item: {qty:0, trackings:[]}}}
    item_counter = {}  # {zip: {item# : {qty:0, trackings:[]}}}
    for email in emails:
        subject = email.subject
        if not subject:
            continue
        if 'Your order #BBY01-' in subject and 'has shipped' in subject:
            order_number = subject.split('Your order #BBY01-')[1][:12]
            content = str(email.parsed_email)
            # TODO change to BS4 in the future
            '''
            payload = None
            if email.parsed_email.is_multipart():
                print "TODO, Deal with multipart!!!!"
                exit()
                for payload in email.parsed_email.get_payload():
                # if payload.is_multipart(): ...
                    print payload.get_payload()
            else:
                payload = email.parsed_email.get_payload()
            parsed_html = BeautifulSoup(payload, 'html.parser')
            '''
            #get shipping zip:
            zip_flag = False
            for zip in zips:
                if zip in content:
                    zip_flag = True
                    if not zip in order_counter:
                        order_counter[zip] = {}
                    if not zip in item_counter:
                        item_counter[zip] = {}
                    break
            if not zip_flag:
                print 'no shipping address found'
                print content
                exit()
            # get tracking
            tracking_html = content.split('TRACKING #<br />')[1].split('</span>')[0]
            parsed_tracking = BeautifulSoup(tracking_html, 'html.parser')
            tracking = parsed_tracking.a.text
            tracking_url = parsed_tracking.a['href']
            # TODO if ... in tracking, requests url, get 'trackingNumber='
            if '...' in tracking:
                search_tracking_header = tracking.split('...')[0].strip()
                search_tracking_tail = tracking.split('...')[1].strip()
                headers = {'User-Agent': 'Mozilla/5.0'}
                page = requests.get(tracking_url, headers=headers).text
                first_part = page.split(search_tracking_header)[1]
                missing_digits = first_part.split(search_tracking_tail)[0]
                tracking = search_tracking_header + missing_digits + search_tracking_tail
            # get sku and qty
            parts = content.split('SKU: </strong>')
            for i in range(1, len(parts)):
                sku = parts[i][:7]
                # TODO in case qty is not 1
                qty = 1
                if sku not in item_counter[zip]:
                    item_counter[zip][sku] = {}
                    item_counter[zip][sku]['qty'] = 0
                    item_counter[zip][sku]['trackings'] = []
                item_counter[zip][sku]['qty'] += qty
                item_counter[zip][sku]['trackings'].append(tracking)
                if order_number not in order_counter[zip]:
                    order_counter[zip][order_number] = {}
                if sku in order_counter[zip][order_number]:
                    order_counter[zip][order_number][sku]['qty'] += qty
                    order_counter[zip][order_number][sku]['trackings'].append(tracking)
                else:
                    order_counter[zip][order_number][sku] = {}
                    order_counter[zip][order_number][sku]['qty'] = qty
                    order_counter[zip][order_number][sku]['trackings'] = [tracking]
        else:
            continue
    return item_counter, order_counter  # get confirmations and calculate total amout

def get_order_confirmations(emails, canceled_orders=[]):
    order_counter = {}  # {zip:{order# : {item: {qty:0, trackings:[]}}}
    item_counter = {}  # {zip:{item# : {qty:0, trackings:[]}}}
    for email in emails:
        subject = email.subject
        if not subject:
            continue
        if "We've received your order #BBY01-" in subject:
            order_number = subject.split('#BBY01-')[1][:12]
            if order_number in canceled_orders:
                continue
            content = str(email.parsed_email).split('ORDER SUMMARY')[0]
            # get sku and qty
            parts = content.split('SKU: </strong>')
            for i in range(1, len(parts)):
                # decide if it is a software
                if '$0.00' in parts[i]:
                    continue
                sku = parts[i][:7]
                # TODO in case qty is not 1
                qty = 1
                previous_zip = None
                for zip in zips:
                    zip_flag = False
                    if zip in parts[i]:
                        zip_flag = True
                        previous_zip = zip
                        if not zip in order_counter:
                            order_counter[zip] = {}
                        if not zip in item_counter:
                            item_counter[zip] = {}
                        break
                # There is a bug in email
                if not zip_flag:
                    zip = previous_zip
                if sku not in item_counter[zip]:
                    item_counter[zip][sku] = {}
                    item_counter[zip][sku]['qty'] = 0
                item_counter[zip][sku]['qty'] += qty
                if order_number not in order_counter[zip]:
                    order_counter[zip][order_number] = {}
                if sku in order_counter[zip][order_number]:
                    order_counter[zip][order_number][sku]['qty'] += qty
                else:
                    order_counter[zip][order_number][sku] = {}
                    order_counter[zip][order_number][sku]['qty'] = qty
        else:
            continue
    return item_counter, order_counter


def get_canceled_orders(emails):
    canceled_orders = []
    for email in emails:
        subject = email.subject
        if not subject:
            continue
        if "Order BBY01-" in subject and ('Your order has been canceled' in subject or 'Item(s) canceled' in subject):
            order_number = subject.split('Order BBY01-')[1][:12]
            canceled_orders.append(order_number)
    return canceled_orders


if __name__ == '__main__':
    error_orders = []
    g_account = None
    g_account = account(username, password)
    emails = g_account.inbox(start=0, amount=2000, date='11/20/2017')
    shipped_item_counter, shipped_order_counter = get_trackings(emails)
    canceled_orders = get_canceled_orders(emails)
    item_counter, order_counter = get_order_confirmations(emails, canceled_orders)

    for zip in zips:
        if zip not in item_counter:
            continue
        print zip
        for sku in item_counter[zip]:
            if zip not in shipped_item_counter or sku not in shipped_item_counter[zip]:
                shipped_qty = 0
                trackings = []
            else:
                shipped_qty = shipped_item_counter[zip][sku]['qty']
                trackings = shipped_item_counter[zip][sku]['trackings']
            print sku
            print 'qty: ', item_counter[zip][sku]['qty']
            print 'shipped qty: ', shipped_qty
            print trackings
            print '\n\n'

        if zip in shipped_order_counter:
            for order_number in shipped_order_counter[zip]:
                if order_number not in order_counter[zip]:
                    error_orders.append(order_number)
                    continue
                for sku in shipped_order_counter[zip][order_number]:
                    shipped_qty = shipped_order_counter[zip][order_number][sku]['qty']
                    order_counter[zip][order_number][sku]['qty'] -= shipped_qty

        for order_number in order_counter[zip]:
            flag = True
            for sku in order_counter[zip][order_number]:
                if order_counter[zip][order_number][sku]['qty'] != 0:
                    if flag:
                        print '-------split line------\n'
                        print 'Order number:', order_number
                        flag = False
                    print sku
                    print 'qty: ', order_counter[zip][order_number][sku]['qty']
                    print '\n'

    print 'These Orders Have Problems, check manually!!!', error_orders
    print 'These Orders got canceled, check manually!!!', canceled_orders
