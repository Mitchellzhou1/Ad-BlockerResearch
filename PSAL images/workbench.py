from selenium import webdriver
from urllib.parse import urlparse


def get_path(url):
# Parse the URL and extract the path
    parsed_url = urlparse(url)
    path = parsed_url.path
    return path
def initialize():
    browser = webdriver.Chrome()
    url = 'https://portswigger.net/web-security/all-labs'
    browser.get(url)
    return browser


url_to_find = "https://portswigger.net/content/images/logos/burp-suite-icon.svghttps://portswigger.net/content/images/logos/portswigger-logo.svg"
driver = initialize()
path = get_path(url_to_find)
if url_to_find in driver.page_source:
    print("IN PAGE SOURCE")

elif path in driver.page_source:
    print("Path in the PAGE SOURCE")

else:
    print("CSS")



while 1:
    1
