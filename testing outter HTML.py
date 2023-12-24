from base_code import *


shared_driver.adBlocker_name = 'uBlock'
shared_driver.html_obj = 'buttons'
HTML_obj = 'buttons'
shared_driver = Driver()
shared_driver.initialize()
shared_driver.load_site("https://en.wikipedia.org/wiki/Main_Page")
string = """
<a data-mw="interface" href="/w/index.php?title=Special:UserLogin&amp;returnto=Main+Page" title="You're encouraged to log in; however, it's not mandatory. [alt-shift-o]" accesskey="o" class=""><span>Log in</span></a>
"""
# xpath = """
# //a[@data-mw='interface'][@href='/w/index.php?title=Special:UserLogin&returnto=Main+Page'][@title='You're encouraged to log in; however, it's not mandatory. [alt-shift-o]'][contains(@accesskey, "o")]
#
# """
xpath = shared_driver.generate_xpath(string)
print(xpath)
elm = shared_driver.get_correct_elem(xpath)
elm.click()
print(xpath)


while 1:
    1
