from base_code import *
from Excel import *

from selenium.common import ElementClickInterceptedException, ElementNotInteractableException

attributes = [
    'button',
    'submit',
    '#'
]

xpaths = [
    '@role',
    '@type'
]

sites = [
    # 'https://en.wikipedia.org/wiki/Main_Page',
    'https://www.amazon.com/',
    # 'https://www.microsoft.com/en-us/',
    # 'https://www.office.com/',
    # 'https://weather.com/',
    # 'https://openai.com/',
    # 'https://www.bing.com/',
    # 'https://duckduckgo.com/'
    # 'https://cnn.com',
    # 'https://www.nytimes.com/',
    # 'https://www.twitch.tv/',
    # 'https://www.imdb.com/',
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

shared_driver.attributes = attributes
shared_driver.xPaths = xpaths
shared_driver.adBlocker_name = 'uBlock'
shared_driver.html_obj = 'buttons'
HTML_obj = 'buttons'

def main():

    # vdisplay = Display(visible=False, size=(1920, 1080))
    # vdisplay.start()
    shared_driver.initialize()
    # sites = ['https://www.imdb.com/']
    curr_site = 0
    tries = 1

    # initialize_csv_file(HTML_obj)
    # initialize()

    while curr_site < len(sites):
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
                error = str(e).split("\n")[0]

            write_results([error, "Failed", "Failed", shared_driver.initial_outer_html, tries])
            tries = 1
            shared_driver.tries = 1
            shared_driver.icon += 1

    print("\n\nFinished Testing on All Sites!\n\n\n")
    # vdisplay.stop()


main()
