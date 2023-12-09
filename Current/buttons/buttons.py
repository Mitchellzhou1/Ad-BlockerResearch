from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from time import *
from bs4 import BeautifulSoup
import requests
import random

import pyautogui
import signal
from Current.Excel import *

# Prepare Chrome
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
# options.add_extension("/home/seluser/measure/harexporttrigger-0.6.3.crx")

# adBlockerIDs = {"adblockPlus": 'cfhdojbkjhnklbpkdaibdccddilifddb'}


sites = [
    'https://en.wikipedia.org/wiki/Main_Page',
    'https://www.amazon.com/',
    'https://www.microsoft.com/en-us/',
    'https://www.office.com/',
    'https://weather.com/',
    'https://openai.com/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
    'https://cnn.com',
    'https://www.nytimes.com/',
    'https://www.twitch.tv/',
    'https://www.imdb.com/',
    'https://mail.ru/',
    'https://naver.com',
    'https://zoom.us/',
    'https://www.globo.com/',
    'https://www.ebay.com/',
    'https://www.foxnews.com/',
    'https://www.instructure.com/',
    'https://www.walmart.com/',
    'https://www.indeed.com/',
    'https://www.paypal.com/us/home',
    'https://www.accuweather.com/',
    'https://www.pinterest.com/',
    'https://www.bbc.com/',
    'https://www.homedepot.com/',
    'https://www.breitbart.com/',
    'https://github.com/'
]

driver = None
icon = 0
outer_html = ''
after_html = ''
global_url = ''

class TimeoutError(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeoutError("Function execution time exceeded the limit")


def initialize(adblocker, seconds=14):
    """
    This function will start a Chrome instance with the option of installing an ad blocker.
    Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
    """
    chrome_options = webdriver.ChromeOptions()

    if adblocker:
        chrome_options.add_extension('adBlockerPlus.crx')

    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # give it time to install
    if adblocker:
        sleep(seconds)
        pyautogui.hotkey('ctrl', 'w')

    return driver



def load_site(url, skipped=[]):
    #url = f'https://www.{url}'
    global global_url
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            driver.get(url)
            wait = WebDriverWait(driver, 15)  # Changed timeout to 15 seconds
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//*")))
                global_url = driver.current_url
                return True
            except TimeoutException:
                raise TimeoutError("Took too long to load...")
    except Exception as e:
        skipped.append(url)
        return False


def count_tags():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tags = soup.find_all()
    return len(tags)


def find_dropdown():
    def collect():
        ret = []
        ret += driver.find_elements(By.TAG_NAME, 'button')
        ret += driver.find_elements(By.XPATH, "//a[@href]")
        return ret

    try:
        ret = collect()
        if ret:
            return ret
    except Exception:
        pass

    sleep(5)
    return collect()


def cursor_change(element):
    actions = ActionChains(driver)
    try:
        actions.move_to_element(element).perform()
        cursor_property = element.value_of_css_property('cursor')
        if cursor_property == 'pointer':
            return True
        else:
            return False
    except Exception as e:
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
        if element.is_displayed():
            return True
        else:
            return False


def check_redirect(url):
    def are_urls_equal(url1, url2):
        path1 = url1.rstrip('/').strip('https://').strip('www.')
        path2 = url2.rstrip('/').strip('https://').strip('www.')
        return path1 == path2

    sleep(3)
    if not are_urls_equal(driver.current_url, url):
        return True, driver.current_url

    all_windows = driver.window_handles
    if len(all_windows) > 1:
        for window in all_windows[1:]:
            driver.switch_to.window(window)
            driver.close()
        driver.switch_to.window(all_windows[0])
        return True, driver.current_url
    return False, driver.current_url

########################################################################################################################

def check_opened(url, button, initial_html, initial_tag, entire_html):
    def check_HTML(initial, after):
        if initial != after:
            return True
        return False

    redirect, new = check_redirect(url)
    if redirect:
        return "True - redirect", new

    after_outer_html = button.get_attribute('outerHTML')

    DOM_change = check_HTML(entire_html, driver.page_source)

    if check_HTML(initial_html, after_outer_html):
        return f"True - outerHTML change\n{DOM_change} - DOM change", after_outer_html

    if count_tags() > initial_tag:
        return f"True - More tags were generated\n{DOM_change} - DOM change", after_outer_html
    return f"False - outerHTML didn't change\n{DOM_change} - DOM change", after_outer_html


def test_drop_down(curr, url, tries=1):
    # attempts to click the button and refreshes afterward
    global driver, icon, outer_html, after_html
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(100)

    seen = []
    while icon < len(curr):
        try:
            outer_html = curr[icon].get_attribute('outerHTML')
            entire_html = driver.page_source

        except Exception as e:
            icon += 1
            continue

        if not cursor_change(curr[icon]):
            icon += 1
            continue

        for prev in seen:
            if outer_html in prev:
                icon += 1
                continue
        print(outer_html)
        initial_tag = count_tags()
        curr[icon].click()

        check, after_html = check_opened(url, curr[icon], outer_html, initial_tag, entire_html)
        # if check == "False":
        #     raise InterruptedError

        load_site(url)
        curr = find_dropdown()

        if check == "True - redirect":
            write_results([check, url, after_html, tries])
        else:
            write_results([check, outer_html, after_html, tries])

        seen.append(outer_html)

        icon += 1


def main():
    global driver, icon, outer_html, after_html
    errors, could_not_scan, timeout, intercept, skipped = [[] for _ in range(5)]
    driver = initialize(False)
    driver.set_window_size(1555, 900)
    #
    index = 0
    seen_sites = []
    tries = 1
    # sites = ['https://duckduckgo.com/']
    while index < len(sites):
        url = sites[index]
        try:
            if load_site(url, skipped):
                if url not in seen_sites:
                    seen_sites.append(url)
                    write_results(url)
                url = global_url
                sleep(tries * 5)
                print("\n", url)
                elms = find_dropdown()
                print(len(elms))
                test_drop_down(elms, url, tries)
                icon = 0
            else:
                write_noscan_row(url)
            index += 1
            tries = 1

        except Exception as e:
            if tries != 3:
                driver.close()
                driver = initialize(False)
                driver.set_window_size(1555, 900)
                tries += 1
                continue

            if isinstance(e, ElementClickInterceptedException):
                print("Element Click Intercepted")
                write_intercepts(url)
                write_results(["Failed - Element Click Intercepted", outer_html, after_html, tries])
            elif isinstance(e, TimeoutError):
                print("Timeout Error")
                write_timeout_row(url)
                write_results("Failed - Site Timeout Error")
            elif isinstance(e, ElementNotInteractableException):
                print("Not Interactable")
                write_notInteractable_row(url)
                write_results(["Failed - Not Interactable", outer_html])
            else:
                print(e)
                write_other_row(url)
                write_results(["Failed - unknown error", str(e).split("\n")[0]])
            icon += 1
            tries = 1
    print("\n\nFinished Testing on All Sites!\n\n\n")
    end()

main()

driver.close()
