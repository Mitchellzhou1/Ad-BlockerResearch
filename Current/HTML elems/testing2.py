from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chrome_driver_path = '/usr/local/bin/chrome_113/chromedriver'  # Adjust this to your Chrome WebDriver path

# Set up Chrome options with DevTools capabilities
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--headless')  # Run in headless mode (optional)

# Initialize the Chrome browser with specified WebDriver path
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Navigate to the webpage
driver.get('https://www.example.com')

# Get all resources loaded on the page
resources = driver.execute_cdp_cmd('Network.getAllLoadedResources', {})

# Print the resources
for resource in resources['resources']:
    print(resource['url'])

# Close the browser
driver.quit()
