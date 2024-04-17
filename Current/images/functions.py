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

extensions_configurations = [
    "control",
    "adblock",
    "privacy-badger",
    "ublock"
]

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


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def possible_rules(self, node, prefix):
        strings = []
        # Base case: if the node is the end of a word, add the prefix to the list of strings
        if node.is_end_of_word:
            strings.append(prefix)
        # Recursively generate strings for each child node
        for char, child in node.children.items():
            strings.extend(self.possible_rules(child, prefix + char))
        return strings

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, entire_url):
        node = self.root
        rule = ''
        for char in entire_url:
            if char not in node.children:
                if rule in self.possible_rules(node, rule):
                    print("found regular search item:", rule)
                    return True
                return False
            rule += char
            node = node.children[char]
        return False

    def inverse_search(self, word):
        """
        Only doing domain matching right now
        """
        node = self.root
        rule = ''
        for char in word:
            if node.is_end_of_word:
                if char == '.':
                    # there is a subdomain identified, but the domain matched.
                    print("found rev-search item:", rule[::-1])
                    return True
                else:
                    # doesn't match
                    return False
            if char not in node.children:
                # the domain didn't match
                return False

            rule += char
            node = node.children[char]

        if node.is_end_of_word:
            print("found rev-search item:", rule[::-1])
            return True
        return False


def is_loaded(webdriver):
    return webdriver.execute_script("return document.readyState") == "complete"


def wait_until_loaded(webdriver, timeout=60, period=0.25, min_time=0):
    start_time = time.time()
    mustend = time.time() + timeout
    while time.time() < mustend:
        if is_loaded(webdriver):
            if time.time() - start_time < min_time:
                time.sleep(min_time + start_time - time.time())
            return True
        time.sleep(period)
    return False


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_pid_by_port(port):
    try:
        output = subprocess.check_output(['lsof', '-i', f'tcp:{port}']).decode()
    except subprocess.CalledProcessError as e:
        # print("Error:", subprocess.check_output(['lsof', '-i', 'tcp']).decode())
        return None

    for line in output.splitlines():
        if "LISTEN" in line:
            parts = line.split()
            return parts[1]  # PID is typically in the second column

    return None


###################################################

"""             Mitchell's Functions            """


def ends_with_file_extension(string):
    for ext in file_extensions:
        if string.endswith(ext):
            return True
    return False


def file_exists(filename):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(current_dir, filename)
    return os.path.exists(filepath)


def write_JSON(name, my_dict):
    json_file_path = 'json/' + name + ".json"
    with open(json_file_path, "w") as json_file:
        json.dump(my_dict, json_file)
    json_file.close()


def remove_after_substring(link, substring):
    for seperator in substring:
        index = link.find(seperator)
        if index != -1:
            link = link[:index]

    return link


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
    print("\nBuilding Blacklist tree...")
    with open('strippeddownblacklist.txt', 'w') as file:
        for item in sorted(combined):
            file.write(str(item) + '\n')
    file.close()
    print("Finished Building Blacklist tree!")
    return sorted(combined), inverse_lookup, regular_lookup


def binary_search(blacklist, domain, full_url):
    def url_formatter(link):
        prefixes = ["https://", "http://", "www."]
        for prefix in prefixes:
            if link.startswith(prefix):
                return link[len(prefix):]
        return link

    def match(rule, full_url):
        parts = rule.split("*")
        for part in parts:
            if part not in full_url:
                return False
        return True

    low = 0
    high = len(blacklist) - 1
    domain = url_formatter(domain)
    while low <= high:
        mid = (low + high) // 2
        rule = blacklist[mid]
        if match(rule, full_url):
            print("found blacklist item:", rule)
            return True  # Match found
        elif rule < domain:
            low = mid + 1
        else:
            high = mid - 1

    return False  # No match found


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


def get_final_url(url):
    try:
        response = requests.get(url, allow_redirects=True)
        if url != response.url:
            print("\n", url)
        return response.url
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def url_parser(full_url):
    extracted = tldextract.extract(full_url)
    subdomain = extracted.subdomain
    domain = extracted.domain
    suffix = extracted.suffix

    return subdomain, domain, suffix


def scheme_extractor(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain = domain.replace('www.', '')
    new_url = domain + parsed_url.path
    if parsed_url.query:
        new_url += '?' + parsed_url.query
    return new_url


def blacklist_parser(blacklist, inverse_lookup, regular_lookup, url):
    subdomain, domain, suffix = url_parser(url)
    subdomains = ['done'] + subdomain.split(".")
    test_url = domain + "." + suffix

    # removes the https:// http:// and www. from the url
    simplified_url = scheme_extractor(url)

    if inverse_lookup.inverse_search(test_url[::-1]):
        return True
    return False

    # NOT USING FOR NOW!!!!
    # while subdomains:
    #     if inverse_lookup.inverse_search(test_url[::-1]):
    #         return True
    #
    #     if regular_lookup.search(simplified_url):
    #         return True
    #
    #     if binary_search(blacklist, domain, url):
    #         return True
    #     domain = f"{subdomains.pop()}.{domain}"
    # return False


def filter_packets(website, packets, blacklist_, inverse_lookup, regular_lookup):
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

            for header in packet['request']['headers']:
                if header['name'].lower() == 'referer':
                    referer = header['value']

            content_type = content_eval(content_type)
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


def compare_resources(extension, control_url_dict, extension_url_dict):
    results = {}
    errors = {}
    for website in control_url_dict.keys():
        results[website] = {"missing_resources": [],
                            "additional_resources": []}

        # control_url_dict = {url: control[website][ind] for ind, (url, _, _, _, _) in enumerate(control[website])}
        # extension_url_dict = {url: extension_resources[website][ind] for ind, (url, _, _, _, _) in enumerate(extension_resources[website])}

        try:
            total_urls = set(list(control_url_dict[website].keys()) + list(extension_url_dict[website].keys()))
            for url in total_urls:
                try:
                    if url not in extension_url_dict[website]:
                        results[website]["missing_resources"].append(control_url_dict[website][url])
                    elif url not in control_url_dict[website]:
                        results[website]["additional_resources"].append(extension_url_dict[website][url])
                except KeyError as k:
                    print(3, url, "KeyError")
                    errors[url] = k
                    continue
                except Exception as e:
                    errors[url] = e
                    continue
        except KeyError as k:
            print(4, extension, k)
            continue
        except Exception as e:
            print(e)

        write_JSON(extension + "missing", results)
    write_JSON(extension + "_errors", errors)


def take_ss(extension, control_url_dict, extension_url_dict):



"""             Mitchell's Functions            """

###################################################