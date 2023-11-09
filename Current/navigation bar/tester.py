from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://duckduckgo.com/")  # Replace with your URL

attribute = 'legacy-homepage_legacyButton__oUMB9'  # Class attribute value you want to find

# Creating the XPath based on the class attribute directly
test = f'//*[contains(translate(@class, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{attribute.lower()}")]'

element = driver.find_elements(By.XPATH, test)

if element:
    outer_html = element[0].get_attribute('outerHTML')
    first_line = outer_html.splitlines()[0]
    print(first_line)
else:
    print("NONe")


xpath = f'//*[contains(concat(" ", normalize-space(@class), " "), " {attribute} ")]'
# driver = webdriver.Chrome()
# driver.get("https://duckduckgo.com/")  # Replace with your URL
#
# attribute = 'legacy-homepage_legacyButton__oUMB9'  # Class attribute value you want to find
#
# # Creating the XPath based on the class attribute in a case-insensitive manner
# path = "@class"
# xpath = f'//*[translate({path}, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="{attribute.lower()}"]'
#
# elements = driver.find_elements(By.XPATH, xpath)
#
# outer_html = elements[0].get_attribute('outerHTML')
# first_line = outer_html.splitlines()[0]
# print(first_line)
#
# is not finding the button