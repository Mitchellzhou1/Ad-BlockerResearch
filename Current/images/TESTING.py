import threading
from selenium import webdriver

def open_browser():
    driver = webdriver.Chrome()
    # Store the WebDriver instance in a global variable for access outside the function
    global drivers
    drivers.append(driver)

# List to store WebDriver instances
drivers = []

# Create threads for opening browsers
threads = []
for _ in range(4):
    thread = threading.Thread(target=open_browser)
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Perform actions with the opened browsers
for driver in drivers:
    driver.get("https://www.example.com")
    # Perform any actions you need in each browser

# Do not quit WebDriver instances here to keep them alive
# Quit WebDriver instances when you're done with them elsewhere in your code

print("All browsers launched successfully and kept alive.")

while 1:
    1
