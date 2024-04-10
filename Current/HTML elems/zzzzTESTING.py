from base_code import *

shared_driver = Driver()

shared_driver.initialize()
shared_driver.load_site("https://www.google.com/")

HTML = """<textarea class="gLFyf" aria-controls="Alh6id" aria-owns="Alh6id" autofocus="" title="Search" value="" jsaction="paste:puy29d;" aria-label="Search" aria-autocomplete="both" aria-expanded="false" aria-haspopup="false" autocapitalize="off" autocomplete="off" autocorrect="off" id="APjFqb" maxlength="2048" name="q" role="combobox" rows="1" spellcheck="false" data-ved="0ahUKEwjC9Z_GqLiFAxV7lIkEHWDoBC4Q39UDCAY"></textarea>"""
xpath = shared_driver.generate_xpath(HTML)
element = shared_driver.get_correct_elem(xpath, HTML)

print(element.get_attribute("outerHTML"))
element.send_keys("test")



while 1:
    1