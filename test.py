import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import tkinter as tk
import io
from PIL import Image


   # Set log level to debug (0)
driver = webdriver.Chrome()

# Open a website
driver.get("https://www.fox.com")
driver.maximize_window()
driver.execute_script("window.scrollTo(0, 0);")
time.sleep(1)
page_width = driver.execute_script("return document.documentElement.scrollWidth")
page_height = driver.execute_script("return document.documentElement.scrollHeight")

screenshots = []
viewport_height = driver.execute_script("return window.innerHeight")
scroll_height = 0
while scroll_height < page_height:
    screenshot = driver.get_screenshot_as_png()
    screenshots.append(screenshot)

    scroll_height += viewport_height
    driver.execute_script(f"window.scrollTo(0, {scroll_height});")
    time.sleep(1)
full_screenshot = Image.new('RGB', (page_width, page_height))
current_height = 0
for screenshot in screenshots:
    img = Image.open(io.BytesIO(screenshot))
    full_screenshot.paste(img, (0, current_height))
    current_height += viewport_height

full_screenshot.save('entire.png')