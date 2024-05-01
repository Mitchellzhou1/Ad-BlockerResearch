import os
from base_code import *
shared_driver.initialize()
shared_driver.load_site("https://www.uxmatters.com/")


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
    parent_directory = os.path.dirname(os.path.dirname(current_dir))
    extensions_dir = os.path.abspath(os.path.join(parent_directory, 'Extensions'))

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
    result = shared_driver.driver.execute_script(script)
    return [item['URL'] for item in result]


def retrieve_blocked_resources():
    blocked_resources = []
    logs = shared_driver.driver.get_log('browser')
    for log in logs:
        resource, message = log['message'].split(" - ")
        if message == "Failed to load resource: net::ERR_BLOCKED_BY_CLIENT":
            blocked_resources.append(resource)
    return blocked_resources


blacklist = black_list()

logs = shared_driver.driver.get_log('browser')
for url in retrieve_all_resources():
    found_in_blacklist = binary_search(blacklist, url)
    print(url, found_in_blacklist)
    print(resource_type(url))

while 1:
    1