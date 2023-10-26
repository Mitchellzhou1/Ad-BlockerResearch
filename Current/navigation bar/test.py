from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import *
from tranco import Tranco
import pyautogui

driver = webdriver.Chrome()
driver.set_window_size(1335,822)



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

curr_test = ['https://www.amazon.com/']

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
              'js-menu-toggle']

xpaths = [ '@aria-expanded',
           '@aria-label',
           '@class',
           '@aria-haspopup'
]


def load_site(url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//*")))


def find_dropdown():
    def resize_window():
        driver.set_window_size(800, 800)

    found_element = []
    for i in range(1):
        for attribute in attributes:
            for path in xpaths:
                xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
                try:
                    found_element += driver.find_elements(By.XPATH, xpath)
                except Exception:
                    ...
    return found_element
    #     resize_window()
    # driver.set_window_size(1024, 768)


def testing(lst, url):
    print(f"Found {len(lst)} elements for {url}")
    # for i in lst:
    #     print(i.get_attribute('outerHTML')



def main():
    for url in sites:
        worked = 0
        load_site(url)
        for icon in find_dropdown():
            # testing(find_dropdown(), icon)
            try:
                icon.click()
                print("clicked on the drop down for", url)
                sleep(2)
                pyautogui.press('esc')
                worked += 1
                sleep(1)
            except Exception:
                ...

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