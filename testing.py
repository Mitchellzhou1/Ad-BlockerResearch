from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time, json, os

chrome_options = webdriver.ChromeOptions()
driver = None

websites = [
    "mrdonn.org"
    # "uxmatters.com",
    # "velocityhub.com",
    # 'amazon.com/',
    # 'en.wikipedia.org/wiki/Main_Page',
    # 'microsoft.com/en-us',
    # 'office.com',
    # 'weather.com',
    # 'openai.com',
    # 'bing.com',
    # 'duckgo.com',
    # 'nytimes.com',
    # 'twitch.tv',
    # 'imdb.com',
    # 'qq.com',
    # 'globo.com',
    # 'ebay.com',
    # 'foxnews.com',
    # 'instructure.com',
    # 'walmart.com',
    # 'indeed.com',
    # 'paypal.com/us/home',
    # 'accuweather.com',
    # 'pinterest.com',
    # 'bbc.com',
    # 'homedepot.com',
    # 'breitbart.com',
    # 'github.com'
]


def initialize(name='', seconds=14):
    """
        This function will start a Chrome instance with the option of installing an ad blocker.
        Adjust the seconds parameter so that it will wait for the ad blocker to finish downloading.
    """
    global driver
    current_dir = os.path.dirname(os.path.realpath(__file__))
    extension_path = os.path.abspath(os.path.join(current_dir, 'Extensions', 'Ad-Blockers'))
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--proxy-server=http://localhost:8888')

    if name == 'AdBlockPlus':
        extension_path = os.path.join(extension_path, 'adBlockerPlus.crx')
        chrome_options.add_extension(extension_path)
    elif name == 'uBlock':
        extension_path = os.path.join(extension_path, 'uBlock-Origin.crx')
        chrome_options.add_extension(extension_path)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.set_window_size(1555, 900)
    # give it time to install
    if name == 'AdBlockPlus':
        time.sleep(seconds)
        for handle in driver.window_handles[1:]:
            driver.switch_to.window(handle)
            driver.close()

        driver.switch_to.window(driver.window_handles[0])


def remove_after_substring(link, substring):
    for seperator in substring:
        index = link.find(seperator)
        if index != -1:
            link = link[:index]

    return link


def black_list():
    """
    Combines all the Black lists into 1 big list
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # parent_directory = os.path.dirname(os.path.dirname(current_dir))
    extensions_dir = os.path.abspath(os.path.join(current_dir, 'Extensions'))

    easy_list = open(f"{extensions_dir}/easylist.txt", "r")
    easy_privacy = open(f"{extensions_dir}/easyprivacy.txt", "r")
    peter_lowe = open(f"{extensions_dir}/Peter Lowe", "r")

    combined = set()

    for rule in easy_privacy:
        if rule[:2] == "||":
            rule = remove_after_substring(rule.strip().lstrip("||"), "^$~*")
            combined.add(rule)

    for rule in easy_list:
        if rule[:2] == "||":
            rule = remove_after_substring(rule.strip().lstrip("||"), "^$~*")
            combined.add(rule)
    for rule in peter_lowe:
        if rule[:10] == "127.0.0.1 ":
            rule = rule.strip()[10:]
            combined.add(rule)

    return sorted(combined)


def binary_search(blacklist, url):
    def url_formatter(link):
        return link.strip("https://www.").strip("http://www.")

    def match(rule, link):
        parts = rule.split("*")
        for part in parts:
            if part not in link:
                return False
        return True

    low = 0
    high = len(blacklist) - 1
    url = url_formatter(url)
    while low <= high:
        mid = (low + high) // 2
        rule = blacklist[mid]
        if match(rule, url):
            print(rule)
            return True  # Match found
        elif rule < url:
            low = mid + 1
        else:
            high = mid - 1

    return False  # No match found


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


def write_JSON(name, my_dict):
    json_file_path = name + ".json"
    with open(json_file_path, "w") as json_file:
        json.dump(my_dict, json_file)


def is_loaded():
    return driver.execute_script("return document.readyState") == "complete"

def wait_until_loaded(timeout=60, period=0.25, min_time=0):
    start_time = time.time()
    mustend = time.time() + timeout
    while time.time() < mustend:
        if is_loaded():
            if time.time() - start_time < min_time:
                time.sleep(min_time + start_time - time.time())
            return True
        time.sleep(period)
    return False


def scroll_to_bottom():
    curr_scroll_position = -1
    curr_time = time.time()
    while True:
        # Define the scroll step size
        scroll_step = 50  # Adjust this value to control the scroll speed
        # Get the current scroll position
        scroll_position = driver.execute_script("return window.pageYOffset;")
        # Check if we've reached the bottom
        if curr_scroll_position == scroll_position:
            break
        else:
            curr_scroll_position = scroll_position

        # Scroll down by the step size
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")

        # Wait for a bit (this controls the scroll speed indirectly)
        time.sleep(0.1)  # Adjust this value to control the scroll speed
        if time.time() - curr_time >= 45:
            break


def capture_resources(name, blacklist, resource_dict, write=False):
    index = len(driver.requests)

    for website in websites:
        url = f"http://www.{website}"
        driver.get(url)
        wait_until_loaded()
        scroll_to_bottom()
        time.sleep(2)

        resource_dict[url] = {"resources_detailed": [], "resources_url": []}
        print(f"resources for {website}:", len(driver.requests))

        while index < len(driver.requests):
            # print("running site", index)
            request = driver.requests[index]
            if request.response:
                content = content_eval(request.response.headers['content-type'])
                found_in_blacklist = binary_search(blacklist, url)

                if "https://optimizationguide-pa.googleapis.com/" in request.url or \
                    "https://www.googletagmanager.com/" in request.url or \
                    "https://www.google-analytics.com/g/collect?v" in request.url:
                    index += 1
                    continue

                resource_dict[url]["resources_detailed"].append([request.url,
                                                                 request.response.status_code,
                                                                 request.response.headers['content-type'],
                                                                 content,
                                                                 found_in_blacklist
                                                                 ])
                resource_dict[url]["resources_url"].append(request.url)

            if write:
                write_JSON(name, resource_dict)
            index += 1

    print("final length:", len(driver.requests))
    return resource_dict


def compare_resources(name, blacklist, control):
    extension_resources = capture_resources(name, blacklist, {})

    results = {}
    for website in extension_resources.keys():
        extension_values = set(extension_resources[website]["resources_url"])
        control_values = set(control[website]["resources_url"])

        missing_resources = list(control_values - extension_values)
        additional_resources = list(extension_values - control_values)

        results["website"] = {"missing_resources": missing_resources,
                              "additional_resources": additional_resources}
        write_JSON(name, results)

blacklist = black_list()


def main():
    global driver

    initialize()
    control = capture_resources("Control", blacklist, {}, True)
    driver.close()

    extensions = ["uBlock", "AdBlockPlus"]
    for extension in extensions:
        print(f"Collecting on {extension}")
        initialize(extension)
        compare_resources(extension, blacklist, control)
        driver.close()


main()
print("done")
while 1:
    1
