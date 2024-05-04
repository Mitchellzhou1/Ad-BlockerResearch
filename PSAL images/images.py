import threading
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from browsermobproxy import Server
import os, requests
import multiprocessing
from helpers import *

# Function to initialize Chrome instances
def initialize_chrome(extn, url):
    global website_drivers, control_scanners
    print("initializing", extn)
    # server = Server("/home/mitch/work/pes/browsermob-proxy/bin/browsermob-proxy")
    # server.start()
    # proxy = server.create_proxy()
    # proxy = server.create_proxy(params={'port': port})

    # Initialize Selenium
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
    # options.add_argument("--proxy-server={0}".format(proxy.proxy))

    # options.add_argument("auto-open-devtools-for-tabs")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

    # proxy.new_har("example", options={'captureHeaders': True, 'captureContent': True})
    driver = webdriver.Chrome(options=options)
    sleep(12)
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

    server = "server"
    proxy = 'proxy'
    if extn == 'control-test':
        if control_scanners[url]['control1']:
            control_scanners[url]['control2'] = [driver, proxy, server]
        else:
            control_scanners[url]['control1'] = [driver, proxy, server]
    else:
        website_drivers[url][extn] = [driver, proxy, server]
    return driver, proxy, server


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


def filter_site(url):
    global control_scanners
    control_scanners[url] = {'control1': None,
                             'control2': None}
    run_same_time('initialize_chrome', [('control-test', url)] * 2)
    driver1, proxy1, server1 = control_scanners[url]['control1']
    driver2, proxy2, server2 = control_scanners[url]['control2']
    sleep(2)

    run_same_time('get_url', [(driver1, url), (driver2, url)])

    images1 = get_image_resources(proxy1.har)
    images2 = get_image_resources(proxy2.har)

    # delete everything (I probably don't need to do this because of garbage collection)
    driver1.quit()
    proxy1.close()
    server1.stop()

    driver2.quit()
    proxy2.close()
    server2.stop()

    control_scanners[url]['control1'] = None
    control_scanners[url]['control2'] = None

    # if there are no differences then it will return true, and we can scan the website
    return len(images1 - images2) == 0


def run(url, website_drivers, json_data):
    """
    creates two control browsers. These will check to see if the page is actually measurable
    some websites are too difficult to measure for missing pictures because the images are changing too much.
    if both controls browsers have no missing images between them, then if I launch the browsers with the extensions
    and I find that there are missing images, then the missing images are caused by the extensions and not the website.
    """
    # opening two control browsers and testing to see if we can measure it
    if filter_site(url):
        args = []

        # launch the drivers
        for extn in extensions:
            args.append((extn, url))
        run_same_time('initialize_chrome', args)

        args = []

        # load the websites are the same time
        for extn in extensions:
            args.append((website_drivers[url][extn][0], url))
        run_same_time('get_url', args)

        control_data = get_image_resources(website_drivers[url]['control'][1].har)
        control_driver = website_drivers[url]['control'][0]
        for extn in extensions:
            extn_driver = website_drivers[url][extn][0]
            if extn == 'control':
                continue
            network_data = website_drivers[url][extn][1].har
            compare_resources(url, control_data, network_data, extn, control_driver, extn_driver)


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

""" 
website_drivers structure:
website_drivers[website][extn] = {'driver': None,
                                  'proxy': None,
                                  'server': None}
                                  
website_drivers structure:
website_drivers[website][extn] = {screen_shot_name: url}
"""
website_drivers_dict = manager.dict()
json_data_dict = manager.dict()

for chunk in chunks:
    jobs = []
    for website in chunk:
        for extn in extensions:
            website_drivers_dict[website][extn] = {'driver': None,
                                                   'proxy': None,
                                                   'server': None}
        p = multiprocessing.Process(target=run, args=(website, website_drivers_dict, json_data_dict))
        jobs.append(p)

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()


"""

NOT USED FUNCTIONS

"""


def is_loaded(driver):
    return driver.execute_script("return document.readyState") == "complete"


def wait_until_loaded(driver, timeout=60, period=0.25, min_time=0):
    start_time = time.time()
    must_end = time.time() + timeout
    while time.time() < must_end:
        if is_loaded(driver):
            if time.time() - start_time < min_time:
                time.sleep(min_time + start_time - time.time())
            return True
        time.sleep(period)
    return False

