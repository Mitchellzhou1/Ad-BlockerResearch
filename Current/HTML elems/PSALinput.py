from PSAL_base_code import *
from selenium.webdriver.common.keys import Keys

sites = [
    'https://www.guldborgsund.dk/',
    'https://mikegap.com/',
    'https://marijuanaretailreport.com/',
    'http://www.bidtheatre.com/',
    'https://www.rosaperez.pt/en/',
    'https://www.hidraulicart.pt/',
    'https://juantorreslopez.com/',
    'http://www.werkschoenen-concurrent.nl',
    'https://naver.com',
    'https://www.ehab.com/',
    'https://copyblogger.com/',
    'http://www.portaldasfinancas.gov.pt/',
    # 'https://www.foxnews.com/',
    # 'https://www.instructure.com/',
    # 'https://www.walmart.com/',
    # 'https://www.indeed.com/',
    # 'https://www.paypal.com/us/home',
    # 'https://www.accuweather.com/',
    # 'https://www.pinterest.com/',
    # 'https://www.bbc.com/',
    # 'https://www.homedepot.com/',
    # 'https://www.breitbart.com/',
    # 'https://github.com/'
]

shared_driver = Driver()


shared_driver.initialize()

driver = shared_driver.driver

driver.get('https://www.bing.com/')

# Find the form box element by its ID or XPath
form_box = driver.find_element_by_id("sb_form")  # Replace "form-box-id" with the actual ID of the form box

# Clear any existing text in the form box (optional)
form_box.clear()

# Type text into the form box
form_box.send_keys("Hello, world!")

# Submit the form or perform any other actions as needed
# For example, you can submit the form by pressing Enter
form_box.send_keys(Keys.RETURN)

# Close the browser window
driver.quit()
