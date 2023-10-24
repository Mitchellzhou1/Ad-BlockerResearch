from selenium import webdriver
from selenium.webdriver.common.by import By
from time import *

driver = webdriver.Chrome()

driver.get("https://en.softonic.com/articles")

sites = ['https://en.wikipedia.org/wiki/Main_Page',
         ''





         ]







sleep(3)
try:
    menu_button1 = driver.find_element(By.CSS_SELECTOR, '[aria-label="Main menu"]')
    menu_button2 = driver.find_element(By.XPATH, '//button[@aria-label="Main menu"]')

    # Click the menu button
    menu_button2.click()


except Exception:
    print("Element with aria-label 'Main menu' not found.")

while 1:
    1

driver.quit()