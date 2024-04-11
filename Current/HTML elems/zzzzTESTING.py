from base_code import *

shared_driver = Driver()

shared_driver.initialize()
shared_driver.load_site("https://www.hidraulicart.pt/")

HTML = """<input autocomplete="off" type="text" size="10" class="gsc-input" name="search" title="pesquisar" aria-label="pesquisar" id="gsc-i-id1" dir="ltr" spellcheck="false" style="width: 100%; padding: 0px; border: none; margin: 0px; height: auto; background: url(&quot;https://www.google.com/cse/static/images/1x/pt_PT/branding.png&quot;) left center no-repeat rgb(255, 255, 255); outline: none;">"""
xpath = shared_driver.generate_xpath(HTML)
element = shared_driver.get_correct_elem(xpath, HTML)

print(element.get_attribute("outerHTML"))
element.send_keys("test")



while 1:
    1