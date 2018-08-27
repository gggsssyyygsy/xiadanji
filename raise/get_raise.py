#!/usr/bin/env python  
# -*- coding: UTF-8 -*-  
   
from email.mime.multipart import MIMEMultipart  
from email.mime.base import MIMEBase  
from email.mime.text import MIMEText  
   
# python 2.3.*: email.Utils email.Encoders  
from email.utils import COMMASPACE,formatdate  
from email import encoders  

import subprocess

import os 
import smtplib 
import requests
import bs4
import time
import datetime

#URL现在是按价格降序排列
brand_dict = {"best-buy":[98, 5], "sephora":[90, 7], "saks-fifth-avenue":[450, 10], "nordstrom":[93,7]}

sleep_time = 5 
#to_list = ['shushuz2@outlook.com','goodluckday2@icloud.com', 'jcaxxq1@gmail.com', 'gucasuw@gmail.com', 'wangpeicivil@gmail.com','lc890213@gmail.com', 'gusiyuan090840@gmail.com']
#to_list = ['jcaxxq1@gmail.com', 'wangpeicivil@gmail.com']
to_list = ['gusiyuan090840@gmail.com']
def main(url, price_bar, percentage_bar):
    r = requests.get(url)
    #print r.status_code
    #print r.text
    soup = bs4.BeautifulSoup(r.text)
    #print soup.prettify()
    #print soup.ul
    flag = 0
    percentage = 0
    price = 0
    for line in soup.find_all("td"):
        if "%" in str(line):
            flag = 1
            raw_percentage = line.contents
            percentage = float(str(raw_percentage[0])[:-1])
            #print percentage
    
        elif "$" in str(line) and flag == 1 and line.strong:
            flag = 0
            raw_price = line.strong.contents
            processed_price = str(raw_price[0]).strip()[1:]
            price = float(''.join(processed_price.split(',')))
            #print price
            #print line
            #exit()
            if price >= price_bar and percentage >= percentage_bar:
                return price, percentage
	    #elif price >= price_bar2 and percentage >= percentage_bar2:
	    #    return price, percentage
    return 0, 0

def email_notification(brand, price, percentage):
    subject = "{} Raise Discount Gift Card Notification!!".format(brand)
    text = "price: {}\n percentage: {}".format(price, percentage)
    kevin_send_gmail(subject, text)

def error_email(e):
    subject = "Raise code error!!!"
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

def loadConfig(filename):
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


def popup_notification(brand, price, percentage):
    subject = "{} Raise Discount Gift Card Notification!!".format(brand)
    text = "price: {}\n percentage: {}".format(price, percentage)
    
    try:
        applescript = '''display dialog "{}" with title "{}"'''.format(text, subject)
    except Exception as e:
        print e
        exit()

    print applescript, subject, text
    
    subprocess.call("osascript -e '{}'".format(applescript), shell=True)

last_price = 0
last_percentage = 0
last_e = ''
log_dict = {}
for brand in brand_dict:
    url = 'https://www.raise.com/buy-{}-gift-cards?value_sort=desc'.format(brand)
    price_bar = brand_dict[brand][0]
    percentage_bar = brand_dict[brand][1]
    log_dict[brand] = [last_price, last_percentage, url, price_bar, percentage_bar]

while 1:
    try:
        for brand in log_dict:
            url = log_dict[brand][2]
            price_bar = log_dict[brand][3]
            percentage_bar = log_dict[brand][4]
            price, percentage = main(url, price_bar, percentage_bar)
            if price != 0 and percentage != 0:
                #print price, percentage
                #send email notification
                last_price = log_dict[brand][0]
                last_percentage = log_dict[brand][1]
                if price != last_price or percentage != last_percentage:
                    last_price = price
                    last_percentage = percentage
                    log_dict[brand][0] = last_price
                    log_dict[brand][1] = last_percentage
                    popup_notification(brand, price, percentage)
                    email_notification(brand ,price, percentage)
            #print datetime.datetime.now(), price, percentage
	    time.sleep(sleep_time)
    except Exception as e:
        #send error email notification
        if e != last_e and str(e).strip() != "HTTPSConnectionPool(host='www.raise.com', port=443): Max retries exceeded with url: /buy-target-gift-cards?page=1&per=25 (Caused by <class 'socket.error'>: [Errno 110] Connection timed out)":
            #error_email(str(e))
            last_e = e
            print e
        time.sleep(sleep_time)
