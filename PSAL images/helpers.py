import threading
import time
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from browsermobproxy import Server
import os, requests, sys
from bs4 import BeautifulSoup
import tldextract

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

def print_batch(lst):
    print("Group:")
    for i in lst:
        print("\t", i._args[0])


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


def find_element_with_src(html_code, src_url):
    # Parse the HTML code using BeautifulSoup
    soup = BeautifulSoup(html_code, 'html.parser')

    # Find the first element with the specified src URL
    element = soup.find(lambda tag: tag.has_attr('src') and tag['src'] == src_url)

    return element

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

    new_path = 'screenshots/'+ extn + '/' + key
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    os.chdir(new_path)
    for url in difference:
        if url in control_driver.source:
            element = find_element(control_driver, url)





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
