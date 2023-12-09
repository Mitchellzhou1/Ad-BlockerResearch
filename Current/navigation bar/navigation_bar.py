from Current.driver import *
from Current.base import *

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


########################################################################################################################


def main():
    global driver, icon, outer_html, after_html
    errors, could_not_scan, timeout, intercept, skipped = [[] for _ in range(5)]

    # vdisplay = Display(visible=False, size=(1920, 1080))
    # vdisplay.start()
    driver = initialize('uBlock')
    driver.set_window_size(1555, 900)
    #
    sites = ["apple.com"]
    index = 0
    seen_sites = []
    tries = 1
    while index < len(sites):
        url = sites[index]
        try:
            if load_site(url, skipped):
                if url not in seen_sites:
                    seen_sites.append(url)
                    write_results(url)
                url = global_url
                sleep(tries * 5)
                print("\n", url)
                elms = find_dropdown()
                print(len(elms))
                test_drop_down(elms, url, tries)
                icon = 0
            else:
                write_noscan_row(url)
            index += 1
            tries = 1

        except Exception as e:
            if tries != 3:
                driver.close()
                driver = initialize(True)
                driver.set_window_size(1555, 900)
                tries += 1
                continue

            if isinstance(e, ElementClickInterceptedException):
                print("Element Click Intercepted")
                write_results(["Failed - Element Click Intercepted", outer_html, after_html, tries])
            elif isinstance(e, TimeoutError):
                print("Timeout Error")
                write_results("Failed - Site Timeout Error")
            elif isinstance(e, ElementNotInteractableException):
                print("Not Interactable")
                write_results(["Failed - Not Interactable", outer_html])
            else:
                print(e)
                write_other_row(["Failed - unknown error", e])
            icon += 1
            tries = 1
    print("\n\nFinished Testing on All Sites!\n\n\n")
    end()
    # vdisplay.stop()

main()

driver.close()
