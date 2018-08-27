from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
   
# python 2.3.*: email.Utils email.Encoders  
from email.utils import COMMASPACE,formatdate  
from email import encoders  
   
import os 
import smtplib 
import requests
import bs4
import time
import datetime
import simplejson as json

sleep_time = 5 
price_bar1 = 10
price_bar2 = 10
percentage_bar1 = 1
percentage_bar2 = 1
brand = "best-buy"
url = 'https://www.abcgiftcards.com/buy-gift-cards/discount-{}-cards/'.format(brand)
#url = 'https://www.cardcash.com/buy-gift-cards/discount-{}-cards/'.format(brand)

def main():
    r = requests.get(url)
    #print r.status_code
    #print r.text
    flag = 0
    percentage = 0
    price = 0
    useful_data = r.text.split('data: [{')[1].split('}],')[0]
    useful_data = "[{" + useful_data + "}]"
    #print useful_data
    l = json.loads(useful_data)
    for item in l:
        card_type = item['card_type']        
        percentage = item['percent']
        price = item['value']
        if price >= price_bar1 and percentage >= percentage_bar1:
            return price, percentage
	elif price >= price_bar2 and percentage >= percentage_bar2:
	    return price, percentage
    return 0, 0

def email_notification(brand, price, percentage):
    subject = "{} ABC Discount Gift Card Notification!!".format(brand)
    text = "price: {}\n percentage: {}".format(price, percentage)
    kevin_send_gmail(subject, text)

def error_email(e):
    subject = "ABC code error!!!"
    text = e
    kevin_send_gmail(subject, text)

#server['name'], server['user'], server['password']  
def send_mail(server, fro, to, subject, text, files=[]):   
    assert type(server) == dict   
    assert type(to) == list   
    assert type(files) == list   
   
    msg = MIMEMultipart()   
    msg['From'] = fro   
    msg['Subject'] = subject   
    msg['To'] = COMMASPACE.join(to) #COMMASPACE==', '   
    msg['Date'] = formatdate(localtime=True)   
    msg.attach(MIMEText(text))   
   
    for file in files:   
        part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data   
        part.set_payload(open(file, 'rb'.read()))   
        encoders.encode_base64(part)   
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))   
        msg.attach(part)   
   
    smtp = smtplib.SMTP(timeout = 20)
    smtp.connect(server['name'],587)  
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(server['user'], server['password'])   
    smtp.sendmail(fro, to, msg.as_string())   
    smtp.close() 

def def loadConfig(filename):
    ''' load your config.csv file
      the file should contain username, password in each line
      make sure the file is under the same directory '''
    username = []
    password = []
    f = open(filename, 'rb')
    reader = csv.reader(f)
    for row in reader:
        username.append(row[0].strip())
        password.append(row[1].strip())
    f.close()
    return username, password


def kevin_send_gmail(subject, text, files=[]):
    username, password = loadConfig("config.csv")
    server = {}
    server['name'] = 'smtp.gmail.com'
    server['user'] = username
    server['password'] = password
    fro = server['user']# + '@gmail.com'
    to = to_list# + '@gmail.com'
    send_mail(server, fro, to, subject, text, files)

last_price = 0
last_percentage = 0
last_e = ''

while 1:
    try:
        price, percentage = main()
        if price != 0 and percentage != 0:
            #print price, percentage
            #send email notification
            if price != last_price or percentage != last_percentage:
                last_price = price
                last_percentage = percentage
                email_notification(brand ,price, percentage)
        #print datetime.datetime.now(),price, percentage      
	time.sleep(sleep_time)
    except Exception as e:
        #send error email notification
        if not e == last_e and str(e).strip() != "HTTPSConnectionPool(host='www.cardcash.com', port=443): Max retries exceeded with url: /buy-gift-cards/discount-target-cards/ (Caused by <class 'socket.error'>: [Errno 101] Network is unreachable)" and not str(e) == 'list index out of range':
            error_email(str(e))
            last_e = e
        time.sleep(sleep_time)

