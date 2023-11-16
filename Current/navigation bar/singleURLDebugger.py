from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import *

import pyautogui

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

sites = ['https://en.wikipedia.org/wiki/Main_Page',
         'https://www.amazon.com/',
         'https://www.microsoft.com/en-us/',
         'https://www.office.com/',
         'https://openai.com/',
         'https://www.bing.com/',
         'https://duckduckgo.com/',
         'https://weather.com/',
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
    'ctabutton'
]

xpaths = [
    '@aria-expanded',
    '@aria-label',
    '@class',
    '@aria-haspopup',
    '@aria-describedby',
    '@data-testid'
]

adBlockerIDs = {"adblockPlus": 'cfhdojbkjhnklbpkdaibdccddilifddb'}


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


def load_site(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*")))


def find_dropdown(driver):
    def find():
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

            # if len(found_elements) > 1:
            found_elements.sort(key=lambda e: driver.execute_script(
                "var elem = arguments[0], parents = 0; while (elem && elem.parentElement) { elem = elem.parentElement; parents++; } return parents;",
                e
            ))

        return found_elements

    # some websites take forever to load the contents correctly --> weather.com  >:(
    try:
        sleep(4)
        return find()
    except Exception:
        sleep(15)
        return find()


def cursorChange(element, driver):
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


def check_redirect(driver, url):
    if driver.current_url != url:
        load_site(driver, url)

    all_windows = driver.window_handles
    if len(all_windows) > 1:
        for window in all_windows[1:]:
            driver.switch_to.window(window)
            driver.close()
        driver.switch_to.window(all_windows[0])


def printer(lst, msg):
    print("\n\n", msg)
    for i in lst:
        print(i)


def print_found_elems(lst):
    for i in lst:
        outer_html = i.get_attribute('outerHTML')
        first_line = outer_html.splitlines()[0]
        print(first_line)
        # print(i)


def collect_data(file, data):
    ...


def intercept_handler(driver, curr, icon):
    def click_corners():
        window_width = driver.execute_script("return window.innerWidth;")
        window_height = driver.execute_script("return window.innerHeight;")

        x_coordinate_left = 0
        y_coordinate = window_height

        x_coordinate_right = window_width

        action = ActionChains(driver)
        action.move_to_element_with_offset(driver.find_element_by_tag_name('body'), x_coordinate_left,
                                           y_coordinate).click().perform()

        action.move_to_element_with_offset(driver.find_element_by_tag_name('body'), x_coordinate_right,
                                           y_coordinate).click().perform()

    try:
        curr[icon - 1].click()
        pyautogui.press('esc')
    except ElementClickInterceptedException:
        click_corners()

    except Exception:
        driver.refresh()
        sleep(5)
        return find_dropdown(driver)
    return curr, icon - 1


def main():
    driver = webdriver.Chrome()
    driver.set_window_size(1555, 900)
    errors = []
    could_not_scan = []
    site_results = []
    sites = ['https://www.microsoft.com/en-us/']
    for url in sites:
        print("\n", url)
        load_site(driver, url)
        icon = 0
        curr = find_dropdown(driver)
        print_found_elems(curr)
        while icon != len(curr):
            # sometimes the elements disappear
            try:
                outer_html = curr[icon].get_attribute('outerHTML')
                first_line = outer_html.splitlines()[0]
            except Exception as e:
                site_results.append([url, e])
                icon += 1
                continue

            try:
                if not cursorChange(curr[icon], driver):
                    icon += 1
                    continue
                print("clicking on:", first_line)
                curr[icon].click()
                sleep(2)
                check_redirect(driver, url)
            except ElementClickInterceptedException:
                curr, icon = intercept_handler(driver, curr, icon)
            except Exception as e:
                errors.append(f"{e} \t\t {url} \t\t {first_line}")
            icon += 1
            # driver.refresh()
        site_results.append([url, 'success'])

    printer(errors, "Errors")
    printer(could_not_scan, "Failed to collect on Site")
    print("DONE")


main()

while 1:
    1
