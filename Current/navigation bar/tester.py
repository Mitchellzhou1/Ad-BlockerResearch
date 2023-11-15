from selenium import webdriver
from selenium.webdriver.common.by import By

# Assuming you have already set up your webdriver, e.g., ChromeDriver
driver = webdriver.Chrome()

# Navigate to your webpage
driver.get("https://www.msn.com/")

# Find the button by its class name
button = driver.find_element(By.CLASS_NAME, 'control')

# Perform actions on the button, like clicking it
button.click()

# Close the browser when done
driver.quit()
