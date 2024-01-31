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

websites = [
    # "examplewebsite1.com",
    # "webworldhub.net",
    # "techtriumph.org",
    # "stellarcode.io",
    # "quantumgadget.com",
    # "explorifyweb.com",
    # "nexusplatform.org",
    "velocityhub.com",
    # "cosmicinsights.net",
    # "datauniverse.io",
    # "innovatexcellence.com",
    # "pixelplanet.org",
    # "synthwavehub.com",
    # "infinitytech.io",
    # "quantumspark.net",
    # "dreamweaverlab.com",
    # "vividvisions.org",
    # "nebulaconnect.com",
    # "digitalsunrise.io",
    # "codecrafters.net"
]

for website in websites:
    url = f"https://www.{website}"
    driver.get(url)

def content_eval(content_header):
    stylesheet = ['text/css', 'application/css', 'application/x-css', 'text/plain',
                  'text/html']
    script = ['application/javascript', 'application/x-javascript', 'text/javascript', 'text/ecmascript',
              'application/ecmascript']
    images = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml', 'image/x-icon']
    if content_header:
        if any(elem in content_header for elem in stylesheet):
            return "stylesheet"
        if any(elem in content_header for elem in script):
            return "script"
        if any(elem in content_header for elem in images):
            return "images"
    return content_header

types = []
blocked = []
# Output all fetched resources
for request in driver.requests:
    if request.response:
        if request.response.status_code != 200:
            blocked.append(request)
        else:
            print(f"URL: {request.url}")
            print(f"Method: {request.method}")
            print(f"Status Code: {request.response.status_code}")
            content = content_eval(request.response.headers['content-type'])
            print(f"Type: {content}          {request.response.headers['content-type']}")
            print("")

# Close the WebDriver when done
driver.quit()

print(set(types))

for i in blocked:
    print(f"URL: {i.url}")
    print(f"Method: {i.method}")
    print(f"Status Code: {i.response.status_code}")
    content = content_eval(i.response.headers['content-type'])
    print(f"Type: {content}          {i.response.headers['content-type']}")
    print("")

