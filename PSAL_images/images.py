import threading
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server
import os, requests
import multiprocessing
from helpers import *

# Function to initialize Chrome instances
def initialize_chrome(extn, url, packet_dict, ss_flag=False):
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

    proxy.new_har("initial", options={'captureHeaders': True, 'captureContent': True})
    driver.get(url)
    wait_until_loaded(driver)
    sleep(3)

    images = get_image_resources(proxy.har)
    packet_dict[extn] = images

    proxy.close()
    server.stop()
    if ss_flag:
        control_data_urls = get_image_resources(packet_dict['control'])
        for extn in extensions:
            if extn == 'control':
                continue
            extn_data_urls = get_image_resources(packet_dict[extn])
            compare_resources(url, control_data, network_data, extn, control_driver, extn_driver)




def run_same_time(target, args):
    process_list = []
    target = getattr(sys.modules[__name__], target)
    for i, arg in enumerate(args):
        process_list.append(multiprocessing.Process(target=target, args=arg))
        process_list[i].start()
    for i in range(len(args)):
        process_list[i].join()


def get_url(driver, url):
    driver.get(url)


def filter_site(url, data):
    run_same_time('initialize_chrome', [('control-test-1', url, data), ('control-test-2', url, data)])
    images1 = data['control-test-1']
    images2 = data['control-test-2']
    for key in data.keys():
        print(key, data[key])

    return images1 == images2


def run(url, json_data, process_dict):
    """
    creates two control browsers. These will check to see if the page is actually measurable
    some websites are too difficult to measure for missing pictures because the images are changing too much.
    if both controls browsers have no missing images between them, then if I launch the browsers with the extensions
    and I find that there are missing images, then the missing images are caused by the extensions and not the website.
    """
    # opening two control browsers and testing to see if we can measure it
    packet_dict = multiprocessing.Manager().dict()
    driver_dict = {}

    if filter_site(url, packet_dict):
        args = []
        # launch the drivers
        for extn in extensions:
            args.append((extn, url, packet_dict, driver_dict))
        run_same_time('initialize_chrome', args)

        args = []




            # website_drivers[url][extn][0].quit()
            # website_drivers[url][extn][1].close()
            # website_drivers[url][extn][2].stop()
            # website_drivers[url].pop(extn)

        website_drivers.pop(url)




websites = [
    # "https://www.example.com",
    "https://www.google.com",
    # "https://www.wikipedia.org",
    # "https://www.github.com"
]

extensions = [
    "control",
    "ublock",
    # "adblock",
    # "privacy-badger",
]

SIZE = 4
chunks = list(divide_chunks(websites, SIZE))
manager = multiprocessing.Manager()
json_data_dict = manager.dict()
process_dict = {}

for chunk in chunks:
    for website in chunk:
        process_dict[website] = {
            'control-scanner1': multiprocessing.Process(target=run, args=(website, json_data_dict, process_dict)),
            'control-scanner2': multiprocessing.Process(target=run, args=(website, json_data_dict, process_dict)),
        }
        for extn in extensions:
            process_dict[website][extn] = multiprocessing.Process(target=run, args=(website, json_data_dict, process_dict))

    for website in chunks:
        process_dict[website]['control-scanner1'].start()
        process_dict[website]['control-scanner2'].start()

    for website in chunks:
        process_dict[website]['control-scanner1'].join()
        process_dict[website]['control-scanner2'].join()


"""

NOT USED FUNCTIONS

"""



