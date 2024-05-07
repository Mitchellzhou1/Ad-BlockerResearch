from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
extension_path = '/home/mitch/Desktop/Ad-BlockerResearch/Extensions/extn_crx/ublock.crx'

# Create a ChromeOptions object
chrome_options = Options()

# Add the extension to ChromeOptions
chrome_options.add_argument(extension_path)

# Create a WebDriver instance with the ChromeOptions
driver = webdriver.Chrome(options=chrome_options)

# Now you can use the WebDriver instance to navigate to a webpage, etc.
driver.get('https://www.example.com')

while 1:
    1