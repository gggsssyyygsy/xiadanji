#!/usr/bin/env python

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time
from helper import loadConfig, loadGiftcards, targetLogIn, targetLogOut, getDriver

target_website = "https://www.target.com"
target_cart = "https://www.target.com/co-cart"
target_checkout = "https://www.target.com/co-payment"
item_urls = [
    "https://www.target.com/p/amazon-fire-tv-stick-with-alexa-voice-remote/-/A-51760055#lnk=sametab"
]
pu_url = "https://www.target.com/p/maruchan-instant-shrimp-lunch-soup-3oz/-/A-47111274#lnk=sametab"


def loginTest(username, password, giftcards, outputlog=True, browser="PhantomJS"):
    '''
    orig_stdout = sys.stdout  # re-route output
    logfile = None
    if outputlog:
        # use current time in log file name
        logfilename = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        logfilename = logfilename.replace(':', '_') + ".log"
        logfile = open('../tmp/' + logfilename, 'w+')
        sys.stdout = logfile
    # input error handle
    if username == [] or password == [] or len(username) != len(password):
        print "username array does not have the same length as password array..."
        # close log file
        if outputlog:
            sys.stdout = orig_stdout
            logfile.close()
        return
    '''
    driver = getDriver(browser)
    begintime = time.time()

    eachbegintime = time.time()
    print "--------------------------------------------------------------"
    print "ID:", username
    # just in case network connection is broken
    try:
        driver.get(target_website)
    except:
        print "website is not available..."
        if outputlog:
            sys.stdout = orig_stdout
            logfile.close()  # close log file
        return

        # manual now

    targetLogIn(driver, username, password)
    # place orders
    all_used_giftcards = []
    while True:
        #'''
        for item_url in item_urls:
            driver.get(item_url)
            element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('page-meta'))
            driver.execute_script("arguments[0].click();", element)
            el = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('sbc-quantity-default'))
            options = WebDriverWait(el, 20).until(lambda el: el.find_elements_by_tag_name('option'))
            max_option = options[-1]
            max_option.click()
            time.sleep(1)
            add_to_cart_button = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath("//*[@class='sbc-add-to-cart btn btn-primary btn-lg btn-block sbc-selected']"))
            driver.execute_script("arguments[0].click();", add_to_cart_button)
            time.sleep(5)
        #'''
        #'''
        #add pu item:
        driver.get(pu_url)
        element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('page-meta'))
        driver.execute_script("arguments[0].click();", element)
        add_to_cart_button = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_xpath(
            "//*[@class='sbc-add-to-cart btn btn-primary btn-lg btn-block sbc-selected']"))
        driver.execute_script("arguments[0].click();", add_to_cart_button)
        time.sleep(5)
        #'''

        # cart page, choose pu  class: custom-radio radio-reference form--control js-fulfillmentRadioBtn js-shipRadio
        driver.get(target_cart)
        time.sleep(5)
        element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('page-meta'))
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        pu_box = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_class_name('puisCheckBox'))
        pu_check = pu_box.find_element_by_xpath("//input[@class='custom-radio form--control puis_radio js-fulfillmentRadioBtn js-puisRadio']")
        #if not pu_check.is_selected():
        driver.execute_script("arguments[0].click();", pu_check)
        raw_input("Press Enter to continue...")
        ready_button = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('checkout-link'))
        driver.execute_script("arguments[0].click();", ready_button)
        time.sleep(5)

        # checkout page
        driver.get(target_checkout)
        time.sleep(5)
        element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('page-meta'))
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        # get total
        remain_total = WebDriverWait(driver, 20).until(lambda driver: driver.find_elements_by_xpath("//*[@class='h-float-right ']"))[0].text
        remain_total = round(float(remain_total[1:]),2)
        # apply gc
        used_giftcards = set()
        error_giftcards = set()
        time.sleep(1)
        element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('creditCard'))
        if element.is_selected():
            driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('giftCard'))
        if not element.is_selected():
            driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        giftcards = list(giftcards)
        for i in range(0, len(giftcards)):
            number = giftcards[i][0]
            pin = giftcards[i][1]
            balance = giftcards[i][2]
            for digit in number:
                WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('giftcard_number')).send_keys(digit)
                time.sleep(0.05)
            for digit in pin:
                WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('access_number')).send_keys(digit)
                time.sleep(0.05)
            time.sleep(2)
            # TODO Here we may have bad gift cards.
            elements = driver.find_elements_by_xpath("//*[@class='h-float-right']")
            for element in elements:
                if element.text.strip():
                    new_remain_total = element.text.strip()
            new_remain_total = round(float(new_remain_total[1:]),2)
            if not new_remain_total:
                balance -= remain_total
                giftcards[i] = (number, pin, balance)
                break
            else:
                if new_remain_total != remain_total - balance:
                    print '!!!!!!wrong balance!!!!!', giftcards[i]
                used_giftcards.add((number, pin, balance))
                all_used_giftcards.append((number, pin, 0))
                remain_total = new_remain_total
        if new_remain_total:
            exit()

        # review
        time.sleep(5)
        element = WebDriverWait(driver, 30).until(lambda driver: driver.find_element_by_id('payment_save'))
        time.sleep(1)
        driver.execute_script("arguments[0].click();", element)
        time.sleep(5)
        # go to cart
        while True:
            driver.get(target_cart)
            time.sleep(5)
            element = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('page-meta'))
            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            ready_button = WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id('checkout-link'))
            driver.execute_script("arguments[0].click();", ready_button)
            time.sleep(5)
            try:
                element = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('order-submitBm'))
                time.sleep(1)
                driver.execute_script("arguments[0].click();", element)
                time.sleep(5)
            except:
                driver.get(target_checkout)
                time.sleep(5)
            break
        giftcards = set(giftcards)
        giftcards -= used_giftcards
        eachendtime = time.time()
        print "Time used: %0.2f seconds" % (eachendtime - eachbegintime)
        print "remained gc--------------------------------------------------------------"
        for giftcard in giftcards:
            print giftcard
        print "used gc--------------------------------------------------------------"
        for giftcard in used_giftcards:
            print giftcard

    endtime = time.time()
    # print summary
    print "--------------------------------------------------------------"
    print "** Summary **"
    print "Total time used: %0.2f seconds" % (endtime - begintime)
    print "--------------------------------------------------------------"
    print "remained gc--------------------------------------------------------------"
    for giftcard in giftcards:
        print giftcard
    print "used gc--------------------------------------------------------------"
    for giftcard in all_used_giftcards:
        print giftcard

    # close log file
    if outputlog:
        sys.stdout = orig_stdout
        logfile.close()
    # close browser
    driver.quit()


def main(argv):
    browser = 'Chrome'
    if len(argv) >= 1:
        browser = argv[0]
    username, password = loadConfig("conf/config.csv")
    giftcards = loadGiftcards("conf/tgc.csv")
    loginTest(username[0], password[0], giftcards, outputlog=True, browser=browser)


if __name__ == '__main__':
    main(sys.argv[1:])
