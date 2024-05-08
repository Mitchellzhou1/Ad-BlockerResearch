from selenium import webdriver

# Initialize the Chrome web driver
options = webdriver.ChromeOptions()
options.headless = True  # Run Chrome in headless mode (no GUI)
driver = webdriver.Chrome(options=options)

# Navigate to the website
url = 'https://www.uxmatters.com/'  # Replace with the URL of the website you want to analyze
driver.get(url)

# Use JavaScript to scroll to the top of the page
driver.execute_script("window.scrollTo(0, 0);")

# Use JavaScript to get the parent node (e.g., <html> or <body> tag)
parent_node = driver.execute_script("return document.documentElement")  # This gets the <html> tag
# Alternatively, you can get the <body> tag as the parent node:
# parent_node = driver.execute_script("return document.body")

# Click on the parent node (assuming it's clickable)
print(parent_node.get_attribute('outerHTML'))

print(parent_node.get_attribute('outerHTML') == driver.page_source)

parent_node.screenshot("AAAAAAAAAAAAAAAAAAAaa.png")
while 1:
    1
