from selenium import webdriver
import time

# Assuming you have already initialized your WebDriver instance
driver = webdriver.Chrome()
driver.get("https://picoctf.org/")  # Replace with your URL

# Scroll to the middle of the page
driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
time.sleep(1)

prev_position = -1
scroll_position = driver.execute_script("return window.scrollY;")
while prev_position != scroll_position:
    print(prev_position, scroll_position)
    prev_position = scroll_position
    scroll_position = driver.execute_script("return window.scrollY;")


print("Scroll position after scrolling to the middle:", scroll_position)


while 1:
    1