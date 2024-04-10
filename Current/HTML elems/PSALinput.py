from PSAL_base_code import *
from selenium.webdriver.common.keys import Keys

sites = [
    'https://www.guldborgsund.dk/',
    'https://mikegap.com/',
    'https://marijuanaretailreport.com/',
    'http://www.bidtheatre.com/',
    'https://www.rosaperez.pt/en/',
    'https://www.hidraulicart.pt/',
    'https://juantorreslopez.com/',
    'http://www.werkschoenen-concurrent.nl',
    'https://naver.com',
    'https://www.ehab.com/',
    'https://copyblogger.com/',
    'http://www.portaldasfinancas.gov.pt/',
]

attributes_dict = {
        "input": {
            "attributes": ['text'],
            "xpaths": ['@type']
        },
        "submit": {
            "attributes": ['submit'],
            "xpaths": ['@type']
        }
        # Search for forms
        # write input into the type="text" attributes
        # click on the input with type="submit"
        # check if diff
}
HTML_TEST = 'input'
ad_blocker = 'control'
replay = 1
data_dict = {}
excel_dict = {}
hierarchy_dict = {}
set_HTML_obj(HTML_TEST)
shared_driver = PSALDriver(attributes_dict[HTML_TEST]["attributes"], attributes_dict[HTML_TEST]["xpaths"], ad_blocker,
                       replay, data_dict, excel_dict, hierarchy_dict)

shared_driver.initialize()
shared_driver.html_obj = "input"

msg = "testing"

for url in sites:
    shared_driver.load_site(url)
    shared_driver.get_elements()
    # Find the form box element by its ID or XPath

    # Clear any existing text in the form box (optional)
    for elem in shared_driver.chosen_elms:
        outerHTML, refresh = elem

    form_box.clear()

    # Type text into the form box
    form_box.send_keys("Hello, world!")

    # Submit the form or perform any other actions as needed
    # For example, you can submit the form by pressing Enter
    form_box.send_keys(Keys.RETURN)

# Close the browser window
driver.quit()
