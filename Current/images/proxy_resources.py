from urllib.parse import urlparse

import requests
#from browsermobproxy import Server
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

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

start_time = time.time()

from functions import *


def main(num_tries, args_lst, display_num, server, port, all_resources, blacklist, inverse_lookup, regular_lookup,
         extn):
    print("port with url", port, args_lst[0])

    # Start X
    data_usage = {}
    contacted_urls = []

    # display number
    os.environ['DISPLAY'] = f":{display_num}"

    # proxy
    proxy = server.create_proxy(params={'port': port})

    # Initialize Selenium
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--proxy-server={0}".format(proxy.proxy))
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-animations")
    options.add_argument("--disable-web-animations")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=AudioServiceOutOfProcess")

    # options.add_argument("auto-open-devtools-for-tabs")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    # options.add_extension("/home/mitch/work/pes/measurements/extensions/extn_crx/adblock.crx")
    # options.binary_location = "/home/ritik/work/pes/chrome_113/chrome"
    # options.binary_location = "/usr/bin/google-chrome"
    # options.binary_location = "/home/ritik/work/pes/chrome_113/chrome"
    if args_lst[-1] != "":
        # always adding the path of the extension at the end
        try:
            options.add_extension(args_lst[-1])
        except Exception as e:
            print(str(e).split("\n")[0])
    # Initialize service
    # service = Service(executable_path='/usr/local/bin/chromedriver')

    driver = ''
    for i in range(num_tries):
        try:
            # Launch Chrome and install our extension for getting HARs
            driver = webdriver.Chrome(options=options)
            # time.sleep(5)

            # element = driver.find_element(By.XPATH, "//ui-button[@type='success']")
            # element.click()

            # time.sleep(2)

            driver.set_page_load_timeout(args_lst[1])
            time.sleep(4)

            if extn == 'adblock':
                time.sleep(15)
            elif extn == 'ghostery':
                windows = self.driver.window_handles
                for window in windows:
                    try:
                        self.driver.switch_to.window(window)
                        url_start = self.driver.current_url[:16]
                        if url_start == 'chrome-extension':
                            element = self.driver.find_element(By.XPATH, "//ui-button[@type='success']")
                            element.click()
                            time.sleep(2)
                            break
                    except Exception as e:
                        print('ghostery', 1, e)
                        return 0

            # driver.get('chrome-extension://mlomiejdfkolichcflejclcbmpeaniij/app/templates/onboarding.html')
            # time.sleep(12)

            # element = driver.find_element(By.XPATH, "//ui-button[@type='success']")
            # element.click()

            # time.sleep(5)
            # print(2222222222222222222222)

            # Create a new HAR with the following options
            proxy.new_har("example", options={'captureHeaders': True, 'captureContent': True})

            # Use Selenium to navigate to a webpage
            # valid = 0
            # i += 1
            website = args_lst[0]

            print("website: ", website)
            driver.get(website)
            wait_until_loaded(driver, args_lst[1])
            time.sleep(2)

            curr_scroll_position = -1
            curr_time = time.time()
            while True:
                # Define the scroll step size
                scroll_step = 50  # Adjust this value to control the scroll speed
                # Get the current scroll position
                scroll_position = driver.execute_script("return window.pageYOffset;")
                # Check if we've reached the bottom
                if curr_scroll_position == scroll_position:
                    break
                else:
                    curr_scroll_position = scroll_position

                # Scroll down by the step size
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")

                # Wait for a bit (this controls the scroll speed indirectly)
                time.sleep(0.1)  # Adjust this value to control the scroll speed
                if time.time() - curr_time >= 45:
                    break
            # valid += 1

            time.sleep(5)
            # Collect HAR data
            result = proxy.har

            # Analyze HAR data (this is a simplified example)
            # total_size = 0
            # print(result)
            data_usage[i] = result['log']['entries']
            print(f"{args_lst[0]} --- {len(data_usage[i])}")
        except Exception as e:
            print(1, e, args_lst[0])

        # Stop Selenium and BrowserMob Proxy
        if driver != '':
            driver.quit()
            time.sleep(2)

    try:
        all_resources[args_lst[0]] = filter_packets(args_lst[0], data_usage[0], blacklist, inverse_lookup,
                                                    regular_lookup).copy()

        # pid = int(get_pid_by_port(port))
        # os.kill(pid, signal.SIGTERM)
    except Exception as e:
        print(2, args_lst[0], e, data_usage.keys())
    # return data_usage


SIZE = 10
if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    # parser.add_argument('website')
    parser.add_argument('--timeout', type=int, default=60)
    # parser.add_argument('--extensions')
    parser.add_argument('--extensions-wait', type=int, default=10)
    args = parser.parse_args()

    manager = multiprocessing.Manager()

    # websites = ast.literal_eval(args.website)
    # websites = [args.website]
    # websites = ['https://www.geeksforgeeks.org/graph-and-its-representations/']

    websites = [
        "uxmatters.com",
        "mrdonn.org",
        "velocityhub.com",
        'amazon.com/',
        'en.wikipedia.org/wiki/Main_Page',
        'microsoft.com/en-us',
        'office.com',
        'weather.com',
        'openai.com',
        'bing.com',
        'duckgo.com',
        'nytimes.com',
        'twitch.tv',
        'imdb.com',
        'qq.com',
        'globo.com',
        'ebay.com',
        'foxnews.com',
        'instructure.com',
        'walmart.com',
        'indeed.com',
        'paypal.com/us/home',
        'accuweather.com',
        'pinterest.com',
        'bbc.com',
        'homedepot.com',
        'breitbart.com',
        'github.com'
    ]

    # website_dict = json.load(open('../../adblock_detect/inner_pages_custom_break.json', 'r'))
    # for key in website_dict:
    #     websites.append(website_dict[key][0])
    # websites = random.sample(websites, 1500)
    website_chunks = list(divide_chunks(websites, SIZE))

    print(f'data --- {websites}')

    # Initialize BrowserMob Proxy
    server = Server("/home/mitch/work/pes/browsermob-proxy/bin/browsermob-proxy")
    server.start()
    # proxy = server.create_proxy()

    data_dict = {}
    # extensions_path = pathlib.Path("/home/seluser/measure/extensions/extn_crx")
    # extensions_path = pathlib.Path("/home/mitch/work/pes/measurements/extensions/extn_crx")
    extensions_path = "/home/mitch/work/pes/measurements/extensions/extn_crx/"

    extension = 0

    name = str(extension)

    blacklist, inverse_lookup, regular_lookup = initialize_blacklists(Trie(), Trie())

    if extension:
        for extn in extensions_configurations:
            new_args = args_lst
            new_args.append(extn)
            if extn != "":
                for extension in args_lst[-1].split(","):
                    matches = list(extensions_path.glob("{}*.crx".format(extension)))
                    if matches and len(matches) == 1:
                        new_args.append(str(matches[0]))
                        # options.add_extension(str(matches[0]))
                        # extn = extension
                    else:
                        print(f"{args_lst[-1]} - Extension not found", file=sys.stderr)
                        sys.exit(1)
            ret, contacted_urls = main(3, new_args, proxy)
            if extn == "":
                data_dict[fname] = [ret, contacted_urls]
            else:
                data_dict[extn] = [ret, contacted_urls]

    else:
        extensions = ["control", "ublock", "adblock", "privacy-badger"]
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
