from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import io
import time

# Initialize the Chrome web driver
options = webdriver.ChromeOptions()
options.headless = True  # Run Chrome in headless mode (no GUI)
driver = webdriver.Chrome()

time.sleep(7)
driver.execute_script("window.scrollTo(0, 0);")

while 1:
    1
