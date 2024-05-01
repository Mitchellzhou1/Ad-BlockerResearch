from urllib.parse import urlparse

import requests
import time
# from adblockparser import *
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import time
# import threading
import os
from datetime import datetime
import ast
import multiprocessing
import random
import signal

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

start_time = time.time()

# from functions import *


def initialize(extn, num_tries=3):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-animations")
    options.add_argument("--disable-web-animations")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=AudioServiceOutOfProcess")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    # options.add_extension(f'/home/mitch/work/pes/measurements/extensions/extn_crx/')
    if extn != 'control':
        options.add_extension(f'/home/character/Desktop/Ad-BlockerResearch/Extensions/extn_crx/{extn}.crx')

    for i in range(num_tries):
        # Launch Chrome and install our extension for getting HARs
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(45)

        time.sleep(15)

        windows = driver.window_handles
        for window in windows[::-1]:
            try:
                driver.switch_to.window(window)
                if len(driver.window_handles) == 1:
                    continue
                driver.close()
            except Exception as e:
                print("SOMETHING WENT WRONG")
                print(e)
                continue
        return driver


driver = initialize('ublock')
driver.get("https://mrdonn.org/")
while 1:
    1