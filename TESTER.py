from base_code import *
import time
from Excel import *

from selenium.common import ElementClickInterceptedException, ElementNotInteractableException

site = 'https://en.wikipedia.org/wiki/Main_Page'
shared_driver.initialize('uBlock')
shared_driver.driver.get(site)
while 1:
    test = shared_driver.driver.find_elements(By.TAG_NAME, 'button')
    print(len(test))
    shared_driver.driver.get(site)
    time.sleep(10)