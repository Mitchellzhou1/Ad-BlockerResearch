from base_code import *
from Excel import *

from selenium.common import ElementClickInterceptedException, ElementNotInteractableException, InvalidSelectorException

attributes_dict = {
    "buttons": {
        "attributes": ['button', '#', '/'],
        "xpaths": ['@role', '@type']
    },
    "drop downs": {
        "attributes": ['false', 'true', 'main menu', 'open menu', 'all microsoft menu', 'menu', 'navigation',
                       'primary navigation', 'hamburger', 'settings and quick links', 'dropdown', 'dialog',
                       'js-menu-toggle', 'searchDropdownDescription', 'ctabutton',
                       'legacy-homepage_legacyButton__oUMB9 legacy-homepage_hamburgerButton__VsG7q',
                       'Toggle language selector', 'Open Navigation Drawer', 'guide', 'Expand Your Library',
                       'Collapse Your Library'],
        "xpaths": ['@aria-expanded', '@aria-label', '@class', '@aria-haspopup', '@aria-describedby', '@data-testid']
    },
    "links": {
        "attributes": [],
        "xpaths": ['href']
    },
    "login": {  # remember to enable HREF
        "attributes": ['button', 'submit', '#'],
        "xpaths": ['@role', '@type']
    }

}

sites = [
    # 'http://www.feimaoyun.com',
    # 'https://en.wikipedia.org/wiki/Main_Page',
    # 'https://www.microsoft.com/en-us/',
    # 'https://www.office.com/',
    # 'https://weather.com/',
    # 'https://openai.com/',
    # 'https://www.bing.com/',
    # 'https://duckduckgo.com/',
    # 'https://cnn.com',
    # 'https://www.nytimes.com/',
    # 'https://www.twitch.tv/',
    # 'https://www.imdb.com/',
    # 'https://www.qq.com/',
    # 'https://mail.ru/',
    # 'https://naver.com',
    # 'https://zoom.us/',
    # 'https://www.globo.com/',
    # 'https://www.ebay.com/',
    # 'https://www.foxnews.com/',
    # 'https://www.instructure.com/',
    # 'https://www.walmart.com/',
    # 'https://www.indeed.com/',
    # 'https://www.paypal.com/us/home',
    # 'https://www.accuweather.com/',
    # 'https://www.pinterest.com/',
    # 'https://www.bbc.com/',
    # 'https://www.homedepot.com/',
    # 'https://www.breitbart.com/',
    # 'https://github.com/'
]
HTML_TEST = 'buttons'
ad_blocker = 'uBlock'

shared_driver.attributes = attributes_dict[HTML_TEST]["attributes"]
shared_driver.xPaths = attributes_dict[HTML_TEST]["xpaths"]
shared_driver.adBlocker_name = ad_blocker
shared_driver.html_obj = HTML_TEST
set_HTML_obj(HTML_TEST)


def scan_website(sites):
    curr_site = 0
    while curr_site < len(sites):
        url = sites[curr_site]

        if shared_driver.load_site(url):
            shared_driver.scan_page()
        else:
            write_noscan_row(url)

        curr_site += 1


def error_catcher(e, tries, url):
    if shared_driver.tries != 3:
        shared_driver.reinitialize()
        tries += 1
        return tries

    if isinstance(e, ElementClickInterceptedException):
        error = "N/A - Element Click Intercepted"
    elif isinstance(e, ElementNotInteractableException):
        error = "N/A - Not Interactable"
    elif isinstance(e, StaleElementReferenceException):
        error = "StaleElementReferenceException"
    elif isinstance(e, NoSuchElementException):
        error = "N/A - No such Element"
    elif isinstance(e, InvalidSelectorException):
        error = "N/A - InvalidSelectorException"
    elif isinstance(e, IndexError):
        print("ok")
    elif isinstance(e, TimeoutError):
        write_noscan_row(url)
        tries = 1
        shared_driver.tries = 1
        shared_driver.curr_elem += 1
        print("TIME OUT EERRORRR")
        return tries

    error = str(e).split("\n")[0]
    return error

def main():

    # vdisplay = Display(visible=False, size=(1920, 1080))
    # vdisplay.start()
    if not os.path.isfile(f"{HTML_TEST}.json"):
        storeDictionary({})
    shared_driver.initialize()
    # initialize_xlsx()

    sites = ["http://www.bidtheatre.com"]
    tries = 1
    for url in sites:
        shared_driver.load_site(url)
    try:
        scan_website(sites)
    except TimeoutException:
        write_noscan_row(shared_driver.url)
    except Exception as e:
        error = str(e).split("\n")[0]
        write_results([error, "N/A", "N/A", shared_driver.initial_outer_html, tries])


    # while shared_driver.curr_site > -1:
    #     try:
    #         shared_driver.click_on_elms(tries)
    #     except Exception as e:
    #         result = error_catcher(e, tries, shared_driver.url)
    #         if type(result) is int:
    #             tries = result
    #         else:
    #             print(shared_driver.url, "\t", result, shared_driver.initial_outer_html)
    #             write_results([result, "N/A", "N/A", shared_driver.initial_outer_html, tries])
    #             tries = 1
    #             shared_driver.tries = 1
    #             shared_driver.curr_elem += 1



    shared_driver.driver.close()
    print("\n\nFinished Testing on All Sites!\n\n\n")
    # vdisplay.stop()


main()
