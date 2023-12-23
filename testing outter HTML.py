from base_code import *


shared_driver.adBlocker_name = 'uBlock'
shared_driver.html_obj = 'buttons'
HTML_obj = 'buttons'
shared_driver = Driver()
shared_driver.initialize()
shared_driver.load_site("https://www.homedepot.com/")
# string = """
# <div class="swiper-button-next" tabindex="0" role="button" aria-label="Go to slide 6" aria-controls="swiper-wrapper-3106f23a78b1fa434" aria-disabled="false"></div># //button[@type="button"][contains(@class, "c-button-logo")][contains(@class, "all-ms-nav")][@aria-expanded="false"][@data-m='{"cN":"GlobalNav_More_nonnav","id":"nn1c1c9c2m1r1a1","sN":1,"aN":"c1c9c2m1r1a1"}'][@style="overflow-x: visible;"]
# """
# xpath = """
# //button[@type='button'][contains(@class, "c-button-logo")][contains(@class, "all-ms-nav")][@aria-expanded='false'][@data-m='{"cN":"GlobalNav_More_nonnav","id":"nn1c1c9c2m1r1a1","sN":1,"aN":"c1c9c2m1r1a1"}'][@style='overflow-x: visible;']"""
# xpath = shared_driver.generate_xpath(string)
# print(xpath)
# elm = shared_driver.get_correct_elem(xpath)
# elm.click()
# print(xpath)


while 1:
    1

