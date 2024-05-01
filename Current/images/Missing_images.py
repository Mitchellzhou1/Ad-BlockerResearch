from urllib.parse import urlparse

import requests
from browsermobproxy import Server
import tldextract
import time
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
import threading

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

start_time = time.time()

from functions import *

def initialize_proxy():
    server = Server("/home/mitch/work/pes/browsermob-proxy/bin/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()
    return proxy

def initialize_selenium(extn, proxy, num_tries=3):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-animations")
    options.add_argument("--disable-web-animations")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=AudioServiceOutOfProcess")
    options.add_argument("--proxy-server={}".format(proxy.proxy))

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


def main():
    ...


SIZE = 10
extensions = ["control", "ublock"]
SIZE = (SIZE % len(extensions)) * len(extensions)
if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument('website')
    parser.add_argument('--timeout', type=int, default=60)
    # parser.add_argument('--extensions')
    parser.add_argument('--extensions-wait', type=int, default=10)
    args = parser.parse_args()

    manager = multiprocessing.Manager()

    websites = [
        "uxmatters.com",
        "mrdonn.org",
        "velocityhub.com",
        'amazon.com/',
        'en.wikipedia.org/wiki/Main_Page'
    ]

    website_chunks = list(divide_chunks(websites, SIZE))

    # keeps track of all the drivers and their associated proxies
    driver_dictionary = {}
    # stores all the missing images
    data_dictionary = {}


    print(f'data --- {websites}')

    threads = []
    for website in websites:
        for extn in extensions:
            driver_dictionary[extn] = {}
            driver_dictionary[extn][website] = {'driver': None,
                                                'proxy': None,
                                                'loaded': False
                                                }
        for _ in range(SIZE):
            thread = threading.Thread(target=main, args=website)
            threads.append(thread)
            thread.start()




    # Initialize BrowserMob Proxy
    server = Server("/home/mitch/work/pes/browsermob-proxy/bin/browsermob-proxy")
    server.start()

    # extensions = ["control", "ublock", "adblock", "privacy-badger"]
    extensions = ["control", "ublock"]
    extensions_dictionary = {}

    # generates extensions dictionary with just the ad blocker extension names
    # intializing the dictionary
    for extension in extensions:
        extensions_dictionary[extension] = None

    for extension in extensions:
        all_resources = manager.dict()
        # if the json data already exits, just load it.
        # USED FOR TESTING!!!!!!
        # if file_exists(f"json/{extension}.json"):
        #     with open(f"json/{extension}.json", 'r') as file:
        #         json_data = file.read()
        #     extensions_dictionary[extension] = json.loads(json_data)
        #     file.close()
        #     continue

        if extension != "control":
            name = extensions_path + extension + ".crx"
        else:
            name = ""
        for chunk in website_chunks:
            # website = "http://" + website
            jobs = []
            vdisplay = Display(visible=False, size=(1920, 1280))
            vdisplay.start()
            display = vdisplay.display

            for i, website in enumerate(chunk):
                website = "http://" + website
                try:
                    fname = './data/' + website.split('//')[1].split('/')[0]
                    extn = fname
                    args_lst = [website, args.timeout]
                    new_args = args_lst
                    new_args.append(name)

                    port = 8181 + i
                    # ret value is the packets
                    p = multiprocessing.Process(target=main, args=(
                    1, new_args, display, server, port, all_resources, blacklist, inverse_lookup, regular_lookup,
                    extension))
                    jobs.append(p)
                    # ret = main(1, new_args, proxy)

                    # filtered_val is LIST with all the filtered packets

                    # large dictionary with all the results of each website.
                    # this should be seperate for each extension.
                    # all_resources[website] = filter_packets(website, ret, blacklist, inverse_lookup, regular_lookup).copy()

                    # write_JSON(extension, all_resources)

                    # data_dict = unfiltered and contains all the packets
                    # data_dict[fname] = ret
                    # with open(fname, 'w') as f:
                    #     json.dump(ret, f)
                    # f.close()
                except Exception as e:
                    print(e)
                    print(website)

            for job in jobs:
                job.start()

            time.sleep(5)

            for job in jobs:
                print(f"joining {job}")
                job.join(timeout=60)

                if job.is_alive():
                    job.terminate()

            time.sleep(2)
            print("-" * 50)
            print("closing open xvfb processes")
            vdisplay.stop()
            os.system('pkill Xvfb')
            print(os.system("ps aux | grep Xvfb | wc -l"))
            print("-" * 50)

            time.sleep(5)

        save_dict = {}
        for key in all_resources.keys():
            save_dict[key] = all_resources[key]
        write_JSON(extension, save_dict)
        extensions_dictionary[extension] = save_dict
        # all_resources = {}

        # once all the JSON data have been collected, compare them.
        for extension in extensions:
            extensions_dictionary[extension] = json.load(open(f'json/{extension}.json', 'r'))
            # print(extensions_dictionary["control"])
            compare_resources(extension, extensions_dictionary["control"], extensions_dictionary[extension])

    # with open(fname, 'w') as f:
    #     json.dump(data_dict, f)
    # f.close()

    print("Finished Collecting on All Sites!")
    server.stop()
    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")
