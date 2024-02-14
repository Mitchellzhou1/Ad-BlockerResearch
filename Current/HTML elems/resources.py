from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up the WebDriver (you need to download the appropriate driver for your browser)
driver = webdriver.Chrome()

# Navigate to a webpage
driver.get("https://en.wikipedia.org/wiki/Main_Page")

try:
    # Find elements using XPath
    element = driver.find_element(By.XPATH, "//div[@class='thumbinner mp-thumb']")
    print(element.screenshot_as_base64)

finally:
    # Close the WebDriver
    driver.quit()
