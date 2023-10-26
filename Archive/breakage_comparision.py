import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pyautogui
import openpyxl

source = ["https://www.forbes.com/"]
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

    #give it time to install
    if adblocker:
        time.sleep(seconds)
        pyautogui.hotkey('ctrl', 'w')
        
    return driver


def grab_sections(html):
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all('div')
    return elements


def get_source_code(driver, website):
    driver.get(website)
    page_source = driver.page_source
    return page_source


def same_section(adblocker, regular):
    return adblocker[5:adblocker.find(">")] == regular[5:regular.find(">")]


def get_difference(adblocker, regular, data):
    # I am going under the assumption that the non-adblocker HTML code is
    # always longer than the HTML that elements blocked
    if len(adblocker) > len(regular):
        print("Wierd!!!! Not suppose to happen!!!!")
    else:
        i = j = 0
        while i < len(regular):
            # we are looking at the same part of the website
            if same_section(adblocker[i], regular[j]):
                if adblocker[i] == regular[j]:
                    i += 1
                    j += 1
                else:
                    data['dropped'].append(regular[i])

            else:
                i += 1



def main():

    data = {
        'dropped': [],
        'changed': []
    }

    reg_browser = initialize(False)
    abp_browser = initialize(True)
    
    for website in source:
        abp_code = grab_sections(get_source_code(abp_browser, website))
        reg_code = grab_sections(get_source_code(reg_browser, website))
        get_difference(abp_code, reg_code, data)

        # for x, div in enumerate(abp_code):
        #     print(f"{x}     \n  {div.prettify()}\n\n")
        # reg_code = grab_sections(get_source_code(reg_browser, website))
        # print(type(reg_code))
    
    input("Press Enter to exit")
    
    reg_browser.quit()
    abp_browser.quit()


if __name__ == "__main__":
    main()
