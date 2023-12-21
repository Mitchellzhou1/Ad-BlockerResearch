from base_code import *
import time
from Excel import *

attributes = [
    'button',
    'submit'
]

xpaths = [
    '@role'
]


shared_driver.attributes = attributes
shared_driver.xpaths = xpaths

site = 'https://www.imdb.com/'
shared_driver.initialize('uBlock')
shared_driver.load_site(site)

xpath = '//button[@title="Close"][@role="button"][@tabindex="0"][@aria-label="Close"][@aria-disabled="false"]'
element = shared_driver.driver.find_element(By.XPATH, xpath)
if shared_driver.cursor_change(element):
    print("FOUND")

element.click()
while 1:
    1



print("\n\n")