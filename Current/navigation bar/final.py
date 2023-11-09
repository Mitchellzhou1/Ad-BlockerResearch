from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import *
import pyautogui

driver = webdriver.Chrome()
driver.set_window_size(1555,900)

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
              'searchDropdownDescription']

xpaths = [ '@aria-expanded',
           '@aria-label',
           '@class',
           '@aria-haspopup',
           '@aria-describedby'
]


def load_site(url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*")))

def find_dropdown():
    found_elements = []

    for i in range(1):
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
            "var elem = arguments[0], parents = 0; while (elem && elem.parentElement) { elem = elem.parentElement; parents++; } return parents;", e
        ))

    print(len(found_elements))
    return found_elements


def printer(list):
    print("\n")
    for i in list:
        print(i.get_attribute('outerHTML').splitlines()[0])

def falsePositive(html):
    traps = ['display: none', "vjs-hidden"]
    for i in traps:
        if i in html:
            return True
    return False

def redirect():
    #check tabs
    #check title
    ...



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


def main():
    errors = []
    curr_test = ['https://en.wikipedia.org/wiki/Main_Page']
    for url in sites:
        print("\n", url)
        load_site(url)
        for icon in find_dropdown():
            outer_html = icon.get_attribute('outerHTML')
            first_line = outer_html.splitlines()[0]
            try:
                icon.click()
                print("clicking on:", first_line)
                # sleep(2)
                pyautogui.press('esc')
            except Exception as e:
                if not cursorChange(icon, driver):
                    continue
                else:
                    errors.append(f"DOUBLE CHECK: {first_line}")

    print("\n\nERRORS!!!! ")

    for i in errors:
        print(i)

    print("DONE")

main()


while 1:
    1



# def works():
#     for url in sites:
#         worked = False
#         driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
#         driver.get(url)
#         wait = WebDriverWait(driver, 10)
#         wait.until(EC.presence_of_element_located((By.XPATH, "//*")))
#         for attribute in attributes:
#             for path in xpaths:
#                 xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
#                 try:
#                     found_element = driver.find_element(By.XPATH, xpath)
#                     found_element.click()
#                     print("clicked on the drop down for", url)
#                     worked = True
#                     break
#                 except Exception:
#                     ...
#             if worked:
#                 break
#         resize_window()
#         if not worked:
#             print(url, "DID NOT WORK!!!")
#         sleep(6)