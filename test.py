import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging to capture Selenium debug messages and print to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Chrome options
options = Options()
options.add_argument("--headless")  # Enable headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--enable-logging")  # Enable logging for ChromeDriver
options.add_argument("--log-level=0")     # Set log level to debug (0)

driver = webdriver.Chrome(options=options)

# Open a website
driver.get("https://www.example.com")
print(driver.title)  # Print the title of the page
driver.quit()