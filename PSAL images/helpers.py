import threading
import time
from time import sleep
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from browsermobproxy import Server
from selenium.webdriver.common.by import By
import os, requests, sys
from bs4 import BeautifulSoup
import tldextract
import re
from selenium.webdriver.common.action_chains import ActionChains


file_extensions = [
    ".js",  # JavaScript
    ".css",  # Cascading Style Sheets
    ".swf",  # Adobe Flash
    ".gif",  # Graphics Interchange Format
    ".jpg",  # Joint Photographic Experts Group
    ".jpeg",  # Joint Photographic Experts Group
    ".png",  # Portable Network Graphics
    ".mp4",  # MPEG-4 video file
    ".mp3",  # MPEG Audio Layer III
    ".html",  # Hypertext Markup Language
    ".php",  # Hypertext Preprocessor
    ".asp",  # Active Server Pages
    ".aspx",  # Active Server Pages
    ".xml",  # Extensible Markup Language
    ".svg",  # Scalable Vector Graphics
    ".woff",  # Web Open Font Format
    ".woff2",  # Web Open Font Format 2
    ".ttf",  # TrueType Font
    ".otf",  # OpenType Font
    ".webm",  # WebM video file
    ".webp",  # WebP image file
    ".ico"  # Icon file
]


"""

Simply code functions

"""


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def print_batch(lst):
    print("Group:")
    for i in lst:
        print("\t", i._args[0])


def get_path(url):
# Parse the URL and extract the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path


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

    parsed_info = parse_html_string(html_string)
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


def get_correct_elem(driver, initial_html, xpath):
    counter = 3
    while "[" in xpath and counter:
        elements = driver.find_elements(By.XPATH, xpath)  # will return [] if none are found
        for i in elements:
            if i.get_attribute("outerHTML") == initial_html:
                return i
        try:  # sometimes the structure is the same.
            return driver.find_element(By.XPATH, xpath)
        except Exception:
            button_part = xpath.split("[")[0]
            xpath_list = re.findall(r'\[@.*?\]', xpath)
            rem_candidate = max(xpath_list, key=len)
            if "aria-label" in rem_candidate:
                rem_candidate = min(xpath_list, key=len)
            xpath_list.remove(rem_candidate)
            xpath = ''.join([button_part] + xpath_list)
        counter -= 1
    try:
        return driver.find_element(By.XPATH, xpath)  # will error if none are found
    except Exception as e:
        print("Didn't find element")
    return None


def scroll_to_elem(element, driver):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()

    # Optional: Center the element on the screen
    driver.execute_script("window.scrollTo(0, arguments[0]);",
                          element.location['y'] - (driver.get_window_size()['height'] / 2))
    sleep(1)
    return driver.execute_script("return window.scrollY;")


def scroll_to_position(driver, y=0):
    driver.execute_script(f"window.scrollTo(0, {y});")
    start_time = time.time()

    while True:
        scroll_position = driver.execute_script("return window.scrollY;")
        if scroll_position == y:
            break

        current_time = time.time()
        if current_time - start_time >= 10:
            print("Timeout reached. Scroll position not stabilized.")
            break

        time.sleep(0.5)

    return driver.execute_script("return [window.scrollX, window.scrollY];")


def take_ss(extn, url, control_driver, extn_driver, element):
    try:
        root_dir = os.getcwd()
        full_path = root_dir + '/screenshots/' + url + '/' + extn
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        if element:
            # element.save_screenshot(f'{full_path}/control')
            ...
        if control_driver:
            y_amount = scroll_to_elem(element, control_driver)
            control_driver.save_screenshot(f'{full_path}/control')
        if extn_driver:
            scroll_to_position(extn_driver, y_amount)
            extn_driver.save_screenshot(f'{full_path}/{extn}')
    except Exception as e:
        print(e)


"""

Blacklist Stuff

"""

def compare_resources(key, control, network_logs, extn, control_driver, extn_driver):
    # compare the resources with the control:
    extn_packets = get_image_resources(network_logs[extn])
    difference = control - extn_packets

    current_path = os.getcwd()
    os.chdir(current_path)

    if not difference:
        return

    for url in difference:
        path = get_path(url)
        html_string = None
        if url in control_driver.source:
            html_string = find_element_in_html(control_driver, url)
        elif path in control_driver.source:
            html_string = find_element_in_html(control_driver, path)
        elif url in control_driver.source:
            html_string = find_element_in_css(control_driver, url)
        elif path in control_driver.source:
            html_string = find_element_in_css(control_driver, path)

        if html_string:
            xpath = generate_xpath(html_string)
            elem = get_correct_elem(control_driver, html_string, xpath)
            elem.take_ss()




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

def remove_after_substring(link, substring):
    for seperator in substring:
        index = link.find(seperator)
        if index != -1:
            link = link[:index]
    return link

def ends_with_file_extension(string):
    for ext in file_extensions:
        if string.endswith(ext):
            return True
    return False


def url_parser(full_url):
    extracted = tldextract.extract(full_url)
    subdomain = extracted.subdomain
    domain = extracted.domain
    suffix = extracted.suffix

    return subdomain, domain, suffix
def initialize_blacklists(inverse_lookup, regular_lookup):
    """
    Combines all the Black lists into 1 big list
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    extensions_dir = os.path.abspath(os.path.join(current_dir, 'blacklists'))

    # Check if extensions_dir exists, if not, create it
    if not os.path.exists(extensions_dir):
        os.makedirs(extensions_dir)

    # URLs for the files to download
    files_urls = {
        "easylist.txt": "https://easylist.to/easylist/easylist.txt",
        "easyprivacy.txt": "https://easylist.to/easylist/easyprivacy.txt",
        "Peter Lowe": "https://pgl.yoyo.org/adservers/serverlist.php"
        # Add the correct file extension if needed, e.g., .txt
    }

    # Iterate over the files and their URLs
    for filename, url in files_urls.items():
        filepath = os.path.join(extensions_dir, filename)

        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Downloading {filename} from {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename} successfully.")
            except requests.RequestException as e:
                print(f"Error downloading {filename}: {e}")
        else:
            print(f"{filename} already exists.")

    easy_list = open(f"{extensions_dir}/easylist.txt", "r")
    easy_privacy = open(f"{extensions_dir}/easyprivacy.txt", "r")
    peter_lowe = open(f"{extensions_dir}/Peter Lowe", "r")

    combined = set()

    for rule in easy_privacy:
        if rule[:2] == "||":
            rule = remove_after_substring(rule.strip().lstrip("||"), "^$~?")
            if ends_with_file_extension(rule):
                continue

            subdomain, domain, suffix = url_parser(rule)
            rule = domain + '.' + suffix
            combined.add(rule)
            inverse_lookup.insert(rule[::-1])
            regular_lookup.insert(rule)

    for rule in easy_list:
        if rule[:2] == "||":
            rule = remove_after_substring(rule.strip().lstrip("||"), "^$~?")
            if ends_with_file_extension(rule):
                continue

            subdomain, domain, suffix = url_parser(rule)
            rule = domain + '.' + suffix
            combined.add(rule)
            inverse_lookup.insert(rule[::-1])
            regular_lookup.insert(rule)

    for rule in peter_lowe:
        if rule[:10] == "127.0.0.1 ":
            rule = rule.strip()[10:]
            if ends_with_file_extension(rule):
                continue

            subdomain, domain, suffix = url_parser(rule)
            rule = domain + '.' + suffix
            combined.add(rule)
            inverse_lookup.insert(rule[::-1])
            regular_lookup.insert(rule)

    # THIS IS JUST TO HELP ME DEBUG AND SEE THE CONTENTS OF THE COMBINED BLACKLISTS
    with open('stripped_down_blacklist.txt', 'w') as file:
        for item in sorted(combined):
            file.write(str(item) + '\n')
    file.close()
    return sorted(combined), inverse_lookup, regular_lookup



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