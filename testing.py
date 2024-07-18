from selenium import webdriver
import time

# Initialize a WebDriver instance (for example, let's use Chrome)
driver = webdriver.Chrome()

# Open a website
driver.get('https://www.example.com')
time.sleep(10)

# Close the browser window
driver.quit()
