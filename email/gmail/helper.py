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
