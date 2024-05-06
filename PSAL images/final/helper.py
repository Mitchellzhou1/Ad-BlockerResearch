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
from blacklist import *
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

    def get_images(self, website, key, storage, blacklist_, inverse_lookup, regular_lookup):
        self.initialize(key)
        self.proxy.new_har("initial", options={'captureHeaders': True, 'captureContent': True})
        self.driver.get(website)
        wait_until_loaded(self.driver)
        sleep(10)

        packets = self.proxy.har['log']['entries']
        images = self.filter_packets(website, packets, blacklist_, inverse_lookup, regular_lookup)

        storage[website][key] = images

        self.driver.close()
        self.server.stop()
        self.proxy.close()

    def find_missing(self, website, key, results, control, blacklist_, inverse_lookup, regular_lookup):
        self.initialize(key)
        self.proxy.new_har("initial", options={'captureHeaders': True, 'captureContent': True})
        self.driver.get(website)
        wait_until_loaded(self.driver)
        sleep(3)

        control = control[website]['control-scanner1']
        packets = self.proxy.har['log']['entries']
        images = self.filter_packets(website, packets, blacklist_, inverse_lookup, regular_lookup)

        if site_filter(control, images):
            results[website] = 'No Missing Images'
        else:
            for url in (control - images):
                path = get_path(url)
                html_string = None
                if url in self.driver.source:
                    html_string = find_element_in_html(self.driver, url)
                elif path in self.driver.source:
                    html_string = find_element_in_html(self.driver, path)
                elif url in self.driver.source:
                    html_string = find_element_in_css(self.driver, url)
                elif path in self.driver.source:
                    html_string = find_element_in_css(self.driver, path)

                if html_string:
                    if 'control' in key:
                        take_ss_control(self.driver, html_string, key, website)
                        results[website] = 'Inconsistent Site'
                    else:
                        take_ss_entire(self.driver, website, key)

                else:
                    ...
                    # the image was not in the HTML:


    def filter_packets(self, website, packets, blacklist_, inverse_lookup, regular_lookup):
        ret = {}
        driver_domain = url_parser(website)[1]
        for packet in packets:
            try:
                request_url = packet["request"]["url"]
                status_code = packet["response"]["status"]
                resource_domain = url_parser(request_url)[1]
                # gets rid of duplicates! very important!!!
                if ((request_url in ret.keys()) or
                        (status_code not in [200, 204])):
                    continue

                try:
                    status_text = packet["response"]["statusText"]
                except KeyError:
                    status_text = "none"
                    if status_code != 200:
                        print("No Status Text")
                content_type = ''
                referer = ''
                for header in packet['response']['headers']:
                    if header['name'].lower() == 'content-type':
                        content_type = header['value']
                        break

                for header in packet['request']['headers']:
                    if header['name'].lower() == 'referer':
                        referer = header['value']
                        break

                content_type = content_eval(content_type)

                # FILTER FOR JUST IMAGES IN THE JSON
                if "image" not in content_type:
                    continue

                content_size = packet["response"]["content"]["size"]
                # Black List Parser

                in_blacklist = (blacklist_parser(blacklist_, inverse_lookup, regular_lookup, request_url) or
                                blacklist_parser(blacklist_, inverse_lookup, regular_lookup, referer))

                ret[request_url] = [request_url, status_code, status_text, content_size, content_type, referer,
                                    in_blacklist]
            except Exception as e:
                print(e)
                print("Error! Could not decode packet.")
        return ret


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


"""

Image Locator Stuff

"""

def take_ss_entire(driver, website, extn):
    full_page_height = driver.execute_script("return document.body.scrollHeight")

    # Set the window size of the WebDriver to the full page height
    driver.set_window_size(1920, full_page_height)

    # Take a screenshot of the entire page
    screenshot = driver.get_screenshot_as_png()

    current_directory = os.getcwd() + 'PSAL_images/final/RESULTS'
    destination = current_directory + '/' + website + '/' + extn
    if not os.path.exists(destination):
        os.makedirs(destination)
        with open(destination + '/full_page.png', 'wb') as file:
            file.write(screenshot)


def take_ss_control(driver, html_string, extn, website):
    current_directory = os.getcwd() + 'PSAL_images/final/RESULTS'

    xpath = generate_xpath(html_string)
    element = driver.find_element(By.XPATH, xpath)
    element_dir = current_directory + '/' + website + '/' + extn
    if not os.path.exists(element_dir):
        os.makedirs(element_dir)
        element.screenshot(element_dir + f'/{html_string}.png')
        element.get_local_DOM()
        element.screenshot(element_dir + f'/CONTEXT_{html_string}.png')
    else:
        return


def get_path(url):
    # Parse the URL and extract the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path


def find_element_in_html(driver, src_url):
    # Parse the HTML code using BeautifulSoup
    html_code = driver.source
    soup = BeautifulSoup(html_code, 'html.parser')

    # Find the first element with the specified src URL
    element = soup.find(lambda tag: tag.has_attr('src') and tag['src'] == src_url)

    return element


def find_element_in_css(driver, url_to_find):
    js_script = f"""
    function findElementWithBackgroundImage(selector, imageUrl) {{
        var elements = document.querySelectorAll(selector);
        for (var i = 0; i < elements.length; i++) {{
            var style = window.getComputedStyle(elements[i]);
            var backgroundImage = style.getPropertyValue('background-image');
            if (backgroundImage.includes(imageUrl)) {{
                return elements[i];
            }}
        }}
        return null;
    }}

    return findElementWithBackgroundImage('.logo', '{url_to_find}');
    """

    # Execute the JavaScript function and get the element
    logo_element = driver.execute_script(js_script)

    # Print the outerHTML of the found element
    if logo_element:
        return logo_element.get_attribute("outerHTML")
    else:
        return None


def generate_xpath(html_string):
    def parse_html_string(string):
        soup = BeautifulSoup(string, 'html.parser')
        if soup:
            tag = soup.find()
            if tag:
                tag_info = {
                    'tag_name': tag.name,
                    'attributes': tag.attrs
                }
                return tag_info
        return None

    def format_attribute(attr, value):
        # if "'" in value:
        #     value_lst = value.split("'")
        #     return "[contains(@" + attr + ", " + "concat(" + value_lst[0] + ", \"'\", " + value_lst[1] + ", \"'\", " + value_lst[2] + "))]"

        if isinstance(value, list):
            return f'[contains(@{attr}, "{value[0]}")]'
        else:
            if "'" and '"' in value:
                return ''  # this case is too weird. will just skip it.
            elif "'" in value:
                return f"""[@{attr}="{value}"]"""
            return f"""[@{attr}='{value}']"""

    parsed_info = parse_html_string(str(html_string))
    if parsed_info:
        tag_name = parsed_info['tag_name']
        attributes = parsed_info['attributes']

        xpath = f'//{tag_name}'
        for attr, value in attributes.items():
            if attr == 'class':
                if isinstance(value, list):
                    for class_value in value:
                        xpath += f'[contains(@{attr}, "{class_value}")]'
                else:
                    xpath += f'[contains(@{attr}, "{value}")]'
            else:
                xpath += format_attribute(attr, value)

        return xpath
    return None


def go_to_elem(driver, element):
    driver.execute_script(
        "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });", element)


"""

Load Page Stuff

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


def get_image_resources(logs):
    ret = set()
    resources = logs['log']['entries']
    for packet in resources:
        status_code = packet["response"]['status']

        if status_code not in [200, 204]:
            continue

        content_type = ''
        for header in packet['response']['headers']:
            if header['name'].lower() == 'content-type':
                content_type = content_eval(header['value'])
                break
        if content_type != 'images':
            continue

        ret.add(packet["request"]["url"])
    return ret


def content_eval(content_header):
    stylesheet = ['text/css', 'application/css', 'application/x-css', 'text/plain',
                  'text/html']
    script = ['application/javascript', 'application/x-javascript', 'text/javascript', 'text/ecmascript',
              'application/ecmascript']
    images = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml', 'image/x-icon']
    if content_header:
        if any(elem in content_header for elem in stylesheet):
            return "stylesheet"
        if any(elem in content_header for elem in script):
            return "script"
        if any(elem in content_header for elem in images):
            return "images"
    return content_header


"""

HTML Stuff

"""


def get_local_DOM(self, elem):
    amt = 4
    try:
        for i in range(amt):
            elem = elem.find_element(By.XPATH, '..')
        return elem
    except Exception as e:
        # No more parent node to go up. Nothing Serious
        return elem
