from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import *
import pyautogui

driver = webdriver.Chrome()

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

def find_dropdown(driver):
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

    return found_elements


driver = webdriver.Chrome()
driver.get("https://weather.com/")

curr = find_dropdown(driver)
i = 0
while i < len(curr):
    button_id = find_dropdown(driver)[i]
    button_id.click()  # Click on the button
    driver.refresh()  # Refresh the page
    i+=1

# Close the browser window
driver.quit()
