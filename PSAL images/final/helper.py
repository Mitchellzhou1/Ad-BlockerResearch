import threading
import time
from time import sleep
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server
from selenium.webdriver.common.by import By
import os, requests, sys
from bs4 import BeautifulSoup
import tldextract
import re
from selenium.webdriver.common.action_chains import ActionChains



class Driver:
    def __init__(self):
        self.driver = None
        self.proxy = None
        self.server = None

        self.image_urls = []

    def initialize(self, extn):
        print("initializing", extn)
        server = Server("/home/mitch/work/pes/browsermob-proxy/bin/browsermob-proxy")
        server.start()
        proxy = server.create_proxy()
        # proxy = server.create_proxy(params={'port': port})

        options = Options()
        if 'control' not in extn:
            options.add_argument(f"/home/mitch/Desktop/Ad-BlockerResearch/Extensions/{extn}.crx")

        options.add_argument("start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-animations")
        options.add_argument("--disable-web-animations")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        options.add_argument("--disable-features=AudioServiceOutOfProcess")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

        options.add_argument(f'--proxy-server={proxy.proxy}')

        driver = webdriver.Chrome(options=options)
        sleep(3)
        windows = driver.window_handles[::-1]
        for window in windows:
            if len(driver.window_handles) <= 1:
                break
            try:
                driver.switch_to.window(window)
                driver.close()
            except Exception as e:
                print(e)
                return 0

        self.driver = driver
        self.server = server
        self.proxy = proxy





def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
