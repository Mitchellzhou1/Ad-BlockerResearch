from PSAL_base_code import *
from selenium.webdriver.common.keys import Keys

sites = [
    'https://www.hidraulicart.pt/',
    'https://www.rosaperez.pt/en/',
    'https://marijuanaretailreport.com/',
    'http://www.bidtheatre.com/',           # blocked by Ublock
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

output_dict = {}

shared_driver.initialize()
shared_driver.html_obj = "input"


def check_opened(url, tag, local_dom, entire_dom, element):
    if url != shared_driver.driver.current_url:
        return "True - url Change"

    if local_dom != shared_driver.get_local_DOM(element):
        return "True - local DOM Change"

    if entire_dom != shared_driver.driver.page_source:
        return "True - Entire DOM Change"

    if tag != shared_driver.count_tags():
        return "True - tag count change"

    return "False"






for url in sites:
    shared_driver.load_site(url)
    shared_driver.get_elements()
    output_dict[url] = []
    for form_html, refresh in shared_driver.chosen_elms:
        shared_driver.load_site(url)
        input_flag = False
        #####  Collect data for checking if it worked
        initial_dom = shared_driver.driver.page_source
        initial_url = shared_driver.driver.current_url
        initial_local_dom = ''
        initial_tag_count = shared_driver.count_tags()
        final_element = None
        #####

        xpath = shared_driver.generate_xpath(form_html)
        form_elem = shared_driver.get_correct_elem(xpath, form_html)

        soup = BeautifulSoup(form_html, "html.parser")
        text_inputs = soup.find_all("input", {"type": "text"})
        email_inputs = soup.find_all("input", {"type": "email"})
        number_inputs = soup.find_all("input", {"type": "number"})

        for input in text_inputs:
            xpath = shared_driver.generate_xpath(input)
            element = shared_driver.get_correct_elem(xpath, input)
            shared_driver.filter(element)

            # Just in case we can't find the submit button
            final_element = element


            try:
                element.click()
                element.send_keys("testing")
                input_flag = True
            except Exception as e:
                print(e)
                continue

        for input in email_inputs:
            xpath = shared_driver.generate_xpath(input)
            element = shared_driver.get_correct_elem(xpath, input)

            # Just in case we can't find the submit button
            final_element = element

            try:
                element.click()
                element.send_keys("testing@gmail.com")
                input_flag = True
            except Exception as e:
                print(e)
                continue

        for input in number_inputs:
            xpath = shared_driver.generate_xpath(input)
            element = shared_driver.get_correct_elem(xpath, input)

            # Just in case we can't find the submit button
            final_element = element

            try:
                element.send_keys("1231111111")
                input_flag = True
            except Exception as e:
                print(e)
                continue

        if input_flag:  # if we inputted data, now we submit it
            submit_elements = soup.find_all(lambda tag: tag.get("type") == "submit")

            if not submit_elements:     # if I cannot find the enter button, just hit enter
                actions = ActionChains(shared_driver.driver)
                actions.send_keys(Keys.RETURN)
                actions.perform()

            for submit in submit_elements:
                xpath = shared_driver.generate_xpath(submit)
                element = shared_driver.get_correct_elem(xpath, submit)
                shared_driver.click_button(element)
                final_element = element

            res = check_opened(initial_url, initial_tag_count, initial_local_dom, initial_dom, final_element)
            output_dict[url].append([initial_url, res, initial_dom])






# Close the browser window
shared_driver.close()
