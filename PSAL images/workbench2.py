from selenium import webdriver

# Path to the WebDriver executable (change this to the path where you downloaded the driver)
# Create a WebDriver instance (for Chrome in this example)
driver = webdriver.Chrome()

# Open a website
driver.get('https://www.example.com')

# Close the WebDriver instance
driver.quit()
