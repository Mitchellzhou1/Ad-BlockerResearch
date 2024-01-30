from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Set up options for Chrome WebDriver with selenium-wire
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')

# Create a proxy_options object
proxy_options = {
    'httpProxy': 'http://localhost:8888',  # Replace with your proxy server address
    'sslProxy': 'http://localhost:8888',
    'noProxy': 'localhost,127.0.0.1',  # Exclude localhost from proxy
}

# Set up proxy in Chrome options
chrome_options.add_argument('--proxy-server=http://localhost:8888')

# Create a WebDriver instance with the configured options
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Send a request to the specified URL
url = 'https://www.uxmatters.com/'
driver.get(url)

# Wait for a moment to ensure all resources are loaded
driver.implicitly_wait(5)

# Output all fetched resources
for request in driver.requests:
    if request.response:
        if request.response.status_code != 200:
            print("something blocked")
        else:
            print(f"URL: {request.url}")
            print(f"Method: {request.method}")
            print(f"Status Code: {request.response.status_code}")
            print(f"Type: {request.response.headers['content-type']}")
            print("")

# Close the WebDriver when done
driver.quit()
