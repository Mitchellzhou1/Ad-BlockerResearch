from browsermobproxy import Server
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time, os

# server = Server("/home/character/Desktop/Ad-BlockerResearch/Current/HTML elems/browsermob-proxy/bin/browsermob-proxy")
server = Server("/home/character/browsermob-proxy/bin/browsermob-proxy")
server.start()
proxy = server.create_proxy()


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--proxy-server={0}".format(proxy.proxy))
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-animations")
chrome_options.add_argument("--disable-web-animations")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
chrome_options.binary_location = '/usr/local/bin/chrome_113/chrome'


# Create a proxy_options object
# proxy_options = {
#     'httpProxy': 'http://localhost:8888',  # Replace with your proxy server address
#     'sslProxy': 'http://localhost:8888',
#     'noProxy': 'localhost,127.0.0.1',  # Exclude localhost from proxy
# }

# Set up proxy in Chrome options
# chrome_options.add_argument('--proxy-server=http://localhost:8888')
# current_dir = os.path.dirname(os.path.realpath(__file__))
# parent_directory = os.path.dirname(os.path.dirname(current_dir))
# extensions_dir = os.path.abspath(os.path.join(parent_directory, 'Extensions', 'Ad-Blockers'))
# extension_path = os.path.join(extensions_dir, 'uBlock-Origin.crx')
# chrome_options.add_extension(extension_path)
driver = webdriver.Chrome(
    # service=Service(ChromeDriverManager().install()),
    options=chrome_options
)
websites = [
    "nytimes.com/"
]
result = {}
proxy.new_har("example", options={'captureHeaders': True})
for website in websites:
    url = f"http://www.{website}"
    time.sleep(2)
    driver.get(url)
    time.sleep(20)
    data = proxy.har
    print(data)
    print(len(data['log']['entries']))
    # print(len(data['log']['entries'][0]))
    result[website] = data
    time.sleep(1000)
    print(proxy.har)

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
# for request in driver.requests:
#     print(f"URL: {request.url}")
#     print(f"Method: {request.method}")
#     if request.response:
#         print(f"Status Code: {request.response.status_code}")
#         content = content_eval(request.response.headers['content-type'])
#         print(f"Type: {content}          {request.response.headers['content-type']}")
#         print("")
#


driver.quit()
server.stop()
print(result)

