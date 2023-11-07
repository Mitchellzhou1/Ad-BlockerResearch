from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import *
import pyautogui


def cursorChange(element, driver):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    cursor_property = element.value_of_css_property('cursor')
    if cursor_property == 'pointer':
        return True
    else:
        return False

# Assuming you have your WebDriver set up (e.g., ChromeDriver)
driver = webdriver.Chrome()

# Replace 'https://example.com' with the URL of the webpage containing the checkbox
driver.get("https://en.wikipedia.org/wiki/Main_Page")

xpath = '//*[@id="vector-main-menu-dropdown-checkbox"]'

# Find all elements matching the XPath
elements = driver.find_element(By.XPATH, xpath)
print(f"visible: {elements.is_displayed()}")
print(f"cursor change: {cursorChange(elements, driver)}")

# Check if the checkbox is selected, and if not, click it to select

elements.click()

while 1:
    1