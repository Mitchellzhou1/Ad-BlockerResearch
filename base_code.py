from time import sleep
from Excel import *
import os
import pyautogui
import requests
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
        self.attributes = []
        self.xpaths = []

        self.initial_url = ''
        self.driver = None
        self.skipped = []
        self.errors = []
        self.could_not_scan = []
        self.timeout = []
        self.intercept = []
        self.tries = 1
        self.seen_sites = []

        self.icon = 0
        self.initial_html = ''
        self.after_outer_html = ''

    def initialize(self, adblocker='', seconds=14):
        """
            This function will start a Chrome instance with the option of installing an ad blocker.
            Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        extensions_dir = os.path.abspath(os.path.join(current_dir, 'Extensions', 'Ad-Blockers'))
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_extension('Captcha-Solver-Auto-Recognition-and-Bypass.crx')
        if adblocker == 'AdBlockPlus':
            extension_path = os.path.join(extensions_dir, 'adBlockerPlus.crx')
            chrome_options.add_extension(extension_path)
        elif adblocker == 'uBlock':
            extension_path = os.path.join(extensions_dir, 'uBlock-Origin.crx')
            chrome_options.add_extension(extension_path)

        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.set_window_size(1555, 900)
        # give it time to install
        if adblocker == 'AdBlockPlus':
            sleep(seconds)
            pyautogui.hotkey('ctrl', 'w')

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
                self.driver.get(url)
                wait = WebDriverWait(self.driver, self.tries * 5)
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, "//*")))
                    self.initial_url = url
                    if url not in self.seen_sites:
                        self.seen_sites.append(url)
                        write_results(url)
                    sleep(self.tries * 5)
                    return True
                except TimeoutException:
                    raise TimeoutError("Took too long to load...")
        except Exception as e:
            self.skipped.append(url)
            return False

    def cursor_change(self, element):
        actions = ActionChains(self.driver)
        try:
            actions.move_to_element(element).perform()
            cursor_property = element.value_of_css_property('cursor')
            if cursor_property == 'pointer':
                return True
            else:
                return False
        except Exception as e:
            self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
            if element.is_displayed():
                return True
            else:
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

    def find_dropdown(self, attributes, xpaths):
        def collect():
            found_elements = []
            for attribute in attributes:
                for path in xpaths:
                    xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element not in found_elements:
                                found_elements.append(element)
                    except Exception as e:
                        print(e)

            if len(found_elements) > 1:
                found_elements.sort(key=lambda e: self.driver.execute_script(
                    "var elem = arguments[0], parents = 0; while (elem && elem.parentElement) { elem = elem.parentElement; parents++; } return parents;",
                    e
                ))

            return found_elements

        try:
            ret = collect()
            if ret:
                return ret
        except Exception:
            pass

        sleep(5)
        return collect()

    def check_opened(self, url, button, initial_html, initial_tag, entire_html):
        def check_HTML(initial, after):
            if initial != after:
                return True
            return False

        redirect, new = self.check_redirect(url)
        if redirect:
            return "True - redirect", new

        after_outer_html = button.get_attribute('outerHTML')

        DOM_change = check_HTML(entire_html, self.driver.page_source)

        if check_HTML(initial_html, after_outer_html):
            return f"True - outerHTML change\n{DOM_change} - DOM change", after_outer_html

        if self.count_tags() > initial_tag:
            return f"True - More tags were generated\n{DOM_change} - DOM change", after_outer_html
        return f"False - outerHTML didn't change\n{DOM_change} - DOM change", after_outer_html

    def test_drop_down(self, curr, url, tries=1):
        # attempts to click the button and refreshes afterward

        seen = []
        while self.icon < len(curr):
            try:
                outer_html = curr[self.icon].get_attribute('outerHTML')
                entire_html = self.driver.page_source

            except Exception as e:
                self.icon += 1
                continue

            if not self.cursor_change(curr[self.icon]):
                self.icon += 1
                continue

            for prev in seen:
                if outer_html in prev:
                    self.icon += 1
                    continue
            print(outer_html)
            initial_tag = self.count_tags()
            curr[self.icon].click()

            check, after_html = self.check_opened(url, curr[self.icon], outer_html, initial_tag, entire_html)
            # if check == "False":
            #     raise InterruptedError

            self.load_site(url)
            curr = self.find_dropdown(self.attributes, self.xpaths)

            if check == "True - redirect":
                write_results([check, url, after_html, tries])
            else:
                write_results([check, outer_html, after_html, tries])

            seen.append(outer_html)

            self.icon += 1
        self.icon = 0

    def reinitialize(self):
        self.driver.close()
        self.initialize("uBlock")
        self.tries += 1


shared_driver = Driver()

