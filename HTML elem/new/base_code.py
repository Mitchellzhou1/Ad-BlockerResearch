import time
import json
import os
import re
from urllib.parse import urlparse

# import pyautogui
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common import NoSuchElementException, StaleElementReferenceException, InvalidSelectorException, \
    ElementNotSelectableException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from functions import *

attributes_dict = {
    "buttons": {
        "attributes": ['button', 'submit', '#'],
        "xpaths": ['@role', '@type']
    },
    "drop downs": {
        "attributes": ['false', 'true', 'main menu', 'open menu', 'all microsoft menu', 'menu', 'navigation',
                       'primary navigation', 'hamburger', 'settings and quick links', 'dropdown', 'dialog',
                       'js-menu-toggle', 'searchDropdownDescription', 'ctabutton',
                       'legacy-homepage_legacyButton__oUMB9 legacy-homepage_hamburgerButton__VsG7q',
                       'Toggle language selector', 'Open Navigation Drawer', 'guide', 'Expand Your Library',
                       'Collapse Your Library'],
        "xpaths": ['@aria-expanded', '@aria-label', '@class', '@aria-haspopup', '@aria-describedby', '@data-testid']
    },
    "links": {
        "attributes": [],
        "xpaths": ['href']
    },
    "login": {  # remember to enable HREF
        "attributes": ['button', 'submit', '#'],
        "xpaths": ['@role', '@type']
    }
    , "manual": {
        "attributes": [],
        "xpaths": []
    },
    "input": {
        "attributes": ['text'],
        "xpaths": ['@type']
    },
    "submit": {
        "attributes": ['submit'],
        "xpaths": ['@type']
    }

}


class Driver:
    def __init__(self, html_elem, adB, replay, data_dict):
        # specific test for these attributes
        self.html_elem = html_elem
        self.attributes = attributes_dict[html_elem]['attributes']
        self.xPaths = attributes_dict[html_elem]['xpaths']
        self.dictionary = {}

        # initializing the adBlocker
        self.adBlocker_name = adB
        self.driver = None
        self.tries = 1
        self.vdisplay = ''
        self.actions = None

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
        self.DOM_traversal_amt = 3
        self.scan_timeout = 180
        self.test_elem_timeout = 300

        # used for testing
        self.elem_indx = 0
        self.page_source = ''
        self.initial_outer_html = ''
        self.after_outer_html = ''
        self.initial_local_DOM = ''
        self.after_local_DOM = ''
        self.initial_manual = ''
        self.after_manual = ''
        self.initial_tag = 0
        self.after_tag = 0
        self.current_url = ''              # current URL shown by the browser
        self.original_url = ''             # original url (contains http://www.)

        self.DOM_changed = False
        self.outer_HTML_changed = False
        self.manual_change = False

        self.result = ''

        # used for storing the final results
        self.final_result = data_dict

        self.all_sites = {}
        self.chosen_elms = []
        self.all_html_elms = []

        #### RITIK
        self.options = ''
        self.replay = replay

        #####debug
        self.image_index = 0
        self.result = ''

    def initialize(self, options, num_tries, url):
        """
            This function will start a Chrome instance with the option of installing an ad blocker.
            Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
        """
        self.original_url = url
        self.tries = num_tries

        key = ''
        if 'www' in url:
            key = url.split('www.')[1]
        if '://' in key:
            key = key.split('://')[1]
        key = key.replace("/", "_")

        # Specify the version of Chrome browser you are using
        self.chrome_version = "113.0.5672.0"  # Chrome browser version

        for i in range(self.tries):
            try:
                self.options = options
                log_file_path = f"logs/chromedriver_{key}.log"
                service = Service(executable_path='/home/mitch/work/pes/chromedriver_113/chromedriver',
                                  service_args=["--verbose", f"--log-path={log_file_path}"])
                # service = Service(ChromeDriverManager(version=self.chrome_version).install(), service_args=["--verbose", f"--log-path={log_file_path}"])
                self.driver = webdriver.Chrome(options=options, service=service)
                print("successfully create driver for", url)
                self.driver.set_page_load_timeout(45)
                time.sleep(2)
                break
            except Exception as e:
                if num_tries == 1:
                    print(f"couldn't create browser session... FAILED -- {self.original_url}")
                    print(e)
                    return 0
                else:
                    print(f"couldn't create browser session... trying again -- {self.original_url}")
                    time.sleep(5)

        time.sleep(5)
        self.actions = ActionChains(self.driver)
        return 1

    def replay_initialize(self):
        """
            This function will store the elements from the previous replay 0 phase. The replay 1 phase will be
            exclusively testing these pre-selected elements
        """

        file_path = f"json/{self.html_elem}_control.json"
        try:
            if os.path.isfile(file_path):
                with open(file_path, 'r') as json_file:
                    self.dictionary = json.load(json_file)[self.original_url]
            else:
                raise "The control file was not found. Please run the replay 0 option."

            return 1
        except KeyError as k:
            print(f"site not found in json --- site:{self.original_url}, extn:{self.adBlocker_name}, html: {self.html_elem}")
            return 0
        except Exception as e:
            print(f"Failed Replay-initialization for {self.current_url}")
            print(e)
            return 0

    def is_loaded(self):
        """
            Final check to see if the webpage has fully loaded.
        """
        return self.driver.execute_script("return document.readyState") == "complete"

    def wait_until_loaded(self, timeout=60, period=0.25, min_time=0):
        """
            Waits for the webpages to load with a certain timeout. Checks the is_loaded function
            to determine if it has loaded.
        """
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
            loads the webpage and scrolls to the bottom of the page (lazy loading) to ensure all resources
            have been loaded.
        """
        try:
            if not self.driver:
                print("No driver!!")
                return False
            self.driver.get(url)
            self.wait_until_loaded()

            # added scroll because of lazy loading
            self.scroll()
            time.sleep(2)

            self.current_url = self.driver.current_url
            self.page_source = self.driver.execute_script("return document.documentElement.outerHTML;")
            return True

        except Exception as e:
            print("Failed to load_site()")
            print(e)
            return False

    def reinitialize(self):
        """
           reinitialized the driver in case selenium crashes trying to perform the specified actions.
        """
        self.driver.close()
        self.initialize(self.options, 3, self.original_url)

    def scroll(self, speed=0.1):
        """
           function used to scroll the webpage
        """
        curr_scroll_position = -1
        curr_time = time.time()
        while True:
            scroll_step = 50  # Adjust this value to control the scroll speed
            scroll_position = self.driver.execute_script("return window.pageYOffset;")
            if curr_scroll_position == scroll_position:
                break
            else:
                curr_scroll_position = scroll_position
            self.driver.execute_script(f"window.scrollBy(0, {scroll_step});")

            time.sleep(speed)
            if time.time() - curr_time >= 45:
                break

    def take_ss(self, fname):
        """
           takes a screenshot of the current webpage. Used primarily for debugging
        """
        try:
            if '//' in fname:
                fname = fname.split('//')[1]
            filepath = f'screen_shots'
            if not os.path.isdir(filepath):
                os.makedirs(filepath, exist_ok=True)
            if self.driver:
                self.driver.save_screenshot(f'{filepath}/{fname}')
        except Exception as e:
            # not that serious if it cannot take the screen shot
            print(f"error taking screen shot for {self.current_url}")

    def get_logs(self):
        """
           Used for retrieving the logs for loading the website. Used primarily for debugging
        """
        if not self.driver:
            print("couldn't get the logs, driver = None")
            return None
        return self.driver.get_log('browser')

    def close(self):
        """
           Used to close the driver instance. Used for clean up
        """
        print("closing driver...", self.adBlocker_name, self.html_elem, self.current_url)
        if self.driver:
            self.driver.quit()

    def click_button(self, button):
        """
            Used to click on the button
        """
        try:
            self.actions.move_to_element(button).perform()
            button.click()
        except Exception:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });", button)
            time.sleep(2)
            button.click()

    def cursor_change(self, element):
        """
           Checks to see if the cursor has changed to a pointer. Used as the primary filter to testing
           if an identified element if 'interactable' or not.
        """
        try:
            self.actions.move_to_element(element).perform()
            time.sleep(1)
            cursor_property = element.value_of_css_property('cursor')
            if cursor_property == 'pointer':
                return True
            else:
                return False
        except Exception as e:
            return False

    def check_redirect(self, url):
        """
            Used to check if interacting with the element causes the browser to go to another link
        """
        def are_urls_equal(url1, url2):
            parsed_url1 = urlparse(url1)
            parsed_url2 = urlparse(url2)

            # Remove trailing slash if present
            path1 = parsed_url1.path.rstrip("/")
            path2 = parsed_url2.path.rstrip("/")

            return (parsed_url1.scheme, parsed_url1.netloc, path1) == (parsed_url2.scheme, parsed_url2.netloc, path2)

        time.sleep(3)
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
        """
            counts the number of tags in the DOM. 
        """
        soup = BeautifulSoup(self.page_source, 'html.parser')
        tags = soup.find_all()
        return len(tags)

    def get_local_DOM(self, elem, level=None):
        """
            given the element, it will go X levels up the DOM tree and return the HTML.
        """
        amt = self.DOM_traversal_amt
        if level:
            amt = level
        try:
            for i in range(amt):
                elem = elem.find_element(By.XPATH, '..')
            return elem.get_attribute('outerHTML')
        except Exception:
            return elem.get_attribute('outerHTML')

    def check_opened(self, url, button):
        """
            checks to see if clicking on the button has caused any change
        """
        def check_HTML(initial, after):
            if initial != after:
                return True
            return False

        redirect, new_url = self.check_redirect(url)
        if redirect:
            self.result = "True - Redirect"
            return

        try:
            self.after_outer_html = button.get_attribute('outerHTML')
        except StaleElementReferenceException:
            # this is good, means that the button disappeared after clicking
            # could be things like "close", "search", "expand", "show more", etc.
            self.result = "True - Stale Element"
            return

        self.DOM_changed = check_HTML(self.initial_local_DOM, self.get_local_DOM(button))
        self.outer_HTML_changed = check_HTML(self.initial_outer_html, self.after_outer_html)

        if self.outer_HTML_changed:
            self.result = "True - outerHTML change"

        elif self.DOM_changed:
            self.result = "True? - Local DOM Change"

        elif self.count_tags() > self.initial_tag:
            self.result = "True - More Tags"

        else:
            self.result = "Check Filters"

    # @timeout(300)
    def test_button(self):
        """
            Interacts with the elements and tests to see if there is any change before and after
        """
        for i in range(self.tries):
            try:
                self.initial_outer_html = self.dictionary[self.original_url][self.elem_indx]
                xpath = self.generate_xpath(self.initial_outer_html)
            except Exception as e:
                # print(e)
                # error(self.original_url, self.html_elem, inspect.currentframe().f_code.co_name, e)
                print("\nUnknown exception while loading outerHTML\n")
                print(e)
                return

            element = self.get_correct_elem(xpath, self.initial_outer_html)
            if not element:
                return

            self.initial_local_DOM = self.get_local_DOM(element)
            self.initial_tag = self.count_tags()

            if self.html_elem == 'input':
                self.initial_manual = self.page_source
                self.find_and_submit_forms(self.original_url, self.initial_outer_html)
            else:
                self.initial_manual = self.get_local_DOM(element, 13)
                self.click_button(element)
                self.check_opened(self.current_url, element)

            if 'true' in self.result.lower():
                self.final_result = [self.result, self.initial_outer_html, '']

            else:
                # Filter Functions
                if self.is_slideshow(self.initial_outer_html):
                    self.check = 'True? - slideshow'
                elif self.is_required(self.initial_outer_html):
                    self.check = 'True? - input is required'
                elif self.is_scrollpage(self.initial_outer_html):
                    self.check = 'True? - page was scrolled'
                elif self.is_download_link(self.initial_outer_html):
                    self.check = 'True? - download link'
                elif self.is_open_application(self.initial_outer_html):
                    self.check = 'True? - opened application'

                if self.result == 'False':
                    check = "False - double checked"
                else:
                    # reinitialize the driver and try again
                    self.result = 'False'
                    self.elem_indx -= 1
                    self.reinitialize()
                    return

                self.manual_change = (self.initial_manual != self.after_manual)
                self.final_result.append([check, self.initial_outer_html, self.manual_change])

    def click_on_elms(self):
        """
            loops through the elements the page and calls the test_button to test them
        """
        while self.elem_indx > len(self.dictionary[self.original_url]):
            self.test_button()
            self.elem_indx += 1

    ############################################################

    """            
            FINDING AND FILTERING THE HTML Elements
    """

    ############################################################
    def scan_page(self):
        """
            loads the website, finds, then filters the HTML elements identified on the
            page.
        """
        self.load_site(self.current_url)  # extra refresh helps get rid of some false findings
        self.get_elements()
        self.final_result = self.chosen_elms

        print("*" * 50)
        print(self.original_url, self.final_result)
        print("*" * 50)

    def get_elements(self):
        # returns the contents (will be selenium objs)
        ret = []
        if self.html_elem == "drop downs":
            ret = self.find_dropdown()
        elif self.html_elem == "buttons":
            ret = self.find_buttons()
        elif self.html_elem == "links":
            ret = self.find_links()
        elif self.html_elem == "login":
            ret = self.find_login()
        elif self.html_elem == "input":
            ret = self.find_forms()
        else:
            print("Invalid Element type to retrieve")

        unique = []
        for elem in ret:
            if self.html_elem == 'links' and len(unique) > 15:
                break
                
            if elem.get_attribute("outerHTML") not in unique:
                if not self.filter(elem):
                    continue
            unique.append(elem.get_attribute("outerHTML"))

        self.chosen_elms = unique

    def generate_xpath(self, html_string):
        """
            given the HTML_string, this will construct a xpath strings so that selenium will be able
            to locate the element.
        """
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

    def get_correct_elem(self, xpath, outerHTML):
        """
            given the xpath and the outerHTML, this will help selenium identify the correct element.
        """
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
            print(str(e).split("\n")[0])
            print(str(e).split("\n")[0])
            print(str(e).split("\n")[0])
            print("Didn't find element--", self.current_url)
            print("Didn't find element--", self.current_url)
            print(outerHTML)
            print("Didn't find element--", self.current_url)
            print("Didn't find element--", self.current_url)
        return None

    def filter(self, element):
        if self.html_elem == 'input':
            return True
        
        if self.html_elem == "login":
            if any(keyword.lower() in element.text.lower() for keyword in self.keywords):
                if self.cursor_change(element):
                    print(f"{self.current_url} \t {element.text}")
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
                            if self.html_elem == "buttons" and "href" not in element.get_attribute("outerHTML"):
                                found_elements.append(element)
                            else:
                                found_elements.append(element)
                except Exception as e:
                    print(f"Could not find {self.html_elem} in {self.original_url}")
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
        except Exception:  # not tested
            try:
                time.sleep(5)
                return collect()
            except Exception as e:
                print(f"Could not get {self.html_elem} for {self.original_url}")
                print(e)

    def find_dropdown(self):
        try:
            ret = self.specific_element_finder()
            return ret
        except Exception:
            try:
                time.sleep(5)
                return self.specific_element_finder()
            except Exception as e:
                print(f"Could not get {self.html_elem} for {self.original_url}")
                print(e)

    def find_links(self):
        def collect():
            black_list = ['#', '/', self.current_url]
            final = []
            for anchor in self.driver.find_elements(By.TAG_NAME, 'a'):
                if anchor.get_attribute("href") not in black_list:
                    final.append(anchor)

            return final

        try:
            ret = collect()
            return ret
        except Exception:
            try:
                time.sleep(5)
                return collect()
            except Exception as e:
                print(f"Could not get {self.html_elem} for {self.original_url}")
                print(e)

    def find_login(self):
        def collect():
            found_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            found_elements += self.driver.find_elements(By.TAG_NAME, 'a')
            final = self.specific_element_finder(found_elements)
            return final

        try:
            ret = collect()
            return ret
        except Exception:
            try:
                time.sleep(5)
                return collect()
            except Exception as e:
                print(f"Could not get {self.html_elem} for {self.original_url}")
                print(e)
                
    def find_forms(self):
        try:
            ret = self.driver.find_elements(By.TAG_NAME, 'form')
            return ret
        except Exception:
            try:
                time.sleep(5)
                return self.driver.find_elements(By.TAG_NAME, 'form')
            except Exception as e:
                print(f"Could not get {self.html_elem} for {self.original_url}")
                print(e)
                

    ############################################################

    """            
            Filters to check edge cases when interacting
            with the element.
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
            '.html', '.ico', '.iso', '.java', '.jpeg', '.jpg', '.js', '.json', '.log', '.m4a',
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


    ############################################################

    """            
            Functions for Testing Forms (inputs)
    """

    ############################################################

    def generate_path(self, html_code):
        soup = BeautifulSoup(html_code, 'html.parser')
        tag = soup.find()
        tag_name = tag.name
        attributes = tag.attrs
        return tag_name, attributes

    def find_and_submit_forms(self, url, form_html):
        if form_html not in self.page_source:
            return

        input_flag = False

        final_element = None

        xpath = self.generate_xpath(form_html)
        form_elem = self.get_correct_elem(xpath, form_html)

        soup = BeautifulSoup(form_html, "html.parser")
        text_inputs = soup.find_all("input", {"type": "text"})
        text_inputs += soup.find_all("input", {"type": "search"})
        text_inputs += soup.find_all("input", {"type": "password"})
        text_inputs += soup.find_all('textarea')

        email_inputs = soup.find_all("input", {"type": "email"})

        number_inputs = soup.find_all("input", {"type": "tel"})

        input_flag, final_element = self.enter_form(text_inputs, "test", final_element, input_flag)
        input_flag, final_element = self.enter_form(email_inputs, "test@gmail.com", final_element, input_flag)
        input_flag, final_element = self.enter_form(number_inputs, "1112223333", final_element, input_flag)

        if input_flag:  # if we inputted data, now we submit it:
            final_element, submit_flag = self.submit_form(form_elem, final_element)

            if submit_flag:
                self.check_opened(url, final_element)
        else:
            self.result = "False"

    def enter_form(self, input_boxes, msg, final_element, input_flag):
        for input in input_boxes:
            xpath = self.generate_xpath(input)
            element = self.get_correct_elem(xpath, input)
            self.filter(element)

            # Just in case we can't find the submit button
            final_element = element

            try:
                self.click_button(element)
            except Exception as e:
                # this is not that important ... just needs to send the inputs
                error_flag = True

            try:
                element.send_keys(msg)
                input_flag = True
            except Exception as e:
                error = str(e).split("\n")[0]
                print(error, element.get_attribute("outerHTML"))
                continue

        return input_flag, final_element

    def submit_form(self, form_elem, final_element):
        html = self.get_local_DOM(form_elem, 2)
        soup = BeautifulSoup(html, "html.parser")
        submit_elements = soup.find_all(lambda tag: tag.get("type") == "submit")
        submitted = False
        if not submit_elements:  # if I cannot find the enter button, just hit enter
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.RETURN)
            actions.perform()
            submitted = True

        for submit in submit_elements:
            xpath = self.generate_xpath(submit)
            element = self.get_correct_elem(xpath, submit)
            try:
                self.click_button(element)
                submitted = True
            except Exception as e:
                try:
                    # if I cannot find the enter button, just hit enter
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.RETURN)
                    actions.perform()
                    submitted = True
                except Exception as e:
                    error = str(e).split("\n")[0]
                    print(error, element.get_attribute("outerHTML"))
            final_element = element
        return final_element, submitted

