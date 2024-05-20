import threading
import time
from time import sleep
from urllib.parse import urlparse
import subprocess

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from browsermobproxy import Server
from selenium.webdriver.common.by import By

from pyvirtualdisplay import Display
from xvfbwrapper import Xvfb

import os, requests, sys
from bs4 import BeautifulSoup
from blacklist import *
import tldextract
import re
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import io
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

user = 'character'
current_dir = os.getcwd()
base_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
current_path = f'{base_dir}/PSAL_images/final/RESULTS/'


def cleanup_tmp():
    files_to_delete = []

    # List all files in the temporary directory
    all_files = os.listdir('/tmp')

    # Filter out files that start with the specified characters
    for file_name in all_files:
        if '.org.chromium' in file_name or '.com.google.Chrome' in file_name or '.X11' in file_name:
            #  or 'go-build' in file_name:
            files_to_delete.append(os.path.join('/tmp', file_name))

    # Delete the files
    for file_path in files_to_delete:
        try:
            subprocess.run(["sudo", "rm", "-rf", file_path], check=True)
            # shutil.rmtree(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def cleanup_chrome():
    os.system('pkill chrome')
    time.sleep(3)


def cleanup_X():
    os.system('pkill Xvfb')
    time.sleep(3)



class Driver:
    def __init__(self):
        self.driver = None
        self.proxy = None
        self.server = None
        self.vdisplay = None

        self.image_urls = []

    def initialize(self, extn):
        try:
            xvfb_args = [
                '-maxclients', '1024'
            ]
            self.vdisplay = Display(backend='xvfb', size=(1920, 1280), visible=False, extra_args=xvfb_args)
            # self.vdisplay = Display(size=(1920, 1280), visible=True)
            self.vdisplay.start()

            if user != 'character':
                server = Server(f"/home/{user}/work/pes/browsermob-proxy/bin/browsermob-proxy")
            else:
                server = Server(f"{base_dir}/browsermob-proxy/bin/browsermob-proxy")
            server.start()
            proxy = server.create_proxy()
            # proxy = server.create_proxy(params={'port': port})

            options = Options()
            if 'control' not in extn:
                options.add_extension(f"{base_dir}/Extensions/extn_crx/{extn}.crx")

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

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            if 'control-scanner' not in extn:
                sleep(12)
            else:
                sleep(2)
            windows = driver.window_handles[::-1]
            for window in windows:
                if len(driver.window_handles) <= 1:
                    driver.switch_to.window(window)
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
            self.driver.set_page_load_timeout(60)
        except Exception as e:
            print(e)

    def load_site(self, site):
        try:
            self.driver.get(site)
            scroll(self.driver)
            sleep(2)
            return True
        except Exception as e:
            print("Error loading site:", site)
            print(str(e).split("\n")[0])
            self.driver.close()
            self.server.stop()
            self.proxy.close()
            self.vdisplay.stop()
            return False

    def get_images(self, website, key, blacklist_):
        for i in range(2):
            try:
                self.initialize(key)
                print(f"Starting Filter Checks: {website}")
                self.proxy.new_har("initial", options={'captureHeaders': True, 'captureContent': True})
                if not self.load_site(website):
                    result = 'Failed Control Filters'
                    write_data(website, key, result)
                    return
                wait_until_loaded(self.driver)
                sleep(2)
                packets = self.proxy.har['log']['entries']
                images = self.filter_packets(website, packets, blacklist_)
                result = images
                write_data(website, key, result)

                self.driver.close()
                self.server.stop()
                self.proxy.close()
                self.vdisplay.stop()
                print(f"Finished Scan Filter: {website}")
                return
            except Exception as e:
                print(e)
                if i == 1:
                    result = 'Failed Control Filters'
                    write_data(website, key, result)
                continue

    def find_missing(self, website, key, blacklist_):
        try:
            self.initialize(key)
            print("Successfully create:", website, key)
            self.proxy.new_har("initial", options={'captureHeaders': True, 'captureContent': True})
            if not self.load_site(website):
                return
            wait_until_loaded(self.driver)

            url = scheme_extractor(website)
            if os.path.exists(f"tmp_data/{url}-control-scanner1.json"):
                with open(f"tmp_data/{url}-control-scanner1.json", 'r') as f:
                    control = json.load(f)
            else:
                result = 'Control-Scanner data was not found... Skipping site'
                write_data(website, key, result)
                return

            packets = self.proxy.har['log']['entries']
            images = self.filter_packets(website, packets, blacklist_)

            if site_filter(control, images, website):
                print(key, "---", "no missing")
                result = 'No Missing Images'
                take_ss(self.driver, '', key, website, '', '')
            else:
                index = 0
                result = {}
                for url in (set(control.keys()) - set(images.keys())):
                    if 'control' in key:
                        result = 'Inconsistent Site'
                        break

                    path = get_path(url)
                    html_string = False
                    if url in self.driver.page_source:
                        html_string = find_element_in_html(self.driver, url)
                    elif path in self.driver.page_source:
                        html_string = find_element_in_html(self.driver, path)
                    elif url in self.driver.page_source:
                        html_string = find_element_in_css(self.driver, url)
                    elif path in self.driver.page_source:
                        html_string = find_element_in_css(self.driver, path)

                    take_ss(self.driver, html_string, key, website, url, str(index))

                    # the html_string tells if the url was found in the page or not
                    result['img_' + str(index)] = control[url]
                    index += 1
            write_data(website, key, result)

        except Exception as e:
            print(e)
            result = 'Inconsistent Site'
            write_data(website, key, result)

        self.driver.close()
        self.server.stop()
        self.proxy.close()
        self.vdisplay.stop()

    def filter_packets(self, website, packets, blacklist_):
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

                in_blacklist = (blacklist_parser(blacklist_, request_url) or
                                blacklist_parser(blacklist_, referer))

                """ FOR TESTING ONLY """
                # setting these strings to False to see if I can take picture of them.

                # if request_url == "https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png":
                #     in_blacklist = False

                """ DONE TESTING """

                if in_blacklist:
                    continue

                ret[request_url] = [request_url, status_code, status_text, content_size, content_type, referer,
                                    in_blacklist]
            except Exception as e:
                print(e)
                print("Error! Could not decode packet.")
        return ret

    def image_packets(self, website, packets, blacklist_, inverse_lookup, regular_lookup):
        ret = {}
        for packet in packets:
            try:
                request_url = packet["request"]["url"]
                status_code = packet["response"]["status"]
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

                in_blacklist = (blacklist_parser(blacklist_, website) or
                                blacklist_parser(blacklist_, website))
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


def scroll(driver, speed=0.1):
    curr_scroll_position = -1
    curr_time = time.time()
    while True:
        # Define the scroll step size
        scroll_step = 100  # Adjust this value to control the scroll speed
        # Get the current scroll position
        scroll_position = driver.execute_script("return window.pageYOffset;")
        # Check if we've reached the bottom
        if curr_scroll_position == scroll_position:
            # this is just in case the scroll doesn't work on the site.
            if curr_scroll_position == 0:
                sleep(5)
            break
        else:
            curr_scroll_position = scroll_position

        # Scroll down by the step size
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")

        # Wait for a bit (this controls the scroll speed indirectly)
        time.sleep(speed)  # Adjust this value to control the scroll speed
        if time.time() - curr_time >= 45:
            break


"""

Image Locator Stuff

"""


def take_ss_entire(driver, screenshot_path, url, extn):
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    page_width = driver.execute_script("return document.body.scrollWidth")
    page_height = driver.execute_script("return document.body.scrollHeight")

    driver.set_window_size(page_width, page_height)

    screenshots = []
    viewport_height = driver.execute_script("return window.innerHeight")
    scroll_height = 0
    while scroll_height < page_height:

        screenshot = driver.get_screenshot_as_png()
        screenshots.append(screenshot)

        scroll_height += viewport_height
        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(1)

    full_screenshot = Image.new('RGB', (page_width, page_height))
    current_height = 0
    for screenshot in screenshots:
        img = Image.open(io.BytesIO(screenshot))
        full_screenshot.paste(img, (0, current_height))
        current_height += viewport_height

    full_screenshot.save(screenshot_path+f'{extn}_entire.png')
    # print("Took full screenshot of", url)
    # print("Path was:", screenshot_path+f'{extn}_entire.png')


def take_ss(driver, html_string, extn, website, img_url, index):

    current_directory = os.getcwd() + '/PSAL_images/final/RESULTS'

    website = scheme_extractor(website)

    element = None
    if html_string:
        xpath = generate_xpath(html_string)
        element = driver.find_element(By.XPATH, xpath)

    element_dir = current_directory + '/' + website + '/'
    if not os.path.exists(element_dir):
        os.makedirs(element_dir)

    # take image of entire site:
    take_ss_entire(driver, element_dir, website, extn)

    if extn != "control":
        element_dir += extn + "/"
        if not os.path.exists(element_dir):
            os.makedirs(element_dir)

        if element:     # element in DOM
            element_dir += '/IN_DOM'
            if not os.path.exists(element_dir):
                os.makedirs(element_dir)
            try:
                element.screenshot(element_dir + f'/img_{index}.png')
            except:
                download_image(img_url, element_dir + f'/img_{index}.png')

            try:
                element = get_parent(element, 4)
                element.screenshot(element_dir + f'/img_{index}_CONTEXT.png')
            except Exception as e:
                return
        elif img_url:           # element in DOM
            element_dir += '/NOT_IN_DOM'
            if not os.path.exists(element_dir):
                os.makedirs(element_dir)
            download_image(img_url, element_dir + f'/img_{index}.png')

       # else: No missing Images



def get_path(url):
    # Parse the URL and extract the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path


def find_element_in_html(driver, src_url):
    # Parse the HTML code using BeautifulSoup
    html_code = driver.page_source
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


def get_parent(elem, amt):
    try:
        for i in range(amt):
            elem = elem.find_element(By.XPATH, '..')
        return elem
    except Exception as e:
        # No more parent node to go up. Nothing Serious
        return elem

def download_image(url, file_path):
    try:
        # Send a GET request to the URL to download the image
        response = requests.get(url)
        if response.status_code == 200:
            # Check if the specified directory exists, create it if not
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Save the image to the specified file path
            with open(file_path, 'wb') as file:
                file.write(response.content)
            file.close()
        else:
            print(f"Failed to download image: {response.status_code} - {response.reason}")
    except Exception as e:
        print(f"An error occurred: {e}")


def manager_dict_serializer(obj):
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items()}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def write_data(website, extn, data):
    website = scheme_extractor(website)
    with open(f"tmp_data/{website}-{extn}.json", 'w') as f:
        json.dump(data, f)
    f.close()


def load_extn_data(website):
    key = scheme_extractor(website)
    ret = []

    for extn in ["control", "ublock", "adblock", "privacy-badger"]:
        if os.path.exists(f"tmp_data/{key}-{extn}.json"):
            with open(f"tmp_data/{key}-{extn}.json", 'r') as f:
                ret.append(json.load(f))
        else:
            ret.append({"missing data": extn})
            print(f"\nmissing {extn} data!\n Aborting site \n")
    return ret
