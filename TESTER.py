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
shared_driver.driver.get(site)
while 1:
    test = shared_driver.driver.find_elements(By.TAG_NAME, 'button')
    test2 = shared_driver.driver.find_elements(By.XPATH, "//button")
    # test2 = [anchor for anchor in shared_driver.driver.find_elements(By.TAG_NAME, 'a') if not anchor.get_attribute("href")]
    # test3 = shared_driver.specific_element_finder()
    #print(f" button tag = {len(test)}   anchor tag = {len(test2)}   my_check = {len(test3)}")
    # print("Before filter", len(test) + len(test2) + len(test3))
    # print("source code length", len(shared_driver.driver.page_source))
    # final = test+test2+test3
    # print("After filter", len(shared_driver.filter(final)))

    for elem in test:
        print("clicking on", elem.accessible_name)
        elem.click()
        print()


    print("\n\n")
    shared_driver.driver.get(site)
    time.sleep(15)