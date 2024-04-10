from PSAL_base_code import *
from selenium.webdriver.common.keys import Keys

sites = [
    'https://marijuanaretailreport.com/',
    'http://www.bidtheatre.com/',       # blocked by Ublock
    'https://www.rosaperez.pt/en/',
    'https://www.hidraulicart.pt/',
    'https://juantorreslopez.com/',
    'http://www.werkschoenen-concurrent.nl',
    'https://naver.com',
    'https://www.ehab.com/',
    'https://copyblogger.com/',
    'http://www.portaldasfinancas.gov.pt/',
    'https://www.guldborgsund.dk/',
    'https://mikegap.com/',
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

for url in sites:
    shared_driver.load_site(url)
    shared_driver.get_elements()
    for form_html, refresh in shared_driver.chosen_elms:
        xpath = shared_driver.generate_xpath(form_html)
        form_elem = shared_driver.get_correct_elem(xpath, form_html)

        soup = BeautifulSoup(form_html, "html.parser")
        text_inputs = soup.find_all("input", {"type": "text"})
        email_inputs = soup.find_all("input", {"type": "email"})
        number_inputs = soup.find_all("input", {"type": "number"})

        for input in text_inputs:
            path = shared_driver.generate_xpath(input)
            element = shared_driver.get_correct_elem(xpath, input)
            shared_driver.filter(element)
            if "required" not in str(input):
                continue
            element.send_keys("testing")

        for input in email_inputs:
            path = shared_driver.generate_xpath(input)
            element = shared_driver.get_correct_elem(xpath, input)
            if "required" not in str(input):
                continue
            element.send_keys("testing@gmail.com")

        for input in number_inputs:
            path = shared_driver.generate_xpath(input)
            element = shared_driver.get_correct_elem(xpath, input)
            if "required" not in str(input):
                continue
            element.send_keys("1231111111")



    1

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
