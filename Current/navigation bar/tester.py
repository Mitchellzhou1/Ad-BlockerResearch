from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse
from time import *
from bs4 import BeautifulSoup
import requests

import pyautogui
import signal
from tranco import Tranco


t = Tranco(cache=True, cache_dir='.tranco')
latest_list = t.list()
sites = latest_list.top(10000)
for i in sites:
    print(i)




# fastly.net: this website is broken
# yahoo.com: going on it on crawler is different then on browser
#  bit.ly   Message: no such execution context
# msn.com
# yandex.net --robot detection

#naver.com: says its redirect
#cnn.com
#golbo.com
#softonic.com
