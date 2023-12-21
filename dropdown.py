from base_code import *
from Excel import *

from selenium.common import ElementClickInterceptedException, ElementNotInteractableException

tag = ['button',
       'div',
       'input',
       'svg',
       'a'
       ]

attributes = [
    'false',
    'true',
    'main menu',
    'open menu',
    'all microsoft menu',
    'menu',
    'navigation',
    'primary navigation',
    'hamburger',
    'settings and quick links',
    'dropdown',
    'dialog',
    'js-menu-toggle',
    'searchDropdownDescription',
    'ctabutton',
    'legacy-homepage_legacyButton__oUMB9 legacy-homepage_hamburgerButton__VsG7q',
    'Toggle language selector',
    'Open Navigation Drawer',
    'guide',
    'Expand Your Library',
    'Collapse Your Library'
]

xpaths = [
    '@aria-expanded',
    '@aria-label',
    '@class',
    '@aria-haspopup',
    '@aria-describedby',
    '@data-testid',
]

sites = [
    'https://azure.microsoft.com/',
    'https://cnn.com',
    'http://cnn.com',
    'https://failedsite1111.com',
    'https://en.wikipedia.org/wiki/Main_Page',
    'https://www.amazon.com/',
    'https://www.microsoft.com/en-us/',
    'https://www.office.com/',
    'https://weather.com/',
    'https://openai.com/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
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

shared_driver.attributes = attributes
shared_driver.xPaths = xpaths

def main():

    # vdisplay = Display(visible=False, size=(1920, 1080))
    # vdisplay.start()
    shared_driver.initialize('uBlock')
    # sites = ['https://en.wikipedia.org/wiki/Main_Page']
    index = 0
    tries = 1
    while index < len(sites):
        url = sites[index]
        try:
            if shared_driver.load_site(url):
                dropdowns = shared_driver.find_dropdown(attributes, xpaths)
                # print(len(elms))
                shared_driver.test_drop_down(dropdowns, tries)
            else:
                write_noscan_row(url)
            index += 1
            tries = 1

        except Exception as e:
            if shared_driver.tries != 3:
                shared_driver.reinitialize()
                tries += 1
                continue

            if isinstance(e, ElementClickInterceptedException):
                # print("Element Click Intercepted")
                error = "Failed - Element Click Intercepted"
            elif isinstance(e, TimeoutError):
                # print("Timeout Error")
                error = "Failed - Site Timeout Error"
            elif isinstance(e, ElementNotInteractableException):
                # print("Not Interactable")
                error = "Failed - Not Interactable"
            else:
                # print(e)
                # print(["Failed - unknown error", e])
                error = e.msg.split("\n")[0]

            write_results([error, "Failed", "Failed", shared_driver.initial_outer_html, tries])
            tries = 1
            shared_driver.tries = 1
            index += 1


    print("\n\nFinished Testing on All Sites!\n\n\n")
    # vdisplay.stop()

main()
