import json
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize the WebDriver (assuming Chrome in this case)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open a webpage
driver.get("https://www.uxmatters.com/")


def resource_type(url):
    response = requests.head(url)
    if response and response.headers.get('Content-Type'):
        extension = response.headers.get('Content-Type')
    else:
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico',
                            '.jfif', '.pjpeg', '.pjp', '.svgz', '.tif', '.tga', '.exif', '.ppm', '.pgm',
                            '.pbm', '.pnm', '.webm', '.hdr', '.heif', '.bat', '.bpg', '.jpe', '.jp2', '.jpm',
                            '.jpx', '.j2k', '.j2c', '.jpf', '.jpx', '.jxr', '.hdp', '.wdp', '.cur', '.dds']

        if any(ext in url.lower() for ext in image_extensions):
            extension = "image"

        elif ".css" in url.lower():
            extension = "stylesheet"

        else:
            extension = "N/A"

    return extension

def retrieve_all_resources():
    script = """
    const resources = performance.getEntriesByType('resource');
    let results = [];
    resources.forEach(resource => {
        results.push({
            'URL': resource.name
        });
    });
    return results;
    """
    result = driver.execute_script(script)
    return [item['URL'] for item in result]


def retrieve_blocked_resources():
    blocked_resources = []
    logs = driver.get_log('browser')
    for log in logs:
        resource, message = log['message'].split(" - ")
        if message == "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT":
            blocked_resources.append(resource)
    return blocked_resources


for url in retrieve_all_resources():
    print(url)
    print(resource_type(url))
    print()

print("Done")
while 1:
    1