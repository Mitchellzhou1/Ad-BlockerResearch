from base_code import *
from Excel import *

from selenium.common import ElementClickInterceptedException, ElementNotInteractableException, InvalidSelectorException

attributes_dict = {
    "buttons": {
        "attributes": ['button', 'submit', '#'],
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
    'https://www.amazon.com/',
    'https://en.wikipedia.org/wiki/Main_Page',
    'https://www.microsoft.com/en-us/',
    'https://www.office.com/',
    'https://weather.com/',
    'https://openai.com/',
    'https://www.bing.com/',
    'https://duckduckgo.com/'
    'https://cnn.com',
    'https://www.nytimes.com/',
    'https://www.twitch.tv/',
    'https://www.imdb.com/',
    'https://mail.ru/',
    'https://naver.com',
    'https://zoom.us/',
    'https://www.globo.com/',
    'https://www.ebay.com/',
    'https://www.foxnews.com/',
    'https://www.instructure.com/',
    'https://www.walmart.com/',
    'https://www.indeed.com/',
    'https://www.paypal.com/us/home',
    'https://www.accuweather.com/',
    'https://www.pinterest.com/',
    'https://www.bbc.com/',
    'https://www.homedepot.com/',
    'https://www.breitbart.com/',
    'https://github.com/'
]

HTML_TEST = 'buttons'
ad_blocker = 'uBlock'

shared_driver.attributes = attributes_dict[HTML_TEST]["attributes"]
shared_driver.xPaths = attributes_dict[HTML_TEST]["xpaths"]
shared_driver.adBlocker_name = ad_blocker
shared_driver.html_obj = HTML_TEST
HTML_obj = HTML_TEST

def main():

    # vdisplay = Display(visible=False, size=(1920, 1080))
    # vdisplay.start()
    shared_driver.initialize()
    # sites = ['https://www.imdb.com/']
    curr_site = 0
    tries = 1

    # initialize_csv_file(HTML_obj)
    initialize_xlsx()

    while curr_site < len(sites) and shared_driver.line > -1:
        url = sites[curr_site]
        try:
            if shared_driver.load_site(url):
                shared_driver.scan_page()
                # shared_driver.click_on_elms(tries)
            else:
                write_noscan_row(url)
            curr_site += 1
            tries = 1

        except Exception as e:
            # if shared_driver.tries != 3:
            #     shared_driver.reinitialize()
            #     tries += 1
            #     continue

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
            elif isinstance(e, TimeoutError):
                write_noscan_row(url)
                tries = 1
                shared_driver.tries = 1
                shared_driver.line += 1
                print("TIME OUT EERRORRR IS GOOD")
                continue

            else:
                error = str(e).split("\n")[0]

            write_results([error, "N/A", "N/A", shared_driver.initial_outer_html, tries])
            tries = 1
            shared_driver.tries = 1
            shared_driver.line += 1

    print("\n\nFinished Testing on All Sites!\n\n\n")
    # vdisplay.stop()


main()
