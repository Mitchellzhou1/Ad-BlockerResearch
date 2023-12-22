from base_code import *

shared_driver = Driver()

string = '<button class="frb-rml-link">                        Maybe later                    </button>'
xpath = shared_driver.generate_xpath(string)
print(xpath)


while 1:
    1