# import csv
# from bs4 import BeautifulSoup
#
#
# def parse_html_string(html_string):
#     soup = BeautifulSoup(html_string, 'html.parser')
#     if soup:
#         tag = soup.find()
#         if tag:
#             tag_info = {
#                 'tag_name': tag.name,
#                 'attributes': tag.attrs
#             }
#             return tag_info
#     return None
#
#
# def generate_xpath(parsed_info):
#     if parsed_info:
#         tag_name = parsed_info['tag_name']
#         attributes = parsed_info['attributes']
#
#         xpath = f'//{tag_name}'
#         for attr, value in attributes.items():
#             if attr != 'class':  # Exclude 'class' attribute
#                 if isinstance(value, list):
#                     xpath += f'[@{attr}="{value[0]}"]'
#                 else:
#                     xpath += f'[@{attr}="{value}"]'
#
#         return xpath
#     return None
#
#
# # File path to the CSV file
# file_path = 'buttons.csv'
#
# # Open the CSV file in read mode
# with open(file_path, newline='') as csvfile:
#     csv_reader = csv.reader(csvfile)
#
#     header = next(csv_reader)
#     for row in csv_reader:
#
#         parsed_info = parse_html_string(row[1])
#         xpath = generate_xpath(parsed_info)
#         print(row[1])
#         print(xpath)




from selenium import webdriver
from selenium.webdriver.common.by import By
driver = webdriver.Chrome()  # Or any other WebDriver you're using

# Load the Wikipedia page
driver.get('https://en.wikipedia.org/wiki/Main_Page')

# Find the button by its class name using XPath
button = driver.find_element(By.XPATH, '//button[contains(@class, "cdx-button")][contains(@class, "cdx-search-input__end-button")]')

print(button.get_attribute("outerHTML"))
button.click()

# Remember to close the WebDriver session when done
driver.quit()