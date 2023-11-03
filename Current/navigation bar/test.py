from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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

curr_test = ['https://www.microsoft.com/en-us/']

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
    found_elements = set()
    found_elements_dict = {}

    for i in range(1):
        for attribute in attributes:
            for path in xpaths:
                xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    for element in elements:
                        # Add elements to a dictionary with their index in the DOM tree
                        found_elements_dict[element] = element.location_once_scrolled_into_view

                    found_elements.update(elements)
                except Exception as e:
                    print(e)

    # Sort elements based on their index in the DOM tree
    sorted_elements = sorted(found_elements, key=lambda element: driver.execute_script("return arguments[0].compareDocumentPosition(arguments[1]);", element, list(found_elements_dict.keys())[0]))

    return list(sorted_elements)


def falsePositive(html):
    traps = ['display: none'
    ]
    for i in traps:
        if i in html:
            return True
    return False


def main():
    errors = []
    for url in sites:
        print("\n\n", url)
        worked = 0
        load_site(url)
        for icon in find_dropdown():
            outer_html = icon.get_attribute('outerHTML')
            first_line = outer_html.splitlines()[0]
            try:
                icon.click()
                # print("clicked on the drop down for", url)
                sleep(2)
                pyautogui.press('esc')
                worked += 1
                sleep(1)
            except Exception as e:
                if falsePositive(first_line):
                    errors.append([url, first_line, str(e)[:35]])
                    print(first_line, "\n", str(e)[:35].strip())

        if not worked:
            print()
    sleep(5)

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