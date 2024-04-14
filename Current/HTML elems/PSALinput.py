from PSAL_base_code import *
from selenium.webdriver.common.keys import Keys

sites = [
    'https://www.ehab.com/',
    # 'https://naver.com',
    # 'https://www.ehab.com/',
    # 'https://www.hidraulicart.pt/',
    # 'https://www.rosaperez.pt/en/',
    # 'https://marijuanaretailreport.com/',
    # 'http://www.bidtheatre.com/',           # blocked by Ublock
    # 'https://juantorreslopez.com/',
    # 'http://www.werkschoenen-concurrent.nl',
    # 'https://copyblogger.com/',
    # 'http://www.portaldasfinancas.gov.pt/',
    # 'https://www.guldborgsund.dk/',
    # 'https://mikegap.com/',
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

    try:
        if local_dom != shared_driver.get_local_DOM(element):
            return "True - local DOM Change"
    except Exception:
        return "True - Stale Element"

    if entire_dom != shared_driver.driver.page_source:
        return "True - Entire DOM Change"

    if tag != shared_driver.count_tags():
        return "True - tag count change"

    return "False"


def find_and_submit_forms(url, form_html):
    if form_html not in shared_driver.driver.page_source:
        return

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
    text_inputs += soup.find_all("input", {"type": "search"})
    text_inputs += soup.find_all("input", {"type": "password"})
    text_inputs += soup.find_all('textarea')

    email_inputs = soup.find_all("input", {"type": "email"})

    number_inputs = soup.find_all("input", {"type": "tel"})

    input_flag, final_element = enter_form(text_inputs, "test", final_element, input_flag)
    input_flag, final_element = enter_form(email_inputs, "test@gmail.com", final_element, input_flag)
    input_flag, final_element = enter_form(number_inputs, "1112223333", final_element, input_flag)

    if input_flag:  # if we inputted data, now we submit it:
        final_element, submit_flag = submit_form(form_elem, final_element)

        if submit_flag:
            res = check_opened(initial_url, initial_tag_count, initial_local_dom, initial_dom, final_element)
            output_dict[url].append([initial_url, res, form_html])
            shared_driver.load_site(url)
        else:
            output_dict[url].append([initial_url, "N/A - Error", form_html])


def enter_form(input_boxes, msg, final_element, input_flag):
    for input in input_boxes:
        xpath = shared_driver.generate_xpath(input)
        element = shared_driver.get_correct_elem(xpath, input)
        shared_driver.filter(element)

        # Just in case we can't find the submit button
        final_element = element

        try:
            shared_driver.click_button(element)
        except Exception as e:
            # this is not that important ... just needs to send the inputs
            error_flag = True       # still not sure what do if this fails.. not that important

        try:
            element.send_keys(msg)
            input_flag = True
        except Exception as e:
            error = str(e).split("\n")[0]
            print(error, element.get_attribute("outerHTML"))
            continue

    return input_flag, final_element


def submit_form(form_elem, final_element):
    html = shared_driver.get_local_DOM(form_elem, 2)
    soup = BeautifulSoup(html, "html.parser")
    submit_elements = soup.find_all(lambda tag: tag.get("type") == "submit")
    submitted = False
    if not submit_elements:  # if I cannot find the enter button, just hit enter
        actions = ActionChains(shared_driver.driver)
        actions.send_keys(Keys.RETURN)
        actions.perform()
        submitted = True

    for submit in submit_elements:
        xpath = shared_driver.generate_xpath(submit)
        element = shared_driver.get_correct_elem(xpath, submit)
        try:
            shared_driver.click_button(element)
            submitted = True
        except Exception as e:
            try:
                # if I cannot find the enter button, just hit enter
                actions = ActionChains(shared_driver.driver)
                actions.send_keys(Keys.RETURN)
                actions.perform()
                submitted = True
            except Exception as e:
                error = str(e).split("\n")[0]
                print(error, element.get_attribute("outerHTML"))
        final_element = element
    return final_element, submitted





def main():
    for url in sites:
        shared_driver.load_site(url)
        shared_driver.load_site(url)
        shared_driver.get_elements()
        output_dict[url] = []
        for form_html, refresh in shared_driver.chosen_elms:
            find_and_submit_forms(url, form_html)

        with open("short_test_input.json", 'w') as json_file:
            json.dump(output_dict, json_file, indent=4)

    print("DONE")

    shared_driver.close()



####################
# Working Code
####################

def works():

    for url in sites:
        shared_driver.load_site(url)
        shared_driver.get_elements()
        output_dict[url] = []
        for form_html, refresh in shared_driver.chosen_elms:

            if form_html not in shared_driver.driver.page_source:
                continue

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
            text_inputs += soup.find_all('textarea')

            email_inputs = soup.find_all("input", {"type": "email"})

            number_inputs = soup.find_all("input", {"type": "tel"})

            for input in text_inputs:
                xpath = shared_driver.generate_xpath(input)
                element = shared_driver.get_correct_elem(xpath, input)
                shared_driver.filter(element)

                # Just in case we can't find the submit button
                final_element = element

                try:
                    shared_driver.click_button(element)
                except Exception as e:
                    # this is not that important ... just needs to send the inputs
                    error_flag = True

                try:
                    element.send_keys("testing")
                    input_flag = True
                except Exception as e:
                    error = str(e).split("\n")[0]
                    print(error, element.get_attribute("outerHTML"))
                    continue

            for input in email_inputs:
                xpath = shared_driver.generate_xpath(input)
                element = shared_driver.get_correct_elem(xpath, input)

                # Just in case we can't find the submit button
                final_element = element

                try:
                    shared_driver.click_button(element)
                except Exception as e:
                    # this is not that important ... just needs to send the inputs
                    error_flag = True

                try:
                    element.send_keys("testing@gmail.com")
                    input_flag = True
                except Exception as e:
                    error = str(e).split("\n")[0]
                    print(error, element.get_attribute("outerHTML"))
                    continue

            for input in number_inputs:
                xpath = shared_driver.generate_xpath(input)
                element = shared_driver.get_correct_elem(xpath, input)

                # Just in case we can't find the submit button
                final_element = element

                try:
                    shared_driver.click_button(element)
                except Exception as e:
                    # this is not that important ... just needs to send the inputs
                    error_flag = True

                try:
                    element.send_keys("111111111")
                    input_flag = True
                except Exception as e:
                    error = str(e).split("\n")[0]
                    print(error, element.get_attribute("outerHTML"))
                    continue

            if input_flag:  # if we inputted data, now we submit it
                html = shared_driver.get_local_DOM(form_elem, 2)
                soup = BeautifulSoup(html, "html.parser")
                submit_elements = soup.find_all(lambda tag: tag.get("type") == "submit")

                if not submit_elements:     # if I cannot find the enter button, just hit enter
                    actions = ActionChains(shared_driver.driver)
                    actions.send_keys(Keys.RETURN)
                    actions.perform()

                for submit in submit_elements:
                    xpath = shared_driver.generate_xpath(submit)
                    element = shared_driver.get_correct_elem(xpath, submit)
                    try:
                        shared_driver.click_button(element)
                    except Exception as e:
                        error = str(e).split("\n")[0]
                        print(error, element.get_attribute("outerHTML"))
                    final_element = element

                res = check_opened(initial_url, initial_tag_count, initial_local_dom, initial_dom, final_element)
                output_dict[url].append([initial_url, res, form_html])
                shared_driver.load_site(url)

    with open("short_test_input.json", 'w') as json_file:
        json.dump(output_dict, json_file, indent=4)

    print("DONE")

    shared_driver.close()

main()