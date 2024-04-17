# from bs4 import BeautifulSoup
#
# html_code = '''
# <div class="promo_ads">
#     <a href="https://www.patreon.com/UXmatters">
#         <img data-promo-mobile="/images/sponsors/UXmattersPatreonMobile.png" data-promo-desktop="/images/sponsors/UXmattersPatreonBanner.png" src="/images/sponsors/UXmattersPatreonBanner.png" class="promo" alt="Please become a patron of UXmatters by
#         subscribing on Patreon.">
#     </a>
# </div>
# '''
#
#
# def find_element_with_attribute_value(html, attribute, value):
#     soup = BeautifulSoup(html, 'html.parser')
#     elements_with_attribute = soup.find_all(lambda tag: tag.has_attr(attribute) and value in tag[attribute])
#     return [str(element) for element in elements_with_attribute]
#
#
# attribute_to_search = "src"
# value_to_find = "/images/sponsors/UXmattersPatreonBanner.png"
# found_elements = find_element_with_attribute_value(html_code, attribute_to_search, value_to_find)
# for element in found_elements:
#     print(element)
from tldextract import tldextract


from urllib.parse import urlparse
def extract_path_from_url(url):
    parsed_url = urlparse(url)
    return parsed_url.path

print(extract_path_from_url("https://www.uxmatters.com/images/sponsors/UXmattersPatreonBanner.png"))