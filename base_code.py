from time import sleep
import time
from Excel import *
import os
import pyautogui
import requests
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
        self.seen_sites = []
        self.website_sleep_time = 3        # longer this value, more consistent the results
        self.html_obj = 'buttons'

        # used for testing
        self.icon = 0
        self.initial_outer_html = ''
        self.after_outer_html = ''
        self.initial_DOM = ''
        self.after_DOM = ''
        self.url = ''
        self.redirect_url = ''
        self.DOM_changed = False
        self.outer_HTML_changed = False

        # used for random picking
        self.no_elms = 15
        self.chosen_elms = []



    def initialize(self, seconds=14):
        """
            This function will start a Chrome instance with the option of installing an ad blocker.
            Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extensions_dir = os.path.abspath(os.path.join(current_dir, 'Extensions', 'Ad-Blockers'))
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_extension('Captcha-Solver-Auto-Recognition-and-Bypass.crx')
        if self.adBlocker_name == 'AdBlockPlus':
            extension_path = os.path.join(extensions_dir, 'adBlockerPlus.crx')
            chrome_options.add_extension(extension_path)
        elif self.adBlocker_name == 'uBlock':
            extension_path = os.path.join(extensions_dir, 'uBlock-Origin.crx')
            chrome_options.add_extension(extension_path)

        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.set_window_size(1555, 900)
        # give it time to install
        if self.adBlocker_name == 'AdBlockPlus':
            sleep(seconds)
            pyautogui.hotkey('ctrl', 'w')

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
        def helper(url):
            if url[:4] != 'http':
                return f'http://www.{url}'
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

                    # wait = WebDriverWait(self.driver, self.tries * 5)
                    # wait.until(EC.presence_of_element_located((By.XPATH, "//*")))
                    # sleep(self.website_sleep_time)                                      # increasing sleep time gives more consistent results
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
            sleep(1)
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

        parsed_info = parse_html_string(html_string)
        if parsed_info:
            tag_name = parsed_info['tag_name']
            attributes = parsed_info['attributes']

            xpath = f'//{tag_name}'
            for attr, value in attributes.items():
                if attr != 'class':  # Exclude 'class' attribute
                    if isinstance(value, list):
                        xpath += f'[@{attr}="{value[0]}"]'
                    else:
                        xpath += f'[@{attr}="{value}"]'

            return xpath
        return None

    def check_opened(self, url, button, initial_tag):
        def check_HTML(initial, after):
            if initial != after:
                return True
            return False

        redirect, new_url = self.check_redirect(url)
        if redirect:
            return "True - Redirect"

        self.after_outer_html = button.get_attribute('outerHTML')

        self.DOM_changed = check_HTML(self.initial_DOM, self.driver.page_source)
        self.outer_HTML_changed = check_HTML(self.initial_outer_html, self.after_outer_html)

        if self.outer_HTML_changed:
            return "True - outerHTML change"

        if self.DOM_changed:
            return "True? - DOM Change"

        if self.count_tags() > initial_tag:
            return "True - More Tags"

        return "False"

    def test_elms(self, html_obj, tries=1):
        # attempts to click the button and refreshes afterward
        while self.load_site(self.url):
            self.get_elements()
            add_to_csv(self.url, )


            # try:
            #     self.initial_outer_html = curr[self.icon].get_attribute('outerHTML')
            #     self.initial_DOM = self.driver.page_source
            #
            # except Exception as e:
            #     self.icon += 1
            #     continue
            #
            # # this is filter but may not need...
            # if not self.cursor_change(curr[self.icon]):
            #     self.icon += 1
            #     continue
            #
            # print("clicking on: ", self.initial_outer_html)
            # initial_tag = self.count_tags()
            #
            # actions = ActionChains(self.driver)
            # actions.move_to_element(curr[self.icon]).perform()
            # self.click_button(curr[self.icon])
            #
            # check = self.check_opened(self.url, curr[self.icon], initial_tag)
            #
            # if check == "True - Redirect":
            #     # outer_HTML_change = url
            #     # Dom_change = new_url
            #     write_results([check, '', '', self.initial_outer_html, '', '',  '',
            #                    self.url, self.driver.current_url, tries])
            # elif check == "True - outerHTML change":
            #     write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html,
            #                    self.after_outer_html, '',  '', '', '', tries])
            #
            # elif check == "True? - DOM Change":
            #     # need to figure out algo after find the difference
            #     write_results([check, self.outer_HTML_changed, self.DOM_changed, self.initial_outer_html, '',
            #                    "self.initial_DOM",  "self.after_DOM", '', '', tries])
            #
            # self.icon += 1
            #
            # if self.icon >= len(curr):
            #     self.icon = 0
            #     break

    def scan_page(self):
        self.get_elements()
        for HTML in self.chosen_elms:
            add_to_csv(self.url, ''.join(HTML.split("\n")), self.html_obj)

############################################################

    """            
            FINDING AND FILTERING THE HTML Elements
    """

############################################################
    def final_list(self, potential):
        self.chosen_elms = [elem.get_attribute("outerHTML") for elem in potential]
        self.chosen_elms = set(self.chosen_elms)



    def get_elements(self):
        # returns the contents (will be selenium objs)
        ret = []
        if self.html_obj == "drop downs":
            ret = self.find_dropdown()
        elif self.html_obj == "buttons":
            ret = self.find_buttons()
        # elif type == "links":
        #     ret = self.find_links()
        else:
            print("Invalid Element type to retrieve")

        self.final_list(ret)

        if len(self.chosen_elms) <= self.no_elms:
            write_results(f"testing {len(self.chosen_elms)} / {len(self.chosen_elms)}")
        else:
            self.chosen_elms = random.sample(self.chosen_elms, self.no_elms)
            write_results(f"testing {len(self.chosen_elms)} / {self.no_elms}")

    def filter(self, total):
        final = []
        for element in total:
            if self.cursor_change(element):
                final.append(element)

        if len(final) > 1:
            final.sort(key=lambda e: self.driver.execute_script(
                "var elem = arguments[0], parents = 0; while (elem && elem.parentElement) { elem = elem.parentElement; parents++; } return parents;",
                e
            ))
        return list(set(final))

    def specific_element_finder(self, found_elements=None):
        # will just add on to the current found_elements list.
        if not found_elements:
            found_elements = []
        for attribute in self.attributes:
            for path in self.xPaths:
                xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element not in found_elements:
                            if self.html_obj == "buttons" and "href" not in element.get_attribute("outerHTML"):
                                found_elements.append(element)
                        else:
                            found_elements.append(element)
                except Exception as e:
                    print(e)

        if len(found_elements) > 1:
            found_elements.sort(key=lambda e: self.driver.execute_script(
                "var elem = arguments[0], parents = 0; while (elem && elem.parentElement) { elem = elem.parentElement; parents++; } return parents;",
                e
            ))
        return found_elements

    def find_buttons(self):
        def collect():
            found_elements = self.driver.find_elements(By.TAG_NAME, 'button')
            for anchor in self.driver.find_elements(By.TAG_NAME, 'a'):
                if anchor.get_attribute("href") is None:
                    found_elements.append(anchor)

            final = self.specific_element_finder(found_elements)
            return self.filter(final)
        try:
            ret = collect()
            # for i in ret:
            #     print(i.get_attribute("outerHTML"))
            return ret
        except Exception as e:       # not tested
            try:
                sleep(5)
                return collect()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                write_results(error_message)

    def find_dropdown(self):
        try:
            ret = self.specific_element_finder()
            return self.filter(ret)
        except Exception as e:
            try:
                sleep(5)
                return self.specific_element_finder()
            except Exception as e:
                error_message = [str(e).split('\n')[0], "Failed to scrape Site", "", "", ""]
                write_results(error_message)


shared_driver = Driver()

