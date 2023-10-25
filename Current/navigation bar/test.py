from selenium import webdriver
from selenium.webdriver.common.by import By
from time import *

driver = webdriver.Chrome()
driver.set_window_size(1080,800)

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

attributes = ['main menu',
              'open menu',
              'all microsoft menu',
              'menu',
              'navigation',
              'hamburger',
              'false',
              'true']

for url in sites:
    worked = False
    driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
    driver.get(url)
    sleep(3)
    for attribute in attributes:
        xpath = f'//*[translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
        try:
            found_element = driver.find_element(By.XPATH, xpath)
            found_element.click()
            print("clicked on the drop down for", url)
            worked = True
            break
        except Exception:
            ...
    if not worked:
        print(url, "DID NOT WORK!!!")
    sleep(3)

while 1:
    1
