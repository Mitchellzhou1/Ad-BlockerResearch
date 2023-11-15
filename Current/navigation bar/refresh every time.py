from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse
from time import *
import requests

import pyautogui
import signal
from tranco import Tranco

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

tag = ['button',
       'div',
       'input',
       'svg',
       'a'
       ]

attributes = [
    'false',
    'true',
    'main menu',
    'open menu',
    'all microsoft menu',
    'menu',
    'navigation',
    'primary navigation',
    'hamburger',
    'settings and quick links',
    'dropdown',
    'dialog',
    'js-menu-toggle',
    'searchDropdownDescription',
    'ctabutton',
    'legacy-homepage_legacyButton__oUMB9 legacy-homepage_hamburgerButton__VsG7q',
    'Toggle language selector',
    'Open Navigation Drawer',
    'guide',
    'Expand Your Library'
]

xpaths = [
    '@aria-expanded',
    '@aria-label',
    '@class',
    '@aria-haspopup',
    '@aria-describedby',
    '@data-testid',
]

driver = webdriver.Chrome()
driver.set_window_size(1555, 900)


class TimeoutError(Exception):
    pass


def signal_handler(signum, frame):
    raise TimeoutError("Function execution time exceeded the limit")


def load_site(url, skipped=[]):
    new_url = f'https://{url}'
    try:
        response = requests.get(new_url)
        if response.status_code == 200:
            driver.get(new_url)
            wait = WebDriverWait(driver, 15)  # Changed timeout to 15 seconds
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//*")))
                return True
            except TimeoutException:
                raise TimeoutError("Took too long to load...")
    except Exception:
        skipped.append(url)
        return False


def find_dropdown():
    def collect():
        found_elements = []
        for attribute in attributes:
            for path in xpaths:
                xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        if element not in found_elements:
                            found_elements.append(element)
                except Exception as e:
                    print(e)

        if len(found_elements) > 1:
            found_elements.sort(key=lambda e: driver.execute_script(
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


def cursorChange(element):
    actions = ActionChains(driver)
    try:
        actions.move_to_element(element).perform()
        cursor_property = element.value_of_css_property('cursor')
        if cursor_property == 'pointer':
            return True
        else:
            return False
    except Exception:
        if element.is_displayed():
            return True
        else:
            return False


def print_found_elems(lst):
    for i in lst:
        outer_html = i.get_attribute('outerHTML')
        first_line = outer_html.splitlines()[0]
        print(first_line)
        # print(i)


def check_redirect(url):
    def are_urls_equal(url1, url2):
        parsed_url1 = urlparse(url1)
        parsed_url2 = urlparse(url2)
        normalized_url1 = f"{parsed_url1.scheme}://{parsed_url1.netloc}"
        normalized_url2 = f"{parsed_url2.scheme}://{parsed_url2.netloc}"
        path1 = parsed_url1.path.rstrip('/')
        path2 = parsed_url2.path.rstrip('/')

        return normalized_url1 == normalized_url2 and path1 == path2

    # sleep(2)
    # if not are_urls_equal(driver.current_url, url):
    #     load_site(url)

    all_windows = driver.window_handles
    if len(all_windows) > 1:
        for window in all_windows[1:]:
            driver.switch_to.window(window)
            driver.close()
        driver.switch_to.window(all_windows[0])


def collect_data(file, data):
    ...


########################################################################################################################
def intercept_handler(curr, icon, url):
    # def click_corners():
    #     screen_width = driver.execute_script("return window.innerWidth;")
    #     screen_height = driver.execute_script("return window.innerHeight;")
    #
    #     actions = ActionChains(driver)
    #
    #     # print("Click on the bottom right corner")
    #     actions.move_by_offset(screen_width - 1, screen_height - 1)
    #     actions.click()
    #     actions.perform()
    #
    #     # print("Click on the bottom left corner")
    #     actions.move_by_offset(1 - screen_width, screen_height - 1)
    #     actions.click()
    #     actions.perform()

    # try:
    #     click_corners()
    #     curr[icon].click()
    #     check_redirect(url)
    # except ElementClickInterceptedException:
    try:
        curr[icon - 1].click()
    except Exception:
        load_site(url)
        print("couldn't resolve intercept error")
        return find_dropdown(), icon

    return curr, icon - 1


def test_drop_down_no_refresh(curr, errors, url, icon=0):
    while icon != len(curr):
        try:
            outer_html = curr[icon].get_attribute('outerHTML')
            first_line = outer_html.splitlines()[0]
        except Exception as e:
            icon += 1
            continue

        try:
            if not cursorChange(curr[icon]):
                icon += 1
                continue
            curr[icon].click()
            print("clicking on:", first_line)
            sleep(3)
            driver.refresh()
        except ElementClickInterceptedException:
            curr, icon = intercept_handler(curr[icon - 1], icon, url)
            print("Intercept Error")
        except Exception as e:
            errors.append(url)
        icon += 1


def test_drop_down(curr, errors, url, intercept, icon=0):
    # attempts to click the button and refreshes afterward
    global driver
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(100)

    while icon < len(curr):
        try:
            outer_html = curr[icon].get_attribute('outerHTML')
            first_line = outer_html.splitlines()[0]
        except Exception as e:
            icon += 1
            continue

        try:
            if not cursorChange(curr[icon]):
                icon += 1
                continue
            curr[icon].click()
            print("clicking on:", first_line)

            check_redirect(url)
            sleep(3)
            load_site(url)
            curr = find_dropdown()
        except ElementClickInterceptedException:
            curr, icon = intercept_handler(curr, icon, url)
            intercept.append(url)

        except Exception as e:
            errors.append(f"{url} \t\t {first_line}")
        icon += 1



def main():
    errors = []
    could_not_scan = []
    timeout = []
    intercept = []
    skipped = []

    t = Tranco(cache=True, cache_dir='.tranco')
    latest_list = t.list()
    sites = latest_list.top(10000)
    # sites = ['yandex.ru']
    for url in sites:
        # print_found_elems(find_dropdown(driver))
        try:
            if load_site(url, skipped):
                print("\n", url)
                elems = find_dropdown()
                test_drop_down(elems, errors, url, intercept)

        except TimeoutError:
            print("too long to load page")
            timeout.append(url)
        except ElementClickInterceptedException:
            print("Intercept Error")

        except Exception as e:
            # print(e)
            print("Something went wrong. Failed to scan page")
            could_not_scan.append(url)

    print("DONE!")


main()

while 1:
    1



# fastly.net: this website is broken
# yahoo.com: going on it on crawler is different then on browser
#  bit.ly   Message: no such execution context
# msn.com
# yandex.net
