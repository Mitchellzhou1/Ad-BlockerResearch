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


shared_driver.attributes = attributes
shared_driver.xpaths = xpaths

def main():

    # vdisplay = Display(visible=False, size=(1920, 1080))
    # vdisplay.start()
    shared_driver.initialize('uBlock')
    sites = ['https://www.imdb.com/']
    curr_site = 0
    tries = 1
    while curr_site < len(sites):
        url = sites[curr_site]
        try:
            if shared_driver.load_site(url):
                buttons = shared_driver.get_elements("buttons")
                shared_driver.test_elems(buttons, "buttons", tries)
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
                error = e.msg.split("\n")[0]

            write_results([error, "Failed", "Failed", shared_driver.initial_outer_html, tries])
            tries = 1
            shared_driver.tries = 1
            shared_driver.icon += 1

    print("\n\nFinished Testing on All Sites!\n\n\n")
    # vdisplay.stop()


main()
