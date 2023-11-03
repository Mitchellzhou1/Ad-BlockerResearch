from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import *
import pyautogui

driver = webdriver.Chrome()
driver.set_window_size(1555,900)

curr_test = ['https://en.wikipedia.org/wiki/Main_Page']

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

    print(len(found_elements))
    return found_elements


def falsePositive(html):
    traps = ['display: none', "vjs-hidden"]
    for i in traps:
        if i in html:
            return True
    return False


def main():
    errors = []
    for url in curr_test:
        invisible = []
        print("\n\n", url)
        worked = 0
        load_site(url)
        for icon in find_dropdown():
            outer_html = icon.get_attribute('outerHTML')
            first_line = outer_html.splitlines()[0]
            # if icon.is_displayed():
            try:
                print("clicking on:", first_line)
                icon.click()
                # sleep(8)
                pyautogui.press('esc')
                worked += 1
                sleep(1)
            except Exception as e:
                if falsePositive(first_line):
                    errors.append([url, first_line, str(e)[:35]])
                    print(first_line, "\n", str(e)[:35].strip())
            # else:
            #     invisible.append(first_line)
        print("\n\nINVISIBLE ELEMENTS!!!")
        for elem in invisible:
            print(elem)
    print("DONE")

main()


while 1:
    1

