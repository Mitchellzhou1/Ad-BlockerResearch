import os
import requests
import tldextract
from urllib.parse import urlparse

file_extensions = [
    ".js",  # JavaScript
    ".css",  # Cascading Style Sheets
    ".swf",  # Adobe Flash
    ".gif",  # Graphics Interchange Format
    ".jpg",  # Joint Photographic Experts Group
    ".jpeg",  # Joint Photographic Experts Group
    ".png",  # Portable Network Graphics
    ".mp4",  # MPEG-4 video file
    ".mp3",  # MPEG Audio Layer III
    ".html",  # Hypertext Markup Language
    ".php",  # Hypertext Preprocessor
    ".asp",  # Active Server Pages
    ".aspx",  # Active Server Pages
    ".xml",  # Extensible Markup Language
    ".svg",  # Scalable Vector Graphics
    ".woff",  # Web Open Font Format
    ".woff2",  # Web Open Font Format 2
    ".ttf",  # TrueType Font
    ".otf",  # OpenType Font
    ".webm",  # WebM video file
    ".webp",  # WebP image file
    ".ico"  # Icon file
]


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def possible_rules(self, node, prefix):
        strings = []
        # Base case: if the node is the end of a word, add the prefix to the list of strings
        if node.is_end_of_word:
            strings.append(prefix)
        # Recursively generate strings for each child node
        for char, child in node.children.items():
            strings.extend(self.possible_rules(child, prefix + char))
        return strings

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, entire_url):
        node = self.root
        rule = ''
        for char in entire_url:
            if char not in node.children:
                if rule in self.possible_rules(node, rule):
                    print("found regular search item:", rule)
                    return True
                return False
            rule += char
            node = node.children[char]
        return False

    def inverse_search(self, word):
        """
        Only doing domain matching right now
        """
        node = self.root
        rule = ''
        for char in word:
            if node.is_end_of_word:
                if char == '.':
                    # there is a subdomain identified, but the domain matched.
                    # print("found rev-search item:", rule[::-1])
                    return True
                else:
                    # doesn't match
                    return False
            if char not in node.children:
                # the domain didn't match
                return False

            rule += char
            node = node.children[char]

        if node.is_end_of_word:
            # print("found rev-search item:", rule[::-1])
            return True
        return False


def initialize_blacklists(inverse_lookup, regular_lookup):
    """
    Combines all the Black lists into 1 big list
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    extensions_dir = os.path.abspath(os.path.join(current_dir, 'blacklists'))

    # Check if extensions_dir exists, if not, create it
    if not os.path.exists(extensions_dir):
        os.makedirs(extensions_dir)

    # URLs for the files to download
    files_urls = {
        "easylist.txt": "https://easylist.to/easylist/easylist.txt",
        "easyprivacy.txt": "https://easylist.to/easylist/easyprivacy.txt",
        "Peter Lowe": "https://pgl.yoyo.org/adservers/serverlist.php"
        # Add the correct file extension if needed, e.g., .txt
    }

    # Iterate over the files and their URLs
    for filename, url in files_urls.items():
        filepath = os.path.join(extensions_dir, filename)

        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Downloading {filename} from {url}")
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename} successfully.")
            except requests.RequestException as e:
                print(f"Error downloading {filename}: {e}")
        else:
            print(f"{filename} already exists.")

    easy_list = open(f"{extensions_dir}/easylist.txt", "r")
    easy_privacy = open(f"{extensions_dir}/easyprivacy.txt", "r")
    peter_lowe = open(f"{extensions_dir}/Peter Lowe", "r")

    combined = set()

    for rule in easy_privacy:
        if rule[:2] == "||":
            rule = remove_after_substring(rule.strip().lstrip("||"), "^$~?")
            if ends_with_file_extension(rule):
                continue

            subdomain, domain, suffix = url_parser(rule)
            rule = domain + '.' + suffix
            combined.add(rule)
            inverse_lookup.insert(rule[::-1])
            regular_lookup.insert(rule)

    for rule in easy_list:
        if rule[:2] == "||":
            rule = remove_after_substring(rule.strip().lstrip("||"), "^$~?")
            if ends_with_file_extension(rule):
                continue

            subdomain, domain, suffix = url_parser(rule)
            rule = domain + '.' + suffix
            combined.add(rule)
            inverse_lookup.insert(rule[::-1])
            regular_lookup.insert(rule)

    for rule in peter_lowe:
        if rule[:10] == "127.0.0.1 ":
            rule = rule.strip()[10:]
            if ends_with_file_extension(rule):
                continue

            subdomain, domain, suffix = url_parser(rule)
            rule = domain + '.' + suffix
            combined.add(rule)
            inverse_lookup.insert(rule[::-1])
            regular_lookup.insert(rule)

    # THIS IS JUST TO HELP ME DEBUG AND SEE THE CONTENTS OF THE COMBINED BLACKLISTS
    print("\nBuilding Blacklist tree...")
    with open('strippeddownblacklist.txt', 'w') as file:
        for item in sorted(combined):
            file.write(str(item) + '\n')
    file.close()
    print("Finished Building Blacklist tree!")
    return sorted(combined), inverse_lookup, regular_lookup


def remove_after_substring(link, substring):
    for seperator in substring:
        index = link.find(seperator)
        if index != -1:
            link = link[:index]

    return link


def url_parser(full_url):
    extracted = tldextract.extract(full_url)
    subdomain = extracted.subdomain
    domain = extracted.domain
    suffix = extracted.suffix

    return subdomain, domain, suffix


def ends_with_file_extension(string):
    for ext in file_extensions:
        if string.endswith(ext):
            return True
    return False


def scheme_extractor(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    domain = domain.replace('www.', '')
    new_url = domain + parsed_url.path
    if parsed_url.query:
        new_url += '?' + parsed_url.query
    return new_url


def blacklist_parser(blacklist, inverse_lookup, regular_lookup, url):
    subdomain, domain, suffix = url_parser(url)
    subdomains = ['done'] + subdomain.split(".")
    test_url = domain + "." + suffix

    # removes the https:// http:// and www. from the url
    simplified_url = scheme_extractor(url)

    if inverse_lookup.inverse_search(test_url[::-1]):
        return True
    return False

    # NOT USING FOR NOW!!!!
    # while subdomains:
    #     if inverse_lookup.inverse_search(test_url[::-1]):
    #         return True
    #
    #     if regular_lookup.search(simplified_url):
    #         return True
    #
    #     if binary_search(blacklist, domain, url):
    #         return True
    #     domain = f"{subdomains.pop()}.{domain}"
    # return False


def site_filter(control_log_1, control_log_2):
    try:
        for control_url1 in control_log_1.keys():
            if control_url1 not in control_log_2.keys():
                return False

        for control_url2 in control_log_2.keys():
            if control_url2 not in control_log_1.keys():
                return False
        return True
    except Exception as e:
        print("Site_Filter() failed... this is really strange")
        print(e)
