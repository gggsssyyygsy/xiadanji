# helper files for target automation

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import csv
import time
from random import choice
import string


def getDriver(browser):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1440,900")
    if browser.lower() == 'firefox':
        driver = webdriver.Firefox()
    elif browser.lower() == 'chrome':
        driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
    elif browser.lower() == 'chrome_linux':
        driver = webdriver.Chrome('./chromedriver_linux64', chrome_options=chrome_options)
    elif browser.lower() in ('phantomjs', 'headless'):
        driver = webdriver.PhantomJS()
    else:
        print "WARNING: browser selection not valid, use PhantomJS as default"
        driver = webdriver.PhantomJS()
    # driver.maximize_window()
    # driver.set_window_size(1440, 900)
    # driver.set_window_position(0, 0)
    return driver


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


def loadGiftcards(filename):
    ''' load your tgc.csv file
      the file should contain username, password in each line
      make sure the file is under the same directory '''
    giftcards = []
    f = open(filename, 'rb')
    reader = csv.reader(f)
    for row in reader:
        giftcards.append((row[0].strip(), row[1].strip(), float(row[2].strip())))
    f.close()
    return set(giftcards)


def closeFeedback(driver):
    try:
        driver.find_element_by_class_name("srCloseBtn").click()
    except:
        try:
            driver.find_element_by_class_name("fsrCloseBtn").click()
        except:
            pass
    time.sleep(1)


def targetLogIn(driver, usr, pwd):
    signinTabID = "js-toggleRightNavLg"
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id(signinTabID)).click()
    time.sleep(1)
    signinFieldID = "rightNav-signIn"
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id(signinFieldID)).click()
    time.sleep(1)
    emailFieldID = "username"
    passFieldID = "password"
    loginBtnID = "login"
    # WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(emailFieldID)).clear()
    raw_input("Press Enter to continue...")
    return
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id(emailFieldID)).send_keys(usr[:-1])
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id(emailFieldID)).send_keys(usr[-1:])
    # WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(passFieldID)).clear()
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id(passFieldID)).send_keys(pwd)
    time.sleep(3)
    WebDriverWait(driver, 20).until(lambda driver: driver.find_element_by_id(loginBtnID)).click()
    time.sleep(5)


def targetLogOut(driver):
    logoutBtnID = "iNavLogOutButton"
    # WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id(logoutBtnID)).click()
    WebDriverWait(driver, 3).until(lambda driver: find_elements_by_xpath("//*[contains(text(), 'Log Out')]")).click()
