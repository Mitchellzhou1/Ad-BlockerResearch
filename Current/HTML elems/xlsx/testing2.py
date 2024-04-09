import pandas as pd
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

# Path to your JSON file
# json_file_path = 'buttons_control.json'
# Path to your Excel file
# excel_file_path = 'buttons_control.xlsx'

# Load JSON data
# with open(json_file_path, 'r') as file:
#     data = json.load(file)

extn_lst = [
    # 'manual'
    'control',
     'adblock'
    #'ublock'
    # , 'privacy-badger'
    #     "ghostery",
    #     "adguard"
    ]


def is_slideshow(html):
    html = html.lower()
    possible = ['active', 'aria-pressed="true"', 'aria-selected="true"']
    for attribute in possible:
        if attribute in html:
            return True
    return False


def is_required(html):
    if 'aria-disabled="true"' in html.lower():
        return True
    return False

def is_scrollpage(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Find all <a> tags with href starting with "#"
    scroll_links = soup.find_all('a', href=lambda href: href and href.startswith('#') and len(href) > 1)
    if scroll_links:
        return True

    if 'scrollIntoView'.lower() in html.lower():
        return True
    return False



def is_download_link(html):
    file_extensions = [
        '.aac', '.aif', '.aifc', '.aiff', '.au', '.avi', '.bat', '.bin', '.bmp', '.bz2',
        '.c', '.class', '.com', '.cpp', '.css', '.csv', '.dat', '.dmg', '.doc', '.docx',
        '.dot', '.dotx', '.eps', '.exe', '.flac', '.flv', '.gif', '.gzip', '.h', '.htm',
        '.html', '.ico', '.iso', '.java', '.jpeg', '.jpg', '.js', '.json', '.log', '.m4a',
        '.m4v', '.mid', '.midi', '.mov', '.mp3', '.mp4', '.mpa', '.mpeg', '.mpg', '.odp',
        '.ods', '.odt', '.ogg', '.otf', '.pdf', '.php', '.pl', '.png', '.ppt', '.pptx',
        '.ps', '.psd', '.py', '.qt', '.rar', '.rb', '.rtf', '.s', '.sh', '.svg', '.swf',
        '.tar', '.tar.gz', '.tex', '.tif', '.tiff', '.ttf', '.txt', '.wav', '.webm', '.wma',
        '.wmv', '.woff', '.woff2', '.xls', '.xlsx', '.xml', '.yml', '.zip', '.apk'
    ]
    if any(html.endswith(ext) for ext in file_extensions):
        return True

    # Check if URL contains certain keywords
    if 'download' in html.lower() or 'file' in html.lower():
        return True
    return False

def is_open_application(html):
    potential = ['mailto', 'tel', 'sms']
    for attribute in potential:
        if attribute in html.lower():
            return True
    return False









HTML_TEST = {'buttons', "drop downs", "links", "login"}
HTML_TEST = {'buttons'}

# Your specified headers
headers = ["URL_KEY", "HTML_obj Opened?", "Outer HTML Change", "DOM structure Change", "Initial Outer HTML", "After Click Outer HTML", "Initial DOM Structure", "After Click DOM Structure", "Initial Link", "After Click Link", "Tries"]

# Process the JSON data
for extn in extn_lst:
    # Iterate through each HTML object and its data
    for html_obj in HTML_TEST:
        rows = []

        # Load JSON data
        with open(f"{html_obj}_{extn}.json", 'r') as file:
            data = json.load(file)

        for url_key, inner_data in data.items():
            if inner_data == []:
                continue
            # Append a row for the url_key
            rows.append([url_key] + [None] * (len(headers) - 1))  # URL row

            for unit_data in inner_data:
                # Assuming 'inner_data' is a list with values corresponding to the columns from "HTML_obj Opened?"
                # Adjust the list slicing if your data structure requires

                if url_key == 'http://www.iiyama-ouendan.net':
                    1

                if unit_data[0] == 'False':
                    if is_slideshow(unit_data[3]):
                        unit_data[0] = 'True? - slideshow'
                    elif is_required(unit_data[3]):
                        unit_data[0] = 'True? - input is required'
                    elif is_scrollpage(unit_data[3]):
                        unit_data[0] = 'True? - page was scrolled'
                    elif is_download_link(unit_data[3]):
                        unit_data[0] = 'True? - download link'
                    elif is_open_application(unit_data[3]):
                        unit_data[0] = 'True? - opened application'
                row_data = [None] + unit_data
                rows.append(row_data[:len(headers)])  # Ensure the row has the correct number of columns

        # Create a DataFrame with the collected rows
        df = pd.DataFrame(rows, columns=headers)

        # Save the DataFrame to an Excel file
        df.to_excel(f"{html_obj}_{extn}.xlsx", index=False)

print('Data successfully saved to Excel file.')