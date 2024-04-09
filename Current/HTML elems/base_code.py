import os
import re
import time
import signal
import functools
import replay_0
from time import sleep

import pyautogui
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from Excel import *

options = Options()
# options.headless = False
# options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-animations")
options.add_argument("--disable-web-animations")
# options.add_argument("--incognito")
# options.add_argument("--single-process")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-web-security")
options.add_argument("--disable-features=IsolateOrigins,site-per-process")
options.add_argument("--disable-features=AudioServiceOutOfProcess")
# options.add_argument("auto-open-devtools-for-tabs")
options.add_argument(
    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")

options.binary_location = '/usr/local/bin/chrome_113/chrome'

# /usr/local/bin/chrome_113/chrome --user-data-dir=/home/chatacter/Downloads/manual_analysis/wpr_data  --host-resolver-rules=“MAP *:80 127.0.0.1:9090,MAP *:443 127.0.0.1:9091,EXCLUDE localhost” --ignore-certificate-errors-spki-list=PhrPvGIaAMmd29hj8BCZOq096yj7uMpRNHpn5PDxI6I=,2HcXCSKKJS0lEXLQEWhpHUfGuojiU0tiT5gOF9LP6IQ=
# folder_path = f"/home/chatacter/wpr_data/"
# if not os.path.exists(folder_path):
# # Create the folder
#     os.makedirs(folder_path)
#
# # options.add_argument('--ignore-certificate-errors')
# options.add_argument(folder_path)
# options.add_argument(f'--host-resolver-rules="MAP *:80 127.0.0.1:9090,MAP *:443 127.0.0.1:9091,EXCLUDE localhost')
# options.add_argument('--ignore-certificate-errors-spki-list=PhrPvGIaAMmd29hj8BCZOq096yj7uMpRNHpn5PDxI6I=,2HcXCSKKJS0lEXLQEWhpHUfGuojiU0tiT5gOF9LP6IQ=')

"""
cd /go/src/catapult/web_page_replay_go

go run src/wpr.go record --http_port=9090 --https_port=9091 ~/control.wprgo
go run src/wpr.go replay --http_port=9090 --https_port=9091 ~/control.wprgo
"""


class TimeoutError(Exception):
    pass

def timeout(seconds):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def handler(signum, frame):
                raise TimeoutError

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)

            result = func(*args, **kwargs)
            signal.alarm(0)
            return result

        return wrapper

    return decorator


class Driver:
    def __init__(self):
        # specific test for these attributes
        self.attributes = []
        self.xPaths = []

        # initializing the adBlocker
        self.adBlocker_name = ''
        self.driver = None
        self.tries = 1

        # used for optimization
        self.keywords = [
            'login', 'my account', 'sign in', 'sign-in', 'signin', 'log in',  # English
            '登录', '我的帐户',  # Chinese (Simplified)
            'вход', 'войти', 'мой аккаунт',  # Russian
            'iniciar sesión', 'mi cuenta'  # Spanish
        ]
        self.seen_sites = []
        self.xpath_remover = 3
        self.website_sleep_time = 3  # longer this value, more consistent the results
        self.html_obj = None
        self.DOM_traversal_amt = 4
        self.scan_timeout = 180
        self.test_elem_timeout = 300

        # used for testing
        self.curr_site = 0
        self.curr_elem = 0
        self.initial_outer_html = ''
        self.after_outer_html = ''
        self.initial_local_DOM = ''
        self.after_local_DOM = ''
        self.url = ''
        self.redirect_url = ''
        self.DOM_changed = False
        self.outer_HTML_changed = False

        # used for random picking
        self.dictionary = {}
        self.all_sites = {}
        self.no_elms = 15
        self.chosen_elms = []
        self.all_html_elms = []

    def initialize(self, seconds=14):
        """
            This function will start a Chrome instance with the option of installing an ad blocker.
            Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_directory = os.path.dirname(os.path.dirname(current_dir))
        extensions_dir = os.path.abspath(os.path.join(parent_directory, 'Extensions', 'Ad-Blockers'))

        proxy_address = "127.0.0.1:8080"
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_extension('Captcha-Solver-Auto-Recognition-and-Bypass.crx')
        chrome_options.add_argument('--enable-logging')
        options.add_argument('--proxy-server={}'.format(proxy_address))
        if self.adBlocker_name == 'AdBlockPlus':
            extension_path = os.path.join(extensions_dir, 'adBlockerPlus.crx')
            chrome_options.add_extension(extension_path)
        elif self.adBlocker_name == 'uBlock':
            extension_path = os.path.join(extensions_dir, 'uBlock-Origin.crx')
            chrome_options.add_extension(extension_path)

        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # self.driver = webdriver.Chrome(options=options)

        self.driver.set_window_size(1555, 900)
        # give it time to install
        if self.adBlocker_name == 'AdBlockPlus':
            sleep(seconds)
            pyautogui.hotkey('ctrl', 'w')

        if self.html_obj:
            file_path = f'{self.html_obj}.replay_0'
            with open(file_path, 'r') as json_file:
                self.dictionary = replay_0.load(json_file)
            self.all_sites = list(self.dictionary.keys())

    def is_loaded(self):
        return self.driver.execute_script("return document.readyState") == "complete"

    def wait_until_loaded(self, timeout=60, period=0.25, min_time=0):
        start_time = time.time()
        mustend = time.time() + timeout
        while time.time() < mustend:
            if self.is_loaded():
                if time.time() - start_time < min_time:
                    time.sleep(min_time + start_time - time.time())
                return True
            time.sleep(period)
        return False

    def load_site(self, url):
        """
            makes selenium load the site. will add http://www. if needed and filters out to see if the website is
            accessible or not.
        """

        def helper(url_):
            if url[:4] != 'http':
                return f'http://www.{url_}'
            return url

        url = helper(url)
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0'}
            response = requests.get(url, timeout=60, allow_redirects=True, headers=headers)
            if response.status_code == 200:
                try:
                    self.driver.get(url)
                    self.is_loaded()
                    sleep(self.website_sleep_time)
                    self.url = self.driver.current_url
                    if self.url not in self.seen_sites:
                        write_results(self.url)
                        self.seen_sites.append(self.url)
                    return True
                except TimeoutException:
                    raise TimeoutError("Took too long to load...")
        except Exception as e:
            self.seen_sites.append(url)
            return False

    def reinitialize(self):
        self.driver.close()
        self.initialize()
        self.tries += 1

    def click_button(self, button):
        try:
            button.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });", button)
            sleep(2)
            button.click()

    def cursor_change(self, element):
        actions = ActionChains(self.driver)
        # print(element.get_attribute('outerHTML'))
        try:
            actions.move_to_element(element).perform()
            sleep(1)
            cursor_property = element.value_of_css_property('cursor')
            if cursor_property == 'pointer':
                return True
            else:
                return False
        except Exception as e:
            return False

    def check_redirect(self, url):
        def are_urls_equal(url1, url2):
            path1 = url1.rstrip('/').strip('https://').strip('www.')
            path2 = url2.rstrip('/').strip('https://').strip('www.')
            return path1 == path2

        sleep(3)
        if not are_urls_equal(self.driver.current_url, url):
            return True, self.driver.current_url

        all_windows = self.driver.window_handles

        # tests for more windows and will close them
        if len(all_windows) > 1:
            for window in all_windows[1:]:
                self.driver.switch_to.window(window)
                self.driver.close()
            self.driver.switch_to.window(all_windows[0])
            return True, self.driver.current_url
        return False, self.driver.current_url

    def count_tags(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tags = soup.find_all()
        return len(tags)

    def get_local_DOM(self, elem):
        for i in range(self.DOM_traversal_amt):
            elem = elem.find_element(By.XPATH, '..')
        return elem.get_attribute('outerHTML')

    def generate_xpath(self, html_string):
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

    def get_correct_elem(self, xpath, outerHTML):
        counter = self.xpath_remover
        while "[" in xpath and counter:
            elements = self.driver.find_elements(By.XPATH, xpath)  # will return [] if none are found
            for i in elements:
                if i.get_attribute("outerHTML") == outerHTML:
                    return i
            try:  # sometimes the structure is the same.
                return self.driver.find_element(By.XPATH, xpath)
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
            return self.driver.find_element(By.XPATH, xpath)  # will error if none are found
        except Exception as e:
            print("Didn't find element")
        return None

    def check_opened(self, url, button, initial_tag):
        def check_HTML(initial, after):
            if initial != after:
                return True
            return False

        redirect, new_url = self.check_redirect(url)
        if redirect:
            return "True - Redirect"

        try:
            self.after_outer_html = button.get_attribute('outerHTML')
        except StaleElementReferenceException:
            # this is good, means that the button disappeared after clicking
            # could be things like "close", "search", "expand", "show more", etc.
            return "True - Stale Element"

        self.DOM_changed = check_HTML(self.initial_local_DOM, self.get_local_DOM(button))
        self.outer_HTML_changed = check_HTML(self.initial_outer_html, self.after_outer_html)

        if self.outer_HTML_changed:
            return "True - outerHTML change"

        if self.DOM_changed:
            return "True? - Local DOM Change"

        if self.count_tags() > initial_tag:
            return "True - More Tags"

        return "False"

    @timeout(300)
    def test_button(self, tries):
        site = self.all_sites[self.curr_site]
        outerHTML, refresh = self.dictionary[site][self.curr_elem]
        xpath = self.generate_xpath(outerHTML)

        if refresh:
            self.load_site(site)
        self.initial_outer_html = outerHTML
        element = self.get_correct_elem(xpath, outerHTML)
        self.initial_local_DOM = self.get_local_DOM(element)

        initial_tag = self.count_tags()

        self.click_button(element)

        check = self.check_opened(self.url, element, initial_tag)

        if check == "True - Redirect":
            # outer_HTML_change = url
            # Dom_change = new_url
            write_results([check, '', '', self.initial_outer_html, '', '', '',
                           self.url, self.driver.current_url, tries])
        elif check == "True - outerHTML change" or check == "True - Stale Element":
            write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html,
                           self.after_outer_html, '', '', '', '', tries])

        elif check == "True? - Local DOM Change":
            # need to figure out algo after find the difference
            write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html, '',
                           self.initial_local_DOM, self.after_local_DOM, '', '', tries])

        elif check == "True - More Tags":
            # need to figure out algo after find the difference
            write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html, '',
                           self.initial_local_DOM, self.after_local_DOM, '', '', tries])

        elif check == "False":
            if self.is_slideshow(self.initial_outer_html):
                check = 'True? - slideshow'
            elif self.is_required(self.initial_outer_html):
                check = 'Filtered - user interaction required'
            elif self.is_scrollpage(self.initial_outer_html):
                check = 'True? - page was scrolled'
            elif self.is_download_link(self.initial_outer_html):
                check = 'True? - download link'
            elif self.is_open_application(self.initial_outer_html):
                check = 'True? - opened application'
            else:
                self.dictionary[site][self.curr_elem][1] = 0
                lst = self.dictionary[self.all_sites[self.curr_site]]
                if self.curr_elem + 1 < len(lst):
                    lst[self.curr_elem], lst[self.curr_elem + 1] = lst[self.curr_elem + 1], lst[self.curr_elem]
                    self.curr_elem -= 1
                return

            write_results([check, "False", "False", self.initial_outer_html, '',
                       "", "", '', '', tries])

    def click_on_elms(self, tries):

        while self.curr_site < len(self.all_sites):
            if self.curr_elem >= len(self.dictionary[self.all_sites[self.curr_site]]):
                self.curr_site += 1
                self.curr_elem = 0
            else:
                self.test_button(tries)
                self.curr_elem += 1

        self.curr_site = -1

    ############################################################

    """            
            FINDING AND FILTERING THE HTML Elements
    """

    ############################################################
    @timeout(300)
    def scan_page(self):
        self.load_site(self.url)  # extra refresh helps get rid of some false findings
        self.get_elements()
        self.dictionary[self.url] = self.chosen_elms

        # while self.curr_elem < len(self.dictionary[self.url]):
        #     try:
        #         xpath = self.generate_xpath(self.dictionary[self.url][self.curr_elem])
        #         elm = self.get_correct_elem(xpath, self.initial_outer_html)
        #         elm.click()
        #         sleep(1)
        #         self.load_site(self.url)
        #     except Exception:
        #         pass
        #     self.curr_elem += 1
        all_windows = self.driver.window_handles
        if len(all_windows) > 1:
            for window in all_windows[1:]:
                self.driver.switch_to.window(window)
                self.driver.close()
            self.driver.switch_to.window(all_windows[0])
        self.curr_elem = 0
        self.curr_site += 1

        storeDictionary(self.dictionary)

    def make_unique(self, potential):
        # temp = [elem.get_attribute("outerHTML") for elem in potential]
        # temp = list(set(temp))
        self.chosen_elms = [[elem, 1] for elem in potential]

    def get_elements(self):
        # returns the contents (will be selenium objs)
        ret = []
        if self.html_obj == "drop downs":
            ret = self.find_dropdown()
        elif self.html_obj == "buttons":
            ret = self.find_buttons()
        elif self.html_obj == "links":
            ret = self.find_links()
        elif self.html_obj == "login":
            ret = self.find_login()
        else:
            print("Invalid Element type to retrieve")

        if self.html_obj == "login":
            final_lst = []
            for i in range(len(ret)):
                try:
                    if self.filter(ret[i]):
                        final_lst.append(ret[i])
                except Exception as e:
                    continue
        else:
            # random.shuffle(ret)   No random shuffle so that the slideshows are better to click on
            unique = []
            limit = min(15, len(ret))
            i = 0
            while len(unique) < limit and i < len(ret):
                print(i, len(unique), ret[i].get_attribute("outerHTML"))
                if self.filter(ret[i]) and ret[i].get_attribute("outerHTML") not in unique:
                    unique.append(ret[i].get_attribute("outerHTML"))
                i += 1

        self.make_unique(unique)  # unique by looking at the outerHTML

        # the chosen_elms will be the unique outerHTML
        if len(self.chosen_elms) <= self.no_elms:
            write_results(f"testing {len(self.chosen_elms)} / {len(self.chosen_elms)}")
        else:
            write_results(f"testing {len(self.chosen_elms)} / {self.no_elms}")

    def filter(self, element):

        if self.html_obj == "login":
            if any(keyword.lower() in element.text.lower() for keyword in self.keywords):
                if self.cursor_change(element):
                    print(f"{self.url} \t {element.text}")
                    return True
        elif self.cursor_change(element):  # and element.is_displayed()   not always working correctly :(
            return True
        else:
            return False

    def specific_element_finder(self, found_elements=None):
        # will just add on to the current found_elements list.
        if not found_elements:
            found_elements = []
        for attribute in self.attributes:
            for path in self.xPaths:
                xpath = (f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
                         f'"abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]')
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element not in found_elements:
                            if self.html_obj == "buttons":
                                if "href" not in element.get_attribute("outerHTML"):
                                    found_elements.append(element)
                            else:
                                found_elements.append(element)
                except Exception as e:
                    print(e)
        return found_elements

    def find_buttons(self):
        def collect():
            found_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            for anchor in self.driver.find_elements(By.TAG_NAME, 'a'):
                if anchor.get_attribute("href") is None:
                    found_elements.append(anchor)

            final = self.specific_element_finder(found_elements)
            return final

        try:
            ret = collect()
            return ret
        except Exception as e:  # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                write_results(error_message)

    def find_dropdown(self):
        try:
            ret = self.specific_element_finder()
            return ret
        except Exception as e:
            try:
                sleep(5)
                return self.specific_element_finder()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                write_results(error_message)

    def find_links(self):
        def collect():
            final = []
            for anchor in self.driver.find_elements(By.TAG_NAME, 'a'):
                if anchor.get_attribute("href"):
                    final.append(anchor)

            return final

        try:
            ret = collect()
            return ret
        except Exception as e:  # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                write_results(error_message)

    def find_login(self):
        def collect():
            found_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            found_elements += self.driver.find_elements(By.TAG_NAME, 'a')
            final = self.specific_element_finder(found_elements)
            return final

        try:
            ret = collect()
            # for i in ret:
            #     print(i.get_attribute("outerHTML"))
            return ret
        except Exception as e:  # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                write_results(error_message)

    ############################################################
    """            
            Resources
    """

    ############################################################
    def collect_failed_resources(self):
        logs = self.driver.get_log('browser')
        for log in logs:
            resource, message = log['message'].split(" - ")
            if message == "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT":
                print(resource)


    ############################################################

    """            
            False Positive Findings
    """

    ############################################################

    def is_slideshow(self, html):
        html = html.lower()
        possible = ['active', 'aria-pressed="true"', 'aria-selected="true"']
        for attribute in possible:
            if attribute in html:
                return None
        return False

    def is_required(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tag = soup
        if soup.find() == 'input':
            return True
        keywords = ['aria-disabled="true"', ' disabled ', 'disabled=""']
        if any(keyword in html.lower() for keyword in keywords):
            return True
        return False

    def is_scrollpage(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Find all <a> tags with href starting with "#"
        scroll_links = soup.find_all('a', href=lambda href: href and href.startswith('#') and len(href) > 1)
        if scroll_links:
            return True

        keywords = ['scrollintoview', 'scroll-down']
        if any(keyword in html.lower() for keyword in keywords):
            return True
        return False

    def is_download_link(self, html):
        file_extensions = [
            '.aac', '.aif', '.aifc', '.aiff', '.au', '.avi', '.bat', '.bin', '.bmp', '.bz2',
            '.c', '.class', '.com', '.cpp', '.css', '.csv', '.dat', '.dmg', '.doc', '.docx',
            '.dot', '.dotx', '.eps', '.exe', '.flac', '.flv', '.gif', '.gzip', '.h', '.htm',
            '.html', '.ico', '.iso', '.java', '.jpeg', '.jpg', '.js', '.replay_0', '.log', '.m4a',
            '.m4v', '.mid', '.midi', '.mov', '.mp3', '.mp4', '.mpa', '.mpeg', '.mpg', '.odp',
            '.ods', '.odt', '.ogg', '.otf', '.pdf', '.php', '.pl', '.png', '.ppt', '.pptx',
            '.ps', '.psd', '.py', '.qt', '.rar', '.rb', '.rtf', '.s', '.sh', '.svg', '.swf',
            '.tar', '.tar.gz', '.tex', '.tif', '.tiff', '.ttf', '.txt', '.wav', '.webm', '.wma',
            '.wmv', '.woff', '.woff2', '.xls', '.xlsx', '.xml', '.yml', '.zip', '.apk'
        ]
        if any(html.endswith(ext) for ext in file_extensions):
            return True

        # Check if URL contains certain keywords
        if 'download' in html.lower() or 'file' in html.lower():
            return True
        return False

    def is_open_application(self, html):
        potential = ['mailto', 'tel', 'sms']
        for attribute in potential:
            if attribute in html.lower():
                return True
        return False


# shared_driver = Driver()
