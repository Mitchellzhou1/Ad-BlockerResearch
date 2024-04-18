from urllib.parse import urlparse

import requests
from browsermobproxy import Server
import tldextract
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

from functions import *


def main(num_tries, args_lst, display_num, extn, url_data):
    # display number
    os.environ['DISPLAY'] = f":{display_num}"

    # Initialize Selenium
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

    options.binary_location = "/home/mitch/work/pes/chrome_113/chrome"
    # if args_lst[-1] != "":
    #     options.add_extension(args_lst[-1])

    # path_ss = '/home/ritik/work/pes/measurements/break/record_replay/proxy/ss'
    index = 0

    driver = ''
    for i in range(num_tries):
        # Launch Chrome and install our extension for getting HARs
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(args_lst[1])
        time.sleep(2)

        if extn == 'adblock':
            time.sleep(15)
        elif extn == 'ghostery':
            windows = driver.window_handles
            for window in windows:
                try:
                    driver.switch_to.window(window)
                    url_start = driver.current_url[:16]
                    if url_start == 'chrome-extension':
                        element = driver.find_element(By.XPATH, "//ui-button[@type='success']")
                        element.click()
                        time.sleep(2)
                        break
                except Exception as e:
                    print('ghostery', 1, e)
                    return 0

        for resource_url, _, _, _, content_type, _, in_blacklist in url_data:
            try:
                website = args_lst[0]
                print("website: ", website)
                driver.get(website)
                wait_until_loaded(driver, args_lst[1])
                time.sleep(2)

                # if in_blacklist:
                #     continue

                path = extract_path_from_url(resource_url)
                # Find any element that contains the resource URL in any of its attributes
                elements = driver.find_elements(By.XPATH, f"//*[@*='{resource_url}']")
                elements += driver.find_elements(By.XPATH, f"//*[@*='{path}']")

                if elements:
                    print(f"Found {len(elements)} element(s) containing the resource URL.")
                    for element in elements:
                        # Take a screenshot of each element
                        # Create the directory if it does not exist
                        if 'http' in website:
                            website = website.split('http://')[1]
                        if 'www' in website:
                            website = website.split('www.')[1]

                        path_site = f'path_ss/{extn}/{website}'
                        if not os.path.exists(path_site):
                            os.makedirs(path_site)
                        screenshot_filename = os.path.join(path_site, f"element_screenshot_{index}.png")
                        try:
                            element.screenshot(screenshot_filename)
                            print(screenshot_filename)
                            index = index + 1
                            print(f"Screenshot of element {index} saved as '{screenshot_filename}'.")

                            parent = get_parent_elem(element, 4)
                            screenshot_filename = os.path.join(path_site, f"element_screenshot_{index}.png")
                            parent.screenshot(screenshot_filename)
                            index = index + 1

                        except Exception as e:
                            print(e)

                else:
                    print("No elements containing the specified resource URL were found.")

            except Exception as e:
                print(1, e, args_lst[0])

            time.sleep(2)

        # Stop Selenium and BrowserMob Proxy
        if driver != '':
            driver.quit()
            time.sleep(2)


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

    data_dict = {}
    extensions_path = "/home/mitch/work/pes/measurements/extensions/extn_crx/"

    extension = 0

    name = str(extension)

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
            # ret, contacted_urls = main(3, new_args, proxy)
            # if extn == "":
            #     data_dict[fname] = [ret, contacted_urls]
            # else:
            #     data_dict[extn] = [ret, contacted_urls]

    else:
        # extensions = ["ublock", "privacy-badger", "adblock"]
        # extensions = ["privacy-badger", "adblock"]
        extensions = ["ublock"]
        extensions_dictionary = {}

        # generates extensions dictionary with just the ad blocker extension names
        for extension in extensions:
            extensions_dictionary[extension] = None
            url_data = json.load(open(f'json/{extension}_missing.json', 'r'))

            websites = list(url_data.keys())
            website_chunks = list(divide_chunks(websites, SIZE))

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
                    try:
                        fname = './data/' + website.split('//')[1].split('/')[0]
                        extn = fname
                        args_lst = [website, args.timeout]
                        new_args = args_lst
                        new_args.append(name)

                        image_resources = []
                        for missing in url_data[website]['missing_resources']:
                            if 'image' in missing[4]:
                                image_resources.append(missing)

                        if image_resources == []:
                            continue

                        p = multiprocessing.Process(target=main,
                                                    args=(1, new_args, display, extension, image_resources))
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
                    job.join(timeout=120)

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

    end_time = time.time()

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    print("Elapsed time:", elapsed_time, "seconds")
